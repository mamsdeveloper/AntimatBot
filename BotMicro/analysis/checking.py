import re
from typing import Optional

from analysis.normilize import get_normalized_text


def check_regex_inject(text: str) -> bool:
    return re.search(r'[\[\]\(\)\{\}\^\$\*\+\?\|\\]', text) is not None


def check_full_words(text: str, full_words: list[str]) -> Optional[str]:
    for word in full_words:
        if check_regex_inject(word):
            word = re.escape(word)

        # ((?<=[\s,.:;{quotas}])|\A) and (?=[\s,.:;{quotas}]|$) is replacement for \b for utf (\b works only for askii)
        quotas = '\\"' + "\\'"
        result = re.search(rf'((?<=[\s,.:;{quotas}])|\A){word}(?=[\s,.:;{quotas}]|$)', text)
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


def check_text(text: str, full_words: list[str], partial_words: list[str]) -> Optional[str]:
    text = get_normalized_text(text)

    full_match = check_full_words(text, full_words)
    if full_match:
        return full_match

    partial_match = check_partial_words(text, partial_words)
    if partial_match:
        return partial_match[0]

    return None
