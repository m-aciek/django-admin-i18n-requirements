from dataclasses import dataclass

from django_resources import DjangoResources


@dataclass(frozen=True)
class DjangoMessagesParameters:
    django_resources: DjangoResources

    def model_verbose_name(self):
        auth = self.django_resources.django_pofile('contrib/auth')
        return [auth.find('user'), auth.find('group')]

    def model_verbose_name_plural(self):
        auth = self.django_resources.django_pofile('contrib/auth')
        return [auth.find('users'), auth.find('groups')]

    def model_ngettext(self):
        return (
            [(1, model) for model in self.model_verbose_name()]
            + [(2, models) for models in self.model_verbose_name_plural()]
            + [(5, models) for models in self.model_verbose_name_plural()]
        )

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
        }
