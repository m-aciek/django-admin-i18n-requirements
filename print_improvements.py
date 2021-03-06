from collections import UserString
from enum import Enum
from gettext import GNUTranslations, c2py
from pathlib import Path
from re import findall
from typing import Generator, Union

import yaml
from polib import POEntry
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.traceback import install
from toml import load
from typer import run

from django_resources import DjangoResources
from parameters import DjangoMessagesParameters

install(show_locals=True)


class MessageSet(str, Enum):
    all = 'all'
    improved = 'improved'
    with_parameters = 'with-parameters'


def get_parameters(msgid: str) -> list[str]:
    if match_groups := findall(r'%(\(([a-z_]+)\))?[ds]|{([a-z_]*)}', msgid):
        return [match[1] or match[2] for match in match_groups]
    return []


def order(entry: POEntry):
    if 'contrib/admin/views/main.py' in (occurence[0] for occurence in entry.occurrences):
        return POEntry('', occurrences=[])
    if 'contrib/admin/templates/admin/change_list_object_tools.html' in (
        occurence[0] for occurence in entry.occurrences
    ):
        return POEntry('', occurrences=[()])
    return entry


def format_translation_with_examples(entry: POEntry, translated_entry: POEntry, examples: list[str]) -> Text:
    current = Text()
    current.append('\n'.join(f'{path}:{line}' for path, line in entry.occurrences) + '\n')
    current.append(entry.msgid + '\n', "bold")
    if translated_entry:
        current.append(translated_entry.msgstr + '\n', "bold")
    current.append('\n'.join(examples))
    return current


def format_examples(examples: list[str]) -> Text:
    return Text('\n'.join(examples))


def render_examples(translated_entry: POEntry, parameters_values: list[dict[str, Union[int, POEntry]]]) -> Generator:
    if not translated_entry:
        yield ""
        return
    for element in parameters_values:
        new_element: dict[str, Union[int, str]] = {}
        for key, value in element.items():
            if isinstance(value, POEntry):
                new_element[key] = value.msgstr
            else:
                new_element[key] = value
        if 'python-format' in translated_entry.flags:
            if all(map(lambda x: x == '', element.keys())):
                yield translated_entry.msgstr % tuple(new_element.values())
            else:
                yield translated_entry.msgstr % new_element
        elif 'python-brace-format' in translated_entry.flags:
            yield translated_entry.msgstr.format(**new_element)


def render_enhanced_examples(
    translated_entry: Union[dict, str],
    parameters_values: list[dict[str, Union[int, POEntry]]],
    rules: dict,
    plural_forms_string: str,
    format: str,
) -> Generator:
    for element in parameters_values:
        yield from render_enhanced_example(translated_entry, element, rules, plural_forms_string, format)


def render_enhanced_example(
    translated_entry: Union[dict, str],
    parameters_values: dict[str, Union[int, str, POEntry]],
    rules: dict,
    plural_forms_string: str,
    format: str,
) -> Generator:
    if isinstance(translated_entry, dict):
        inflection, inflecting_parameter = list(translated_entry.keys())[0].split(':')
        if inflection == "plurals":
            value = parameters_values[inflecting_parameter]
            inflection_category = plural_category(plural_forms_string, value)
            translation = list(translated_entry.values())[0].get(inflection_category) or list(
                translated_entry.values()
            )[0].get('other')
            yield from render_enhanced_example(translation, parameters_values, rules, plural_forms_string, format)
        else:
            value = parameters_values[inflecting_parameter].msgid
            inflection_category = rules.get(f'{value}.{inflection}')
            translation = list(translated_entry.values())[0].get(inflection_category)
            fallback = list(translated_entry.values())[0].get('other')
            yield from render_enhanced_example(
                translation or fallback, parameters_values, rules, plural_forms_string, format
            )
    else:
        formattables = {}
        for parameter, value in parameters_values.items():
            if format == 'python-format':
                if parameter == '':
                    formattables |= {
                        '.accusative': rules.get(f'{value.msgid}.accusative', value.msgstr),
                        '.genitive': rules.get(f'{value.msgid}.genitive', value.msgstr),
                    }
                elif isinstance(value, POEntry):
                    formattables |= {
                        parameter: value.msgstr,
                        f'{parameter}.accusative': rules.get(f'{value.msgid}.accusative', value.msgstr),
                        f'{parameter}.genitive': rules.get(f'{value.msgid}.genitive', value.msgstr),
                    }
                else:
                    formattables |= {parameter: value}
            else:
                if isinstance(value, POEntry):
                    formattable = UserString(value.msgstr)
                    formattable.accusative = rules.get(f'{value.msgid}.accusative', value.msgstr)
                    formattable.genitive = rules.get(f'{value.msgid}.genitive', value.msgstr)
                    formattables |= {parameter: formattable}
                else:
                    formattables |= {parameter: value}
        if format == 'python-format':
            yield translated_entry % formattables
        else:
            yield translated_entry.format(**formattables)


