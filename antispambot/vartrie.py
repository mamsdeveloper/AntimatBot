"""VarTrie package.

Provide prefix trie for words with letters that have variable forms.

Example:
    words = {'apple', 'banana', 'apricot'}
    chars_table = {'a': {'á', '@-'}, 'e': {'e', 'é', 'É'}}
    trie = VarTrie(chars_table, words)

    '@-pplÉ' in trie  # True
    'apple' in trie  # False (because 'a' is not in chars_table)

Inspirations:
    Search for words in different forms is common task in text processing.
    For example, in a chat application, we may want to filter out bad words
    in messages. However, some letters in bad words may be replaced with
    similar-looking letters, such as 'a' with '@' or 'e' with 'é'. In this
    case, we need to search for words in different forms. But if we have
    a large number of words, it may be inefficient to search for each word
    in all its forms. This is where VarTrie comes in handy.

    In one of my projects I process 47k words with about 20 forms each
    with VarTrie in milliseconds.
"""


from collections import defaultdict
from email.policy import default
from typing import DefaultDict, Optional


class Node:
    """Node of VarTrie.

    Consists of a dictionary of children nodes and a boolean value
    indicating whether this node is the end of a word.
    """

    def __init__(self, is_end: bool = False):
        """Initialize Node.

        Args:
            is_end (bool):
                Whether this node is the end of a word. Defaults to False.
        """
        super().__init__()
        self.is_end = is_end
        self.children: DefaultDict[frozenset[str], Node] = defaultdict(Node)

    def __repr__(self) -> str:
        """Return Node string representation as dict.

        Returns:
            str: Node dictionary representation.
        """
        return str(self.children)


class VarTrie:
    """Prefix trie with letters that have variable forms.

    The trie is constructed using a set of words and a characters table,
    which maps each letter to a set of its possible forms.

    Characters table rules:
        If a letter is not in the characters table, it is assumed to have
        only one form, itself.

        If letter in the characters table, but its forms do not include itself,
        it will not be included in the trie.

        For chars_table = {'a': {'á', '@-'}, 'e': {'e', 'é', 'É'}}
        'a' will have three forms, 'á', '@-', but not 'a',
        'b' will have only one form, 'b',
        'e' will have three forms, 'e', 'é', 'É'.

    Example:
        words = {'apple', 'banana', 'apricot'}
        chars_table = {'a': {'á', '@-'}, 'e': {'e', 'é', 'É'}}
        trie = VarTrie(chars_table, words)

        '@-pplÉ' in trie  # True
        'apple' in trie  # False (because 'a' is not in chars_table)
    """

    def __init__(
        self,
        chars_table: dict[str, set[str]],
        words: Optional[set[str]] = None,
    ):
        """Initialize VarTrie from provided characters table and words.

        Args:
            chars_table (dict[str, set[str]]):
                Maps each letter to a set of its possible forms.
            words (set[str]):
                Words to be inserted into the trie.
                Defaults empty trie created.
        """
        self.root = Node()
        self.chars_table = self._froze_chars_table(chars_table)
        if words is not None:
            self.insert_all(words)

    def insert(self, word: str) -> None:
        """Insert word into the trie.

        Args:
            word (str): Word to be inserted.
        """
        node = self.root
        while word:
            char = word[0]
            word = word[1:]
            forms = self._get_char_forms(char)
            node = node.children[forms]

        node.is_end = True

    def insert_all(self, words: set[str]) -> None:
        """Insert all words into the trie.

        Args:
            words (set[str]): Words to be inserted.
        """
        for word in words:
            self.insert(word)

    def search(self, word: str) -> bool:
        """Return whether the word is in the trie.

        Args:
            word (str): Word to be searched.

        Returns:
            bool: Whether the word is in the trie.
        """
        return self._search(self.root, word)

    def search_prefix(self, prefix: str) -> bool:
        """Return whether the prefix is a prefix of a word in the trie.

        Args:
            prefix (str): Prefix to be searched.

        Returns:
            bool: Whether the prefix is a prefix of a word in the trie.
        """
        return self._search_prefix(self.root, prefix)

    @classmethod
    def _froze_chars_table(
        cls,
        chars_table: dict[str, set[str]],
    ) -> dict[str, frozenset[str]]:
        """Return frozenset version of chars_table.

        Args:
            chars_table (dict[str, set[str]]): Characters table.

        Returns:
            dict[str, frozenset[str]]: Frozenset version of chars_table.
        """
        return {char: frozenset(forms) for char, forms in chars_table.items()}

    def _get_char_forms(self, char: str) -> frozenset[str]:
        """Return set of forms of a character.

        If the character is not in the characters table, it is assumed to have
        only one form, itself.

        Args:
            char (str): Character to get forms of.

        Returns:
            set[str]: Set of forms of the character.
        """
        forms = self.chars_table.get(char)
        if forms is None:
            return frozenset((char, ))

        return forms

    def _get_descendants(
        self,
        node: Node,
        word: str,
    ) -> list[tuple[str, Node]]:
        """Return list of descendants of node that match word.

        Find all forms that match word prefix and return their nodes.

        Args:
            node (Node): Node to get descendants of.
            word (str): Word to match descendants against.

        Returns:
            list[tuple[str, Node]]:
                List of descendants of node that match word.
        """
        nodes = []
        for forms, forms_node in node.children.items():
            sorted_forms = sorted(forms, key=len, reverse=True)
            for form in sorted_forms:
                if word.startswith(form):
                    nodes.append((form, forms_node))

        return nodes

    def _search(self, node: Node, word: str) -> bool:
        """Return whether the word is in the trie.

        Args:
            node (Node): Node to search word in.
            word (str): Word to be searched.

        Returns:
            bool: Whether the word is in the trie.
        """
        descendants = self._get_descendants(node, word)
        if not descendants:
            return False

        if any(word == prefix and node.is_end for prefix, node in descendants):
            return True

        return any(
            self._search(node, word.removeprefix(prefix))
            for prefix, node in descendants
        )

    def _search_prefix(self, node: Node, prefix: str) -> bool:
        """Return whether the prefix is a prefix of a word in the trie.

        Args:
            node (Node): Node to search prefix in.
            prefix (str): Prefix to be searched.

        Returns:
            bool: Whether the prefix is a prefix of a word in the trie.
        """
        descendants = self._get_descendants(node, prefix)
        if not descendants:
            return False

        if any(d_prefix == prefix for d_prefix, _ in descendants):
            return True

        return any(
            self._search_prefix(node, prefix.removeprefix(word))
            for word, node in descendants
        )
