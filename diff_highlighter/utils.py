from __future__ import absolute_import

import pygments.lexers
import pygments.util

from .working_with_tokens import (
    group_tokens,
    split_words,
)


def lex_text(text, lexer=None):
    """Split text into (token_type, token_text) pairs using the given lexer"""
    if lexer is None:
        return [(pygments.token.Text, word) for word in split_words(text)]

    tokens = lexer.get_tokens(text)
    tokens = list(group_tokens(tokens))  # TODO: Necessary cast?

    return tokens


def get_lexer_for_files(from_file, to_file, **options):
    if not from_file or not to_file:
        return None
    if from_file.lower() == '/dev/null':
        return None
    if to_file.lower() == '/dev/null':
        return None
    try:
        from_lexer = pygments.lexers.get_lexer_for_filename(from_file, **options)
        to_lexer = pygments.lexers.get_lexer_for_filename(to_file, **options)
        if from_lexer.__class__ != to_lexer.__class__:
            return None
        return from_lexer
    except pygments.util.ClassNotFound:
        return None