def plural_category(plural_forms_string: str, value: int) -> str:
    gnu_translations = GNUTranslations()
    gnu_translations._catalog = {
        ("PLURAL-CATEGORY", 0): "one",
        ("PLURAL-CATEGORY", 1): "few",
        ("PLURAL-CATEGORY", 2): "many",
        ("PLURAL-CATEGORY", 3): "other",
    }
    v = plural_forms_string
    v = v.split(';')
    plural = v[1].split('plural=')[1]
    gnu_translations.plural = c2py(plural)
    inflection_category = gnu_translations.ngettext('PLURAL-CATEGORY', 'PLURAL-CATEGORIES', value)
    return inflection_category


def print_improvements(
    django_clone_path: Path, language: str, print: MessageSet = MessageSet.improved, module: str = 'contrib/admin'
) -> None:
    module_keys = DjangoResources(django_clone_path, 'en').django_pofile(module) + [
        POEntry(
            msgid="%(count)d %(name)s",
            msgid_plural="%(count)d %(name_plural)s",
            occurrences=[("contrib/admin/templates/admin/pagination.html", '9')],
            flags=["python-format"],
        )
    ]
    resources = DjangoResources(django_clone_path, language)
    admin = resources.admin_pofile()
    with open(f'{language}.toml') as rules_src:
        improvements = load(rules_src)
    rendered_improvements = []
    plural_forms = admin.metadata['Plural-Forms']
    for entry in sorted(module_keys, key=order):
        translated_entry = admin.find(entry.msgid) or (
            POEntry(
                msgid="%(count)d %(name)s",
                msgid_plural="%(count)d %(name_plural)s",
                msgstr="%(count)d %(name)s",
                msgstr_plural=["%(count)d %(name_plural)s", "%(count)d %(name_plural)s", "%(count)d %(name_plural)s"],
                flags=["python-format"],
            )
            if entry.msgid == "%(count)d %(name)s"
            else None
        )
        if print == MessageSet.improved and entry.msgid not in improvements:
            continue
        with_parameters = 'python-format' in entry.flags or 'python-brace-format' in entry.flags
        parameters = with_parameters and get_parameters(entry.msgid)
        if print == MessageSet.with_parameters and not parameters:
            continue
        parameters_mapping = DjangoMessagesParameters(resources).parameters_mapping()
        parameters_values = parameters_mapping.get(entry.msgid, [])
        enhanced_translation = improvements.get(entry.msgid)
        format = with_parameters and next(filter(lambda x: x in ('python-format', 'python-brace-format'), entry.flags))
        rendered_improvements.append(
            (
                entry,
                translated_entry,
                [example for example in render_examples(translated_entry, parameters_values)],
                enhanced_translation,
                [
                    example
                    for example in render_enhanced_examples(
                        enhanced_translation, parameters_values, improvements, plural_forms, format
                    )
                ]
                if enhanced_translation
                else [],
            )
        )

    table = Table(show_lines=True)
    table.add_column('current translation with examples')
    table.add_column('enhanced translation')
    table.add_column('enhanced examples')
    for entry, translated_entry, examples, enhanced_translation, enhanced_examples in rendered_improvements:
        table.add_row(
            format_translation_with_examples(entry, translated_entry, examples),
            yaml.dump(enhanced_translation, allow_unicode=True) if enhanced_translation else Text(),
            format_examples(enhanced_examples),
        )
    Console().print(table)


if __name__ == '__main__':
    run(print_improvements)
