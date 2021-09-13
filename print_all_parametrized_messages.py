import re
from collections import Counter, UserString
from sys import argv

import polib

import toml
import yaml
from rich.console import Console
from rich.pretty import Pretty
from rich.table import Table
from rich.text import Text

django_clone_path = argv[2]
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
singulars = [
    ('user', user),
    ('group', group),
    ('permission', permission),
    ('session', session),
    ('site', site),
    ('redirect', redirect),
    ('flat page', flatpage),
    ('log entry', logentry),
    ('content type', contenttype),
]
plurals = [
    ('users', users),
    ('groups', groups),
    ('permissions', permissions),
    ('sessions', sessions),
    ('sites', sites),
    ('redirects', redirects),
    ('flat pages', flatpages),
    ('log entries', logentries),
    ('content types', contenttypes),
]
c: Counter = Counter()

console = Console()


def n_to_category(n):
    if n == 1:
        return 'one'
    if 1 < n % 10 < 5 and (10 > n % 100 or n % 100 > 20):
        return 'few'
    return 'many'


def parse(rule: str, python_brace_format: bool, **translated_parameters) -> str:
    prepared_parameters = {}
    for param, value in translated_parameters.items():
        if isinstance(value, tuple):
            for_brace_param = UserString(value[1])
            for_brace_param.accusative = rules.get(f'{value[0]}.accusative', value[1])
            for_brace_param.genitive = rules.get(f'{value[0]}.genitive', value[1])
            prepared_parameters |= {
                param: for_brace_param,
                f'{param}.accusative': rules.get(f'{value[0]}.accusative', value[1]),
                f'{param}.genitive': rules.get(f'{value[0]}.genitive', value[1]),
            }
        else:
            prepared_parameters |= {param: value}
    if rule:
        if isinstance(rule, str):
            if not python_brace_format:
                return rule % prepared_parameters
            return rule.format(**prepared_parameters)
        for element in rule:
            if match := re.match('gender:(.*)', element):
                flection_param = match.group(1)
                key = translated_parameters[flection_param][0]
                gendered = rule[element].get(rules.get(f'{key}.gender', 'other'), rule[element].get('other'))
                if type(gendered) == str:
                    if not python_brace_format:
                        return gendered % prepared_parameters
                    return gendered.format(**prepared_parameters)
                else:
                    return parse(gendered, python_brace_format, **translated_parameters)
            if match := re.match('plurals:(.*)', element):
                flection_param = match.group(1)
                category = n_to_category(translated_parameters[flection_param])
                pluralized = rule[element][category]
                if type(pluralized) == str:
                    if not python_brace_format:
                        return pluralized % prepared_parameters
                    return pluralized.format(**prepared_parameters)
                else:
                    return parse(pluralized, python_brace_format, **translated_parameters)
    return ''


