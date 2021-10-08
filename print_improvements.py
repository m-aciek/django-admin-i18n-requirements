from enum import Enum
from itertools import product
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
from parameters import DjangoMessagesParameters, ParametersSet

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
    current.append(translated_entry.msgid + '\n', "bold")
    current.append(translated_entry.msgstr + '\n', "bold")
    current.append('\n'.join(examples))
    return current


def format_examples(examples: list[str]) -> Text:
    return Text('\n'.join(examples))


def render_examples(translated_entry: POEntry, parameters_values: dict[str, ParametersSet]) -> Generator:
    print(parameters_values)
    print(dict([('doo', 'bar')]))
    print(dict([('param', value) for value in list(parameters_values.values())[0].parameters]))
    print([dict([(param, value) for value in values.parameters]) for param, values in parameters_values.items()])
    print(list(parameters_values.items())[0])  # [[(count, 1) (count, 2)], [(items, 1), (items, 2)])
    param, values = list(parameters_values.items())[0]
    print(param, values.parameters)
    print([[(param, value) for value in values.parameters] for param, values in parameters_values.items()])
    print(
        list(
            dict(el)
            for el in list(
                product(
                    *[[(param, value) for value in values.parameters] for param, values in parameters_values.items()]
                )
            )
        )
    )
    for element in list(
        dict(el)
        for el in list(
            product(*[[(param, value) for value in values.parameters] for param, values in parameters_values.items()])
        )
    ):
        new_element = {}
        for key, value in element.items():
            if isinstance(value, POEntry):
                new_element[key] = value.msgstr
            else:
                new_element[key] = value
        if all(map(lambda x: x == '', element.keys())):
            yield translated_entry.msgstr % new_element.values()
        else:
            yield translated_entry.msgstr % new_element
    # for parameter, values in parameters_values.items():
    #     if parameter == '':
    #         for value in values.parameters:
    #             if isinstance(value, POEntry):
    #                 yield translated_entry.msgstr % (value.msgstr,)
    #             else:
    #                 yield translated_entry.msgstr % (value,)
    #     else:
    #         for value in values.parameters:
    #             if isinstance(value, POEntry):
    #                 yield translated_entry.msgstr % {parameter: value.msgstr}
    #             else:
    #                 yield translated_entry.msgstr % {parameter: value}


def render_enhanced_examples(
    translated_entry: Union[dict, str], parameters_values: dict[str, ParametersSet], rules: dict
) -> Generator:
    for element in list(
        dict(el)
        for el in list(
            product(*[[(param, value) for value in values.parameters] for param, values in parameters_values.items()])
        )
    ):
        yield from render_enhanced_example(translated_entry, element, rules)


def render_enhanced_example(
    translated_entry: Union[dict, str], parameters_values: dict[str, Union[str, POEntry]], rules: dict
) -> Generator:
    if isinstance(translated_entry, dict):
        inflection, inflecting_parameter = list(translated_entry.keys())[0].split(':')
        if inflection == "plurals":
            value = parameters_values[inflecting_parameter]
            inflection_category = 'one'
            translation = list(translated_entry.values())[0].get(inflection_category)
            yield from render_enhanced_example(translation, parameters_values, rules)
        else:
            value = parameters_values[inflecting_parameter].msgid
            inflection_category = rules.get(f'{value}.{inflection}')
            translation = list(translated_entry.values())[0].get(inflection_category)
            fallback = list(translated_entry.values())[0].get('other')
            yield from render_enhanced_example(translation or fallback, parameters_values, rules)
    else:
        formattables = {}
        for parameter, value in parameters_values.items():
            if parameter == '':
                formattables |= {
                    '.accusative': rules.get(f'{value.msgid}.accusative'),
                }
            elif isinstance(value, int):
                formattables |= {parameter: value}
            else:
                formattables |= {
                    parameter: value.msgstr,
                    f'{parameter}.accusative': rules.get(f'{value.msgid}.accusative'),
                }
        yield translated_entry % formattables


def print_improvements(django_clone_path: Path, language: str, print: MessageSet = MessageSet.improved) -> None:
    admin_keys = DjangoResources(django_clone_path, 'en').admin_pofile()
    resources = DjangoResources(django_clone_path, language)
    admin = resources.admin_pofile()
    with open(f'{language}.toml') as rules_src:
        improvements = load(rules_src)
    rendered_improvements = []
    for entry in sorted(admin_keys, key=order)[:6]:
        translated_entry = admin.find(entry.msgid)
        if print == MessageSet.improved and entry.msgid not in improvements:
            continue
        parameters = get_parameters(entry.msgid)
        if print == MessageSet.with_parameters and not parameters:
            continue
        parameters_mapping = DjangoMessagesParameters(resources).parameters_mapping()
        parameters_values = {param: parameters_mapping[entry.msgid][param] for param in parameters}
        enhanced_translation = improvements.get(entry.msgid)
        rendered_improvements.append(
            (
                entry,
                translated_entry,
                [example for example in render_examples(translated_entry, parameters_values)],
                enhanced_translation,
                [example for example in render_enhanced_examples(enhanced_translation, parameters_values, improvements)]
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
