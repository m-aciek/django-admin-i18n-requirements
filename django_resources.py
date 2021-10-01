from dataclasses import dataclass
from pathlib import Path

from polib import pofile


@dataclass(frozen=True)
class DjangoResources:
    django_clone_path: Path
    language: str

    def admin_pofile(self):
        return self.django_pofile('contrib/admin')

    def django_pofile(self, module: str):
        return pofile(
            str(self.django_clone_path / 'django' / module / 'locale' / self.language / 'LC_MESSAGES' / 'django.po')
        )
