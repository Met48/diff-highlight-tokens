from diff_highlighter.constants import (
    FORMAT_ADD,
    FORMAT_INVERT,
    FORMAT_REMOVE,
    FORMAT_RESET,
    FORMAT_RESET_INVERT,
)
from diff_highlighter.main import main


def check(input_lines, expected_lines):
    input_lines = [
        line.format(
            add=FORMAT_ADD,
            remove=FORMAT_REMOVE,
            reset=FORMAT_RESET,
        )
        for line in input_lines
    ]
    expected_lines = [
        line.format(
            add=FORMAT_ADD,
            remove=FORMAT_REMOVE,
            reset=FORMAT_RESET,
            diff=FORMAT_INVERT,
            nodiff=FORMAT_RESET_INVERT,
        )
        for line in expected_lines
    ]
    actual_lines = list(main(input_lines))

    # Assert that the output (with highlighting) is as expected
    assert actual_lines == expected_lines


def test_dont_modify():
    check([
        ' basic\n',
    ], [
        ' basic\n',
    ])
    check([
        '--- myfiles.js\n',
        '+++ myfile.js\n',
    ], [
        '--- myfiles.js\n',
        '+++ myfile.js\n',
    ])
    check([
        'thisisnotadiff\n',
    ], [
        'thisisnotadiff\n',
    ])


def test_no_format():
    # Lack of format defaults to a word diff.
    # The word diff breaks on changes between letters/quotes/dashes,
    # numbers, spaces, and everything else.

    # Simple check to see that whole word (and space) are highlighted
    check([
        '{remove}-hello world test{reset}\n',
        '{add}+hello test{reset}\n',
    ], [
        '{remove}-hello{diff} world{nodiff} test{reset}\n',
        '{add}+hello test{reset}\n',
    ])

    # Should highlight whole "word" even if some characters are shared
    check([
        '{remove}-one12345six{reset}\n',
        '{add}+one45six{reset}\n',
    ], [
        '{remove}-one{diff}12345{nodiff}six{reset}\n',
        '{add}+one{diff}45{nodiff}six{reset}\n',
    ])


def test_unknown_format():
    # Unknown formats use a word diff
    check([
        '--- a/myfile.unknownextension\n',
        '+++ b/myfile.unknownextension\n',
        '{remove}-basic test for the a wordd diff{reset}\n',
        '{add}+basic text for a word diff{reset}\n',
    ], [
        '--- a/myfile.unknownextension\n',
        '+++ b/myfile.unknownextension\n',
        '{remove}-basic {diff}test{nodiff} for {diff}the {nodiff}a {diff}wordd{nodiff} diff{reset}\n',
        '{add}+basic {diff}text{nodiff} for a {diff}word{nodiff} diff{reset}\n',
    ])

def test_basic_tokenize_js():
    # Check that the diff is using tokens from javascript lexing.
    # Since it's token-based, whole identifier should be highlighted
    # (word diff would just highlight numeric change)
    check([
        '--- a/myfile.js\n',
        '+++ b/myfile.js\n',
        '{remove}-function hello123() {{}}{reset}\n',
        '{add}+function hello12() {{}}{reset}\n',
    ], [
        '--- a/myfile.js\n',
        '+++ b/myfile.js\n',
        '{remove}-function {diff}hello123{nodiff}() {{}}{reset}\n',
        '{add}+function {diff}hello12{nodiff}() {{}}{reset}\n',
    ])


