from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

#Список плохих слов
BAD_WORDS = ['редиска', 'оченьплохоеслово', 'ещеплохоеслово']

@register.filter(needs_autoescape=True)
def censor(value, autoescape=True):
    if not isinstance(value, str):
        return value

    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    words = value.split()
    processed_words = []

    for word in words:
        lower_word = word.lower()
        # Проверка всех вариантов слова (с учетом окончаний)
        if any(bad_word in lower_word for bad_word in BAD_WORDS):
            # Замена всех букв кроме первой на '*'
            censored = word[0] + '*' * (len(word) - 1)
            processed_words.append(esc(censored))
        else:
            processed_words.append(esc(word))

    result = ' '.join(processed_words)
    return mark_safe(result)