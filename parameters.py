from dataclasses import dataclass
from functools import lru_cache

from django_resources import DjangoResources


@dataclass(frozen=True)
class DjangoMessagesParameters:
    django_resources: DjangoResources

    @lru_cache
    def model_verbose_name(self):
        auth = self.django_resources.django_pofile('contrib/auth')
        sessions = self.django_resources.django_pofile('contrib/sessions')
        sites = self.django_resources.django_pofile('contrib/sites')
        redirects = self.django_resources.django_pofile('contrib/redirects')
        flatpages = self.django_resources.django_pofile('contrib/flatpages')
        admin = self.django_resources.django_pofile('contrib/admin')
        contenttypes = self.django_resources.django_pofile('contrib/contenttypes')
        return [
            auth.find('user'),
            auth.find('group'),
            auth.find('permission'),
            sessions.find('session'),
            sites.find('site'),
            redirects.find('redirect'),
            flatpages.find('flat page'),
            admin.find('log entry'),
            contenttypes.find('content type'),
        ]

    @lru_cache
    def model_verbose_name_plural(self):
        auth = self.django_resources.django_pofile('contrib/auth')
        sessions = self.django_resources.django_pofile('contrib/sessions')
        sites = self.django_resources.django_pofile('contrib/sites')
        redirects = self.django_resources.django_pofile('contrib/redirects')
        flatpages = self.django_resources.django_pofile('contrib/flatpages')
        admin = self.django_resources.django_pofile('contrib/admin')
        contenttypes = self.django_resources.django_pofile('contrib/contenttypes')
        return [
            auth.find('users'),
            auth.find('groups'),
            auth.find('permissions'),
            sessions.find('sessions'),
            sites.find('sites'),
            redirects.find('redirects'),
            flatpages.find('flat pages'),
            admin.find('log entries'),
            contenttypes.find('content types'),
        ]

    def model_ngettext(self, counts: list[int] = [1, 2, 5]):
        result = []
        for count in counts:
            models = self.model_verbose_name() if count == 1 else self.model_verbose_name_plural()
            for model in models:
                result.append((count, model))
        return result

    def parameters_mapping(self):
        return {
            'Select %s': [{'': value} for value in self.model_verbose_name()],
            'Select %s to change': [{'': value} for value in self.model_verbose_name()],
            'Select %s to view': [{'': value} for value in self.model_verbose_name()],
            'Add %(name)s': [{'name': value} for value in self.model_verbose_name()],
            'Delete selected %(verbose_name_plural)s': [
                {'verbose_name_plural': value} for value in self.model_verbose_name_plural()
            ],
            'Successfully deleted %(count)d %(items)s.': [
                {'count': count, 'items': items} for count, items in self.model_ngettext()
            ],
            'Cannot delete %(name)s': [{'name': name} for name in set(map(lambda x: x[1], self.model_ngettext()))],
            'Add another %(verbose_name)s': [{'verbose_name': value} for value in self.model_verbose_name()],
            'Added {name} “{object}”.': [{'name': name, 'object': 'maciek'} for name in self.model_verbose_name()],
            'Changed {fields} for {name} “{object}”.': [
                {'fields': 'username', 'name': name, 'object': 'maciek'} for name in self.model_verbose_name()
            ],
            'Deleted {name} “{object}”.': [{'name': name, 'object': 'maciek'} for name in self.model_verbose_name()],
            'The {name} “{obj}” was added successfully.': [
                {'name': name, 'obj': 'maciek'} for name in self.model_verbose_name()
            ],
            'The {name} “{obj}” was added successfully. You may add another {name} below.': [
                {'name': name, 'obj': 'maciek'} for name in self.model_verbose_name()
            ],
            'The {name} “{obj}” was changed successfully. You may edit it again below.': [
                {'name': name, 'obj': 'maciek'} for name in self.model_verbose_name()
            ],
            'The {name} “{obj}” was added successfully. You may edit it again below.': [
                {'name': name, 'obj': 'maciek'} for name in self.model_verbose_name()
            ],
            'The {name} “{obj}” was changed successfully. You may add another {name} below.': [
                {'name': name, 'obj': 'maciek'} for name in self.model_verbose_name()
            ],
            'The {name} “{obj}” was changed successfully.': [
                {'name': name, 'obj': 'maciek'} for name in self.model_verbose_name()
            ],
            'The %(name)s “%(obj)s” was deleted successfully.': [
                {'name': name, 'obj': 'maciek'} for name in self.model_verbose_name()
            ],
            '%(name)s with ID “%(key)s” doesn’t exist. Perhaps it was deleted?': [
                {'name': name, 'key': 'maciek'} for name in self.model_verbose_name()
            ],
            'Add %s': [{'': name} for name in self.model_verbose_name()],
            'Change %s': [{'': name} for name in self.model_verbose_name()],
            'View %s': [{'': name} for name in self.model_verbose_name()],
            '%(count)s %(name)s was changed successfully.': [
                {'count': number, 'name': name} for number, name in self.model_ngettext()
            ],
            '%(class_name)s %(instance)s': [
                {'class_name': name, 'instance': 'maciek'} for name in self.model_verbose_name()
            ],
            'Deleting %(class_name)s %(instance)s would require deleting the following protected '
            'related objects: %(related_objects)s': [
                {'class_name': name, 'instance': 'maciek', 'related_objects': 'group admins'}
                for name in self.model_verbose_name()
            ],
            'Select all %(total_count)s %(module_name)s': [
                {'total_count': 2, 'module_name': name_plural} for name_plural in self.model_verbose_name_plural()
            ]
            + [{'total_count': 5, 'module_name': name_plural} for name_plural in self.model_verbose_name_plural()],
            "Deleting the %(object_name)s '%(escaped_object)s' would result in deleting "
            "related objects, but your account doesn't have permission to delete the "
            "following types of objects:": [
                {'object_name': name, 'escaped_object': 'maciek'} for name in self.model_verbose_name()
            ],
            "Deleting the %(object_name)s '%(escaped_object)s' would require deleting the following protected"
            " related objects:": [
                {'object_name': name, 'escaped_object': 'maciek'} for name in self.model_verbose_name()
            ],
            "Are you sure you want to delete the %(object_name)s \"%(escaped_object)s\"? "
            "All of the following related items will be deleted:": [
                {'object_name': name, 'escaped_object': 'maciek'} for name in self.model_verbose_name()
            ],
            "Deleting the selected %(objects_name)s would result in deleting related "
            "objects, but your account doesn't have permission to delete the following "
            "types of objects:": [
                {'objects_name': name, 'count': count} for count, name in self.model_ngettext([1, 2])
            ],
            "Deleting the selected %(objects_name)s would require deleting the following protected related objects:": [
                {'objects_name': name, 'count': count} for count, name in self.model_ngettext([1, 2])
            ],
            "Are you sure you want to delete the selected %(objects_name)s? All of the "
            "following objects and their related items will be deleted:": [
                {'objects_name': name, 'count': count} for count, name in self.model_ngettext([1, 2])
            ],
            "Change selected %(model)s": [{'model': model} for model in self.model_verbose_name()],
        }
