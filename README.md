**Requirements for natural sounding translations in Django.**

This repository intents to gather requirements for natural sounding translations in all languages that Django supports,
with focus on Django admin.

In languages that inflects sentences basing on grammatical gender of nouns or uses nouns inflected in various 
grammatical cases (and more language-specific phenomena to come), current state of Django admin internationalization,
mainly for messages that are parametrized, is not enough – those messages after being rendered often don't sound
correct.

Let's help fix it and start by gathering the rules for various languages, that in the near future can help to find the pragmatic solution
for next level of Django admin internationalization.

This repository abstracts the rules for message inflections in isolation to potential future implementation.

Currently supported:
* plurals (rules copied from existing resources),
* placeables' variants: grammatical cases of nouns or potentially other variants,
* messages variants based on placeable's attribute (e.g. gender).

**How to contribute?**

Clone Django repository and this repository to your workspace. Run the script:

    % python print_improvements.py [path-to-django-source-code-clone] [your-language-iso-code] --module [conf|contrib/admin|contrib/…]

It will print three columns. You can edit your language TOML file and see the effect.

**Next steps**

The data gathered here can be a help for enhancement work, that's around [ticket 11688](https://code.djangoproject.com/ticket/11688) and being worked [here](https://github.com/django/django/compare/main...m-aciek:django:ticket-11688) (current challange is changing the template rendering to improve i18n capacity).
