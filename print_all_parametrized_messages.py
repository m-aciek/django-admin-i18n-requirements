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
users = auth.find('users').msgstr
group = auth.find('group').msgstr
groups = auth.find('groups').msgstr
permission = auth.find('permission').msgstr
permissions = auth.find('permissions').msgstr
sessions_file = polib.pofile(f'{django_clone_path}/django/contrib/sessions/locale/{language}/LC_MESSAGES/django.po')
session = sessions_file.find('session').msgstr
sessions = sessions_file.find('sessions').msgstr
sites_file = polib.pofile(f'{django_clone_path}/django/contrib/sites/locale/{language}/LC_MESSAGES/django.po')
site = sites_file.find('site').msgstr
sites = sites_file.find('sites').msgstr
redirects_file = polib.pofile(f'{django_clone_path}/django/contrib/redirects/locale/{language}/LC_MESSAGES/django.po')
redirect = redirects_file.find('redirect').msgstr
redirects = redirects_file.find('redirects').msgstr
flatpages_file = polib.pofile(f'{django_clone_path}/django/contrib/flatpages/locale/{language}/LC_MESSAGES/django.po')
flatpage = flatpages_file.find('flat page').msgstr
flatpages = flatpages_file.find('flat pages').msgstr
admin = polib.pofile(f'{django_clone_path}/django/contrib/admin/locale/{language}/LC_MESSAGES/django.po')
logentry = admin.find('log entry').msgstr
logentries = admin.find('log entries').msgstr
contenttypes_file = polib.pofile(
    f'{django_clone_path}/django/contrib/contenttypes/locale/{language}/LC_MESSAGES/django.po'
)
contenttype = contenttypes_file.find('content type').msgstr
contenttypes = contenttypes_file.find('content types').msgstr
singulars = (user, group, permission, session, site, redirect, flatpage, logentry, contenttype)
plurals = (users, groups, permissions, sessions, sites, redirects, flatpages, logentries, contenttypes)
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
            if param_names[0] == 'verbose_name_plural':
                for model in plurals:
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
