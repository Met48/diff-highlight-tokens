import difflib
import re

from .working_with_tokens import get_token_text


def is_token_junk(token):
    # TODO: Optimize a bit, detect \n in regex
    token_text = get_token_text(token)
    if '\n' in token_text:
        return False
    # FIXME: Not language-agnostic
    # TODO: Is this a great idea? Seems to improve JavaScript diffs
    if '(' == token_text or ')' == token_text:
        return True
    # # TODO: Figure out better heuristic for discouraging matching minor syntax
    # if len(token_text) <= 2:
    #     return True
    return re.match(r'^[ \t]*$', token_text)


def diff_tokens(tokens_a, tokens_b):
    """
    Given two lists of tokens, produce two lists of tokens with highlighting tokens added.

    Highlighting tokens are of form ('START_HIGHLIGHT', '') and ('END_HIGHLIGHT', '') and
    will surround any additions or removals in their respective stream (always removals
    in first token list and additions in second token list).

    """
    tokens_a = list(tokens_a)
    tokens_b = list(tokens_b)

    streams = {
        'a': {
            'tokens': [],
            'highlighting': False,
        },
        'b': {
            'tokens': [],
            'highlighting': False,
        },
    }

    def add_tokens(stream, highlight, tokens):
        if stream['highlighting'] != highlight:
            if highlight:
                stream['tokens'].append(('START_HIGHLIGHT', ''))
            else:
                stream['tokens'].append(('END_HIGHLIGHT', ''))
            stream['highlighting'] = highlight
        stream['tokens'].extend(tokens)

    matcher = difflib.SequenceMatcher(is_token_junk, tokens_a, tokens_b)
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'insert':
            add_tokens(streams['b'], True, tokens_b[j1:j2])
        elif op == 'replace':
            add_tokens(streams['a'], True, tokens_a[i1:i2])
            add_tokens(streams['b'], True, tokens_b[j1:j2])
        elif op == 'delete':
            add_tokens(streams['a'], True, tokens_a[i1:i2])
        elif op == 'equal':
            add_tokens(streams['a'], False, tokens_a[i1:i2])
            add_tokens(streams['b'], False, tokens_b[j1:j2])
        else:
            raise RuntimeError('Unknown op: %s' % op)

    # Clear any remaining highlighting
    add_tokens(streams['a'], False, [])
    add_tokens(streams['b'], False, [])

    return streams['a']['tokens'], streams['b']['tokens']
