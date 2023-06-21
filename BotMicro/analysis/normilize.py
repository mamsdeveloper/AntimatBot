import re


analyzer = None


def remove_stop_words(text: str, stop_words: list[str]) -> str:
    for word in stop_words:
        text = text.replace(word.lower(), '')
        text = text.replace(word, '')

    return text


def get_normalized_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r' {2, }', ' ', text)
    text = text.replace('ё', 'е')
    return text


def get_words(text: str) -> set[str]:
    words = re.findall(r'\w+', text)
    return set(words)


def get_obfuscated_words(text: str) -> set[str]:
    words = re.findall(r"\w[-\w'`&%$#@*]+\w", text)
    return set(words)


def get_normalized_words(words: list[str]) -> set[str]:
    from pymorphy2.analyzer import MorphAnalyzer

    global analyzer
    if not analyzer:
        analyzer = MorphAnalyzer()

    normalized_words: set[str] = set()

    for word in words:
        if len(word) < 3:
            continue

        normalized_words.update(analyzer.normal_forms(word))

    return normalized_words
