from __future__ import absolute_import

import re

from .constants import (
    ESCAPE_RE,
    FORMAT_ADD,
    FORMAT_INVERT,
    FORMAT_REMOVE,
    FORMAT_RESET,
    FORMAT_RESET_INVERT,
)
from .diff import diff_tokens
from .utils import (
    get_lexer_for_files,
    lex_text,
)
from .working_with_tokens import tokens_to_lines


DIFF_FILENAME_RE = re.compile(r'(?:---|\+\+\+)\s*(.+)')


# NOTE: Order of operations here is important, since
# + and - are prefixes of +++ and ---; the longer
# versions must be checked first
UNIFIED_DIFF_OPERATIONS = [
    '---',
    '+++',
    '-',
    '+',
    ' ',
]


def get_operation(line):
    """Get the unified diff operation from diff line."""
    if not line:
        return None
    return next((op for op in UNIFIED_DIFF_OPERATIONS if line.startswith(op)), None)


def get_filename(line):
    """
    Get the filename from the unified diff header line.

    Only compatible with git diffs, which do not have any additional information
    after the filename.

    """
    match = DIFF_FILENAME_RE.match(line)
    return match and match.group(1)


def unified_diff_to_opcodes(input_stream):
    """
    Converts lines from a unified diff into individual diff operations.

    Yields:
    ('DIFF', from_filename, to_filename, from_lines, to_lines)
        `from_lines` and `to_lines` are lists of lines, with escape codes removed
    ('RAW', line)
        `line` will be identical to the input line

    """

    lines = {
        'from': [],
        'to': [],
        'possible': [],
    }
    filenames = {
        'from': None,
        'to': None,
    }

    def pop_accumulators():
        if lines['from'] or lines['to']:
            yield 'DIFF', filenames['from'], filenames['to'], lines['from'], lines['to']
            lines['from'] = []
            lines['to'] = []
        for line in lines['possible']:
            yield 'RAW', ' ' + line
        lines['possible'] = []

    def move_possible():
        lines['from'] += lines['possible']
        lines['to'] += lines['possible']
        lines['possible'] = []

    for line in input_stream:
        line_simple = ESCAPE_RE.sub('', line)
        operation = get_operation(line_simple)

        # Detect reasons to stop collecting lines for the current diff
        needs_to_pop_accumulators = (
            # A non-empty unchanged line
            (operation == ' ' and line_simple[1:].strip()) or
            # A new file
            operation == '+++' or
            operation == '---' or
            # An unrecognized operation
            operation is None
        )

        if needs_to_pop_accumulators:
            for res in pop_accumulators():
                yield res

        if operation == ' ':
            # Empty lines can be used to join multiple seconds of the diff
            if lines['from'] or lines['to']:
                lines['possible'].append(line_simple[1:])
            else:
                yield 'RAW', line
        elif operation == '-':
            move_possible()
            lines['from'].append(line_simple[1:])
        elif operation == '+':
            move_possible()
            lines['to'].append(line_simple[1:])
        elif operation == '---':
            filenames['from'] = get_filename(line_simple)
            yield 'RAW', line
        elif operation == '+++':
            filenames['to'] = get_filename(line_simple)
            yield 'RAW', line
        else:
            yield 'RAW', line

    # Yield any remaining diff
    for res in pop_accumulators():
        yield res


def add_line_formatting(line, escape_start, escape_end=FORMAT_RESET):
    """
    Wraps a line in given text, maintaining newline as last character
    (if applicable).

    """
    line_o, nl, after = line.rpartition('\n')
    assert not after, 'Line must not have any text after the newline %s' % repr(line)
    return escape_start + line_o + escape_end + nl


def main(input_stream):
    for operation in unified_diff_to_opcodes(input_stream):
        opcode = operation[0]
        if opcode == 'RAW':
            yield operation[1]
        elif opcode == 'DIFF':
            from_file, to_file, from_lines, to_lines = operation[1:]
            # Perform token-based diff
            # (falls back on word diff if unable to tokenize)
            if from_lines and to_lines:
                lexer = get_lexer_for_files(from_file, to_file, stripnl=False, ensurenl=False)
                from_lines = ''.join(from_lines)
                to_lines = ''.join(to_lines)
                from_tokens = lex_text(from_lines, lexer)
                to_tokens = lex_text(to_lines, lexer)
                from_tokens, to_tokens = diff_tokens(from_tokens, to_tokens)
                from_lines = tokens_to_lines(from_tokens)
                to_lines = tokens_to_lines(to_tokens)
            else:
                # Highlight whole lines by default
                from_lines = (add_line_formatting(line, FORMAT_INVERT, FORMAT_RESET_INVERT) for line in from_lines)
                to_lines = (add_line_formatting(line, FORMAT_INVERT, FORMAT_RESET_INVERT) for line in to_lines)
            for line in from_lines:
                yield add_line_formatting('-' + line, FORMAT_REMOVE)
            for line in to_lines:
                yield add_line_formatting('+' + line, FORMAT_ADD)
        else:
            raise RuntimeError('Invalid opcode: %s' % opcode)