def test_multiple_newlines_js():
    # Trailing
    check([
        '--- a/myfile.js\n',
        '+++ b/myfile.js\n',
        '{remove}-var hello = 5;{reset}\n',
        '{remove}-{reset}\n',
        '{remove}-{reset}\n',
        '{add}+var test = 5;{reset}\n',
        '{add}+{reset}\n',
        '{add}+{reset}\n',
    ], [
        '--- a/myfile.js\n',
        '+++ b/myfile.js\n',
        '{remove}-var {diff}hello{nodiff} = 5;{reset}\n',
        '{remove}-{reset}\n',
        '{remove}-{reset}\n',
        '{add}+var {diff}test{nodiff} = 5;{reset}\n',
        '{add}+{reset}\n',
        '{add}+{reset}\n',
    ])

    # Middle of code
    check([
        '--- a/myfile.js\n',
        '+++ b/myfile.js\n',
        '{remove}-var a = function () {{\n',
        '{remove}-\n',
        '{remove}-\n',
        '{remove}-}};\n',
        '{add}+var a = 5;\n',
    ], [
        '--- a/myfile.js\n',
        '+++ b/myfile.js\n',
        '{remove}-var a = {diff}function () {{{nodiff}{reset}\n',
        '{remove}-{reset}\n',
        '{remove}-{reset}\n',
        '{remove}-{diff}}}{nodiff};{reset}\n',
        '{add}+var a = {diff}5{nodiff};{reset}\n',
    ])


def test_remove_only():
    check([
        '{remove}-hello{reset}\n',
    ], [
        '{remove}-{diff}hello{nodiff}{reset}\n',
    ])


def test_add_only():
    check([
        '{add}+testing{reset}\n',
    ], [
        '{add}+{diff}testing{nodiff}{reset}\n',
    ])


def test_comment_word_diff():
    # Comments use a word diff
    check([
        '--- a/myfile.js\n',
        '+++ a/myfile.js\n',
        '{remove}-// Test wordd diff{reset}\n',
        '{add}+// Test word diff{reset}\n',
    ], [
        '--- a/myfile.js\n',
        '+++ a/myfile.js\n',
        '{remove}-// Test {diff}wordd{nodiff} diff{reset}\n',
        '{add}+// Test {diff}word{nodiff} diff{reset}\n',
    ])


def test_code_differing_number_of_lines():
    check([
        '--- a/myfile.js\n',
        '+++ b/myfile.js\n',
        '{remove}-function constant(x) {{{reset}\n',
        '{remove}-    return x;{reset}\n',
        '{remove}-}}{reset}\n',
        '{add}+function constant(x) {{{reset}\n',
        '{add}+    return function () {{{reset}\n',
        '{add}+        return x;{reset}\n',
        '{add}+    }};{reset}\n',
        '{add}+}}{reset}\n',
    ], [
        '--- a/myfile.js\n',
        '+++ b/myfile.js\n',
        '{remove}-function constant(x) {{{reset}\n',
        '{remove}-    return x;{reset}\n',
        '{remove}-}}{reset}\n',
        '{add}+function constant(x) {{{reset}\n',
        '{add}+    return {diff}function () {{{nodiff}{reset}\n',
        '{add}+{diff}        return {nodiff}x{diff};{nodiff}{reset}\n',
        '{add}+{diff}    }}{nodiff};{reset}\n',
        '{add}+}}{reset}\n',
    ])


def test_trailing_whitespace_into_non_diff():
    check([
        '{remove}-a\n',
        '{add}+b\n',
        ' ',
        ' hello',
    ], [
        '{remove}-{diff}a{nodiff}{reset}\n',
        '{add}+{diff}b{nodiff}{reset}\n',
        ' ',
        ' hello',
    ])


def test_whitespace_continuation():
    check([
        '{remove}-a c\n',
        '{add}+b\n',
        ' \n',
        '{add}+c\n',
    ], [
        '{remove}-{diff}a {nodiff}c{reset}\n',
        '{remove}-{reset}\n',
        '{add}+{diff}b{nodiff}{reset}\n',
        '{add}+{reset}\n',
        '{add}+c{reset}\n',
    ])


def test_rst_word_diff():
    check([
        '--- a/myfile.rst\n',
        '+++ b/myfile.rst\n',
        '{remove}-- a list item\n',
        '{add}+- a listed item\n',
    ], [
        '--- a/myfile.rst\n',
        '+++ b/myfile.rst\n',
        '{remove}-- a {diff}list{nodiff} item{reset}\n',
        '{add}+- a {diff}listed{nodiff} item{reset}\n',
    ])
