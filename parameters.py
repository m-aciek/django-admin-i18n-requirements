from dataclasses import dataclass
from typing import Union

from polib import POEntry

from django_resources import DjangoResources


@dataclass(frozen=True)
class ParametersSet:
    name: str
    parameters: list[Union[int, POEntry]]


@dataclass(frozen=True)
class DjangoMessagesParameters:
    django_resources: DjangoResources

    def model_verbose_name(self):
        auth = self.django_resources.django_pofile('contrib/auth')
        return ParametersSet("model_verbose_name", [auth.find('user'), auth.find('group')])

    def model_verbose_name_plural(self):
        auth = self.django_resources.django_pofile('contrib/auth')
        return ParametersSet("model_verbose_name_plural", [auth.find('users'), auth.find('groups')])

    def model_ngettext(self):
        return (
            [(1, model) for model in self.model_verbose_name().parameters]
            + [(2, models) for models in self.model_verbose_name_plural().parameters]
            + [(5, models) for models in self.model_verbose_name_plural().parameters]
        )

    def parameters_mapping(self):
        return {
            'Select %s': [{'': value} for value in self.model_verbose_name().parameters],
            'Select %s to change': [{'': value} for value in self.model_verbose_name().parameters],
            'Select %s to view': [{'': value} for value in self.model_verbose_name().parameters],
            'Add %(name)s': [{'name': value} for value in self.model_verbose_name().parameters],
            'Delete selected %(verbose_name_plural)s': [
                {'verbose_name_plural': value} for value in self.model_verbose_name_plural().parameters
            ],
            'Successfully deleted %(count)d %(items)s.': [
                {'count': count, 'items': items} for count, items in self.model_ngettext()
            ],
        }
