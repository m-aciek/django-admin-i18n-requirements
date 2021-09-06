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
auth = polib.pofile(f'{django_clone_path}/django/contrib/auth/locale/{language}/LC_MESSAGES/django.po')
user = auth.find('user').msgstr
group = auth.find('group').msgstr
permission = auth.find('permission').msgstr
session = (
    polib.pofile(f'{django_clone_path}/django/contrib/sessions/locale/{language}/LC_MESSAGES/django.po')
    .find('session')
    .msgstr
)
site = (
    polib.pofile(f'{django_clone_path}/django/contrib/sites/locale/{language}/LC_MESSAGES/django.po')
    .find('site')
    .msgstr
)
redirect = (
    polib.pofile(f'{django_clone_path}/django/contrib/redirects/locale/{language}/LC_MESSAGES/django.po')
    .find('redirect')
    .msgstr
)
flatpage = (
    polib.pofile(f'{django_clone_path}/django/contrib/flatpages/locale/{language}/LC_MESSAGES/django.po')
    .find('flat page')
    .msgstr
)
logentry = (
    polib.pofile(f'{django_clone_path}/django/contrib/admin/locale/{language}/LC_MESSAGES/django.po')
    .find('log entry')
    .msgstr
)
contenttype = auth.find('content type').msgstr
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
            examples = []
            for model in (user, group, permission, session, site, redirect, flatpage, logentry, contenttype):
                try:
                    examples.append(entry.msgstr % {param_names[0]: model})
                except KeyError:
                    pass
            print(
                entry.msgid,
                entry.msgctxt,
                'PLURAL' if entry.msgid_plural else None,
                # entry.flags,
                entry.comment,
                entry.msgstr_plural if entry.msgid_plural else entry.msgstr,
                rules.get(entry.msgid),
                examples,
            )

print('names of placeholders with count of their occurrence:', c)
