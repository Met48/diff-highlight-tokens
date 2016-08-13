import itertools
import operator
import re

import pygments.token

from .constants import (
    FORMAT_INVERT,
    FORMAT_RESET_INVERT,
)


# Token types which are often repeated despite conceptually being one unit
JOIN_TOKENS = set([
    pygments.token.Error,
    pygments.token.Text,
])
# Token types which can be split apart as words
WORD_TOKENS = set([
    pygments.token.Comment,
    pygments.token.Error,
    pygments.token.String,
    pygments.token.Text,
])


get_token_type = operator.itemgetter(0)
get_token_text = operator.itemgetter(1)


WORD_FIND_RE = re.compile(r'([a-zA-Z_-]+|[\d.]+| +|[\s\S])')


def split_words(text):
    """Split a string at every word boundary"""
    return WORD_FIND_RE.findall(text)


def tokenize(text, lexer=None):
    """
    Split text into (token_type, token_text) pairs using the given lexer

    When there is no lexer, it will split by words instead.

    """
    if lexer is None:
        return [(pygments.token.Text, word) for word in split_words(text)]

    tokens = lexer.get_tokens(text)
    tokens = group_tokens(tokens)

    return tokens


def group_tokens(tokens):
    """
    Join and separate tokens to be more suitable for diffs.

    Transformations:
    - Empty tokens are removed
    - Text containing newlines is split to have the newline be one token
    - Other sequential whitespace tokens are joined
    - Token types which contain freeform text (ie. comments, strings) are split into words

    """
    for token_type, group in itertools.groupby(tokens, get_token_type):
        if any(token_type in type_set for type_set in JOIN_TOKENS):
            text = ''.join(get_token_text(token) for token in group)
            group = [(token_type, text)]
        if any(token_type in type_set for type_set in WORD_TOKENS):
            group = (
                (token_type, word)
                for token in group
                for word in split_words(get_token_text(token))
            )
        # Split by newlines
        for token in group:
            text_parts = re.split(r'(\n)', get_token_text(token))
            for text_part in text_parts:
                # Empty tokens are discarded, to avoid confusing
                # difflib or highlighting empty regions
                if text_part:
                    yield (token_type, text_part)


def persist_highlighting(tokens):
    """
    Given a stream of tokens, yield tokens with additional
    START_HIGHLIGHT and END_HIGHLIGHT tokens inserted to persist
    highlighting across tokens with a newline '\n' as text.

    """
    should_be_highlighting = False
    is_highlighting = False
    for token in tokens:
        token_type = get_token_type(token)
        if token_type == 'START_HIGHLIGHT':
            assert not should_be_highlighting, 'Multiple attempts to start highlighting'
            should_be_highlighting = True
        elif token_type == 'END_HIGHLIGHT':
            assert should_be_highlighting, 'Attempt to end highlighting while not highlighting'
            should_be_highlighting = False
        else:
            if get_token_text(token) == '\n':
                if is_highlighting:
                    yield ('END_HIGHLIGHT', '')
                    is_highlighting = False
            elif is_highlighting is not should_be_highlighting:
                if should_be_highlighting:
                    yield ('START_HIGHLIGHT', '')
                else:
                    yield ('END_HIGHLIGHT', '')
                is_highlighting = should_be_highlighting
            yield token


def fill_highlighting_text(tokens, highlight=FORMAT_INVERT, reset=FORMAT_RESET_INVERT):
    """
    Given a stream of tokens, yield tokens where highlighting tokens
    have formatting text

    """
    for token in tokens:
        token_type = get_token_type(token)
        if token_type == 'START_HIGHLIGHT':
            yield ('START_HIGHLIGHT', highlight)
        elif token_type == 'END_HIGHLIGHT':
            yield ('END_HIGHLIGHT', reset)
        else:
            yield token


def convert_to_lines(tokens):
    """
    Given a stream of tokens, yield lines as strings.

    Each output string is guaranteed to end with a newline.

    """
    line = []
    for token in tokens:
        text = get_token_text(token)
        line.append(text)
        if text == '\n':
            yield ''.join(line)
            line = []
    if line:
        line.append('\n')
        yield ''.join(line)


def tokens_to_lines(tokens):
    tokens = persist_highlighting(tokens)
    tokens = fill_highlighting_text(tokens)
    lines = convert_to_lines(tokens)
    return lines
