from dataclasses import dataclass
from typing import Union

from polib import POEntry

from django_resources import DjangoResources


@dataclass(frozen=True)
class ParametersSet:
    name: str
    parameters: list[Union[str, POEntry]]


@dataclass(frozen=True)
class DjangoMessagesParameters:
    django_resources: DjangoResources

    def model_verbose_name(self):
        auth = self.django_resources.django_pofile('contrib/auth')
        return ParametersSet("model_verbose_name", [auth.find('user'), auth.find('group')])

    def model_verbose_name_plural(self):
        auth = self.django_resources.django_pofile('contrib/auth')
        return ParametersSet("model_verbose_name_plural", [auth.find('users'), auth.find('groups')])

    def parameters_mapping(self):
        return {
            'Select %s': {'': self.model_verbose_name()},
            'Select %s to change': {'': self.model_verbose_name()},
            'Select %s to view': {'': self.model_verbose_name()},
            'Add %(name)s': {'name': self.model_verbose_name()},
            'Delete selected %(verbose_name_plural)s': {'verbose_name_plural': self.model_verbose_name_plural()},
            'Successfully deleted %(count)d %(items)s.': {},
        }
