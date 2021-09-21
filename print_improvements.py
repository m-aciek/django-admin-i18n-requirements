from enum import Enum
from pathlib import Path

from polib import pofile
from toml import load
from typer import echo, run


class MessageSet(Enum):
    all = 'all'
    improved = 'improved'
    with_parameters = 'with_parameters'


def print_improvements(django_clone_path: Path, language: str, print: MessageSet = MessageSet.improved) -> None:
    admin = pofile(
        str(django_clone_path / 'django' / 'contrib' / 'admin' / 'locale' / 'en' / 'LC_MESSAGES' / 'django.po')
    )
    with open(f'{language}.toml') as rules_src:
        improvements = load(rules_src)
    for entry in admin:
        if print == MessageSet.improved and entry.msgid not in improvements:
            continue
        if print == MessageSet.with_parameters and None:  # and doesn't have parameters
            continue
        echo(entry.msgid)


if __name__ == '__main__':
    run(print_improvements)
