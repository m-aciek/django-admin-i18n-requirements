**Requirements for natural sounding translations in Django.**

This repository intent to gather requirements for natural sounding translations in all languages that Django supports,
with focus on Django admin.

In languages that inflects sentences basing on grammatical gender of nouns or uses nouns inflected in various 
grammatical cases (and more language-specific phenomena to come), current state of Django admin internationalization,
mainly for messages that are parametrized, is not enough – those messages after being rendered often don't sound
correct.

Let's fix it and gather the rules for various languages, that in the near future can help to find the pragmatic solution
for next level of Django admin internationalization.

This repository abstracts the rules for message inflections in isolation to potential future implementation.

**How to contribute?**

Clone Django repository and this repository to your workspace. Run the script:

    % python print_improvements.py [path-to-django-source-code-clone] [your-language-iso-code]

It will print three columns.