for package, domain in (
    tuple(
        (
            (package, 'django')
            for package in (
                'contrib/admin',
                # 'contrib/admindocs',
                # 'contrib/auth',
                # 'contrib/contenttypes',
                # 'contrib/flatpages',
                # 'contrib/gis',
                # 'contrib/humanize',
                # 'contrib/postgres',
                # 'contrib/redirects',
                # 'contrib/sessions',
                # 'contrib/sites',
                # 'conf',
            )
        )
    )
    # + (('contrib/admin', 'djangojs'),)
):
    pofile = polib.pofile(f'{django_clone_path}/django/{package}/locale/{language}/LC_MESSAGES/{domain}.po')
    pofile_en = polib.pofile(f'{django_clone_path}/django/{package}/locale/en/LC_MESSAGES/{domain}.po')

    table = Table(show_lines=True, title=package)
    table.add_column('current translation with examples')
    table.add_column('enhanced translation')
    table.add_column('enhanced examples')
    for entry, entry_en in zip(pofile, pofile_en):
        python_brace_format = 'python-brace-format' in entry.flags
        if match_groups := re.findall(r'%(\(([a-z_]+)\))?s|{([a-z_]*)}', entry.msgid):
            param_names = [match[1] or match[2] for match in match_groups]
            c.update(param_names)
            examples = []
            shouldbeexamples = []
            rule = rules.get(entry.msgid)
            if param_names[0] == 'verbose_name_plural':
                placeables = plurals
                for key, translation in placeables:
                    examples.append(entry.msgstr % {'verbose_name_plural': translation})
                for key, translation in placeables:
                    shouldbeexamples.append(parse(rule, python_brace_format, verbose_name_plural=(key, translation)))
            if param_names[0] == 'verbose_name':
                placeables = singulars
                for key, translation in placeables:
                    examples.append(entry.msgstr % {'verbose_name': translation})
                for key, translation in placeables:
                    shouldbeexamples.append(parse(rule, python_brace_format, verbose_name=(key, translation)))
            if param_names[0] == 'items':
                placeables = []
                for singular, plural in zip(singulars, plurals):
                    placeables.append({'count': 1, 'items': singular})
                    placeables.append({'count': 2, 'items': plural})
                    placeables.append({'count': 5, 'items': plural})
                for placeable in placeables:
                    examples.append(entry.msgstr % {'count': placeable['count'], 'items': placeable['items'][1]})
                for placeable in placeables:
                    shouldbeexamples.append(
                        parse(rule, python_brace_format, count=placeable['count'], items=placeable['items'])
                    )
            if param_names == ['name']:
                placeables = []
                for singular in singulars:
                    placeables.append({'name': singular, 'obj': 'maciek', 'key': 1})
                for plural in plurals:
                    placeables.append({'name': plural, 'obj': 'maciek', 'key': 1})
                for placeable in placeables:
                    # if 'python-format' in entry.flags:
                    examples.append(
                        entry.msgstr % {'obj': placeable['obj'], 'name': placeable['name'][1], 'key': placeable['key']}
                    )
                    # elif 'python-brace-format' in entry.flags:
                for placeable in placeables:
                    shouldbeexamples.append(parse(rule, python_brace_format, **placeable))
            if param_names == ['name', 'object']:
                placeables = [{'name': singular, 'object': 'maciek'} for singular in singulars]
                for placeable in placeables:
                    examples.append(entry.msgstr.format(name=placeable['name'][1], object=placeable['object']))
                for placeable in placeables:
                    shouldbeexamples.append(parse(rule, python_brace_format, **placeable))
            if param_names == ['fields', 'name', 'object']:
                placeables = [{'name': singular, 'fields': 'username', 'object': 'maciek'} for singular in singulars]
                for placeable in placeables:
                    examples.append(
                        entry.msgstr.format(
                            name=placeable['name'][1], fields=placeable['fields'], object=placeable['object']
                        )
                    )
                for placeable in placeables:
                    shouldbeexamples.append(parse(rule, python_brace_format, **placeable))
            if param_names == ['name', 'obj']:
                placeables = [{'name': singular, 'obj': 'maciek'} for singular in singulars]
                for placeable in placeables:
                    if python_brace_format:
                        examples.append(entry.msgstr.format(name=placeable['name'][1], obj=placeable['obj']))
                    else:
                        examples.append(entry.msgstr % {'name': placeable['name'][1], 'obj': placeable['obj']})
                for placeable in placeables:
                    shouldbeexamples.append(parse(rule, python_brace_format, **placeable))
            if param_names == ['name', 'obj', 'name']:
                placeables = [{'name': singular, 'obj': 'maciek'} for singular in singulars]
                for placeable in placeables:
                    examples.append(entry.msgstr.format(name=placeable['name'][1], obj=placeable['obj']))
                for placeable in placeables:
                    shouldbeexamples.append(parse(rule, python_brace_format, **placeable))
            if param_names == ['name', 'key']:
                placeables = [{'name': singular, 'key': 'maciek'} for singular in singulars]
                for placeable in placeables:
                    if python_brace_format:
                        examples.append(entry.msgstr.format(name=placeable['name'][1], key=placeable['key']))
                    else:
                        examples.append(entry.msgstr % {'name': placeable['name'][1], 'key': placeable['key']})
                for placeable in placeables:
                    shouldbeexamples.append(parse(rule, python_brace_format, **placeable))
            if param_names == ['']:
                placeables = [{'': singular} for singular in singulars]
                for placeable in placeables:
                    if python_brace_format:
                        examples.append(entry.msgstr.format(placeable[''][1]))
                    else:
                        examples.append(entry.msgstr % (placeable[''][1],))
                for placeable in placeables:
                    shouldbeexamples.append(parse(rule, python_brace_format, **placeable))
            if param_names == ['count', 'name']:
                placeables = []
                for singular, plural in zip(singulars, plurals):
                    placeables.append({'count': 1, 'name': singular})
                    placeables.append({'count': 2, 'name': plural})
                    placeables.append({'count': 5, 'name': plural})
                for placeable in placeables:
                    examples.append(entry.msgstr % {'count': placeable['count'], 'name': placeable['name'][1]})
                for placeable in placeables:
                    shouldbeexamples.append(
                        parse(rule, python_brace_format, count=placeable['count'], name=placeable['name'])
                    )
            shouldbeoutput = ''
            if not rule:
                shouldbeoutput += 'no need to enhance or not parametrized with models verbose name'
            if shouldbeexamples:
                shouldbeoutput = '\n'.join(shouldbeexamples)
            current = Text()
            current.append('\n'.join(f'{path}:{line}' for path, line in entry_en.occurrences) + '\n')
            current.append(entry.msgid + '\n', "bold")
            current.append(entry.msgstr + '\n', "bold")
            current.append('\n'.join(examples))
            table.add_row(current, yaml.dump(rule, allow_unicode=True), shouldbeoutput)
    console.print(table)

console.print('names of placeholders with count of their occurrence:', str(c))
