import re
from typing import Optional

from antispambot.analysis.normilize import get_normalized_text


def check_regex_inject(text: str) -> bool:
    return re.search(r'[\[\]\(\)\{\}\^\$\*\+\?\|\\]', text) is not None


def check_full_words(text: str, full_words: list[str]) -> Optional[str]:
    for word in full_words:
        if check_regex_inject(word):
            word = re.escape(word)

        # ((?<=[\s,.:;{quotas}])|\A) and (?=[\s,.:;{quotas}]|$) is replacement for \b for utf (\b works only for askii)
        quotas = '\\"' + "\\'"
        result = re.search(
            rf'((?<=[\s,.:;{quotas}])|\A){word}(?=[\s,.:;{quotas}]|$)', text)
        if result:
            return result.group()

    return None


def check_partial_words(text: str, partial_words: list[str]) -> Optional[tuple[str, str]]:
    for word in partial_words:
        if word in text:
            outer = re.search(fr'\b\w*{word}\w*\b', text)
            if outer:
                return outer.group(), word
            else:
                return '', word

    return None


def check_regexps(text: str, patterns: list[str]) -> Optional[tuple[str, str]]:
    for pattern in patterns:
        result = re.search(pattern, text)
        if result:
            return result.group(), pattern

    return None


def check_text(text: str, full_words: list[str], partial_words: list[str]) -> Optional[str]:
    text = get_normalized_text(text)

    full_match = check_full_words(text, full_words)
    if full_match:
        return full_match

    partial_match = check_partial_words(text, partial_words)
    if partial_match:
        return partial_match[0]

    return None


def check_substitution(text: str) -> Optional[str]:
    """Check Russian symbols replaced with Unicode chars."""
    RU_SYMS = '[а-яА-ЯёЁ]'
    EN_SYMS = r'[a-zA-Z]'
    SUBSTITUTED = rf'({RU_SYMS}{EN_SYMS})|({EN_SYMS}{RU_SYMS})'
    match = re.findall(rf'(\w*({SUBSTITUTED})\w*)', text)
    if match:
        return match[0][0]

    return None


def check_emoji(text: str) -> bool:
    """Check if text is spam consists of custom emojies."""
    if len(text) < 15:
        # it is probable normal text
        return False

    non_emoji = re.findall(r'[\w\d{re.escape(string.punctuation)}]', text)
    if len(non_emoji) < 3:
        return True

    return False
