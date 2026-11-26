import sexp


def test_parse_and_find():
    tree = sexp.parse('(kicad_pcb (version 20221018) (net 1 "GND") (net 2 "3V3"))')[0]
    nets = sexp.find(tree, "net")
    assert [n[2] for n in nets] == ['"GND"', '"3V3"']


def test_quoted_strings_with_parentheses():
    tree = sexp.parse('(a "x (y) z" (b 1))')[0]
    assert tree[1] == '"x (y) z"'
    assert sexp.find(tree, "b") == [["b", "1"]]
