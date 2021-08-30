import re
from collections import Counter

import polib

import toml

django_clone_path = '/Users/maciek/projects/django'
language = 'pl'

with open(f'languages/{language}.toml') as rules_src:
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
    print(package)
    pofile = polib.pofile(f'{django_clone_path}/django/{package}/locale/{language}/LC_MESSAGES/{domain}.po')

    for entry in pofile:
        if groups := re.findall(r'%(\(([a-z_]+)\))?s|{([a-z_]*)}', entry.msgid):
            # print([match[1] or match[2] for match in groups])
            param_names = [match[1] or match[2] for match in groups]
            c.update(param_names)
            # if "name" in param_names:
            print(entry.msgid, entry.flags, entry.msgstr, rules.get(entry.msgid))
print(c)
