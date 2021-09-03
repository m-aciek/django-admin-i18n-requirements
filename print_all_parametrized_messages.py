import re
from collections import Counter
from sys import argv

import polib

import toml

django_clone_path = '/Users/maciek/projects/django'
try:
    language = argv[1]
except IndexError:
    language = 'pl'

with open(f'{language}.toml') as rules_src:
    rules = toml.load(rules_src)

c = Counter()
for package, domain in (
    tuple(
        (
            (package, 'django')
            for package in (
                'contrib/admin',
                'contrib/admindocs',
                'contrib/auth',
                'contrib/contenttypes',
                'contrib/flatpages',
                'contrib/gis',
                'contrib/humanize',
                'contrib/postgres',
                'contrib/redirects',
                'contrib/sessions',
                'contrib/sites',
                'conf',
            )
        )
    )
    + (('contrib/admin', 'djangojs'),)
):
    print(f'[package name: {package}]')
    pofile = polib.pofile(f'{django_clone_path}/django/{package}/locale/{language}/LC_MESSAGES/{domain}.po')

    for entry in pofile:
        if groups := re.findall(r'%(\(([a-z_]+)\))?s|{([a-z_]*)}', entry.msgid):
            param_names = [match[1] or match[2] for match in groups]
            c.update(param_names)
            print(
                entry.msgid,
                entry.msgctxt,
                'PLURAL' if entry.msgid_plural else None,
                # entry.flags,
                entry.comment,
                entry.msgstr_plural if entry.msgid_plural else entry.msgstr,
                rules.get(entry.msgid),
            )

print('names of placeholders with count of their occurrence:', c)
