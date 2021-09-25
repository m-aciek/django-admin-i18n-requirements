from enum import Enum
from pathlib import Path
from re import findall

from polib import pofile, POEntry
from rich.console import Console
from rich.table import Table
from rich.text import Text
from toml import load
from typer import run

from parameters import parameters_mapping


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
        return POEntry('')
    return entry


def format_translation_with_examples(entry: POEntry) -> Text:
    current = Text()
    current.append('\n'.join(f'{path}:{line}' for path, line in entry.occurrences) + '\n')
    current.append(entry.msgid + '\n', "bold")
    current.append(entry.msgstr + '\n', "bold")
    return current


def print_improvements(django_clone_path: Path, language: str, print: MessageSet = MessageSet.improved) -> None:
    admin_keys = admin_pofile(django_clone_path, 'en')
    admin = admin_pofile(django_clone_path, language)
    with open(f'{language}.toml') as rules_src:
        improvements = load(rules_src)
    rendered_improvements = []
    for entry in sorted(admin_keys, key=order)[:4]:
        translated_entry = admin.find(entry.msgid)
        if print == MessageSet.improved and entry.msgid not in improvements:
            continue
        parameters = get_parameters(entry.msgid)
        if print == MessageSet.with_parameters and not parameters:
            continue
        enhanced_parameters = [parameters_mapping[entry.msgid][param] for param in parameters]
        rendered_improvements.append(entry)

    table = Table(show_lines=True)
    table.add_column('current translation with examples')
    table.add_column('enhanced translation')
    table.add_column('enhanced examples')
    for improvement in rendered_improvements:
        table.add_row(format_translation_with_examples(improvement))
    Console().print(table)


def admin_pofile(django_clone_path: Path, language: str):
    return pofile(
        str(django_clone_path / 'django' / 'contrib' / 'admin' / 'locale' / language / 'LC_MESSAGES' / 'django.po')
    )


if __name__ == '__main__':
    run(print_improvements)
