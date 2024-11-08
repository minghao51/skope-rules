from skrules import Rule, replace_feature_name


def test_rule():
    assert Rule('a <= 10 and a <= 12') == Rule('a <= 10')
    assert Rule('a <= 10 and a <= 12 and a > 3') == Rule('a > 3 and a <= 10')
    assert Rule('a <= 10 and a <= 10 and a > 3') == Rule('a > 3 and a <= 10')
    assert Rule('a <= 10 and a <= 12 and b > 3 and b > 6') == Rule('a <= 10 and b > 6')
    assert len({Rule('a <= 2 and a <= 3'), Rule('a <= 2')}) == 1
    assert len({Rule('a > 2 and a > 3 and b <= 2 and b <= 3'), Rule('a > 3 and b <= 2')}) == 1
    assert len({Rule('a <= 3 and b <= 2'), Rule('b <= 2 and a <= 3')}) == 1


def test_hash_rule():
    assert len({Rule('a <= 2 and a <= 3'), Rule('a <= 2')}) == 1
    assert len({Rule('a <= 4 and a <= 3'), Rule('a <= 2')}) != 1


def test_str_rule():
    rule = 'a <= 10.0 and b > 3.0'
    assert str(Rule(rule)) == rule


def test_equals_rule():
    rule = "a == a"
    assert str(Rule(rule)) == rule
    rule2 = "a == a and a == a"
    assert str(Rule(rule2)) == rule
    rule3 = "a < 3.0 and a == a"
    assert str(Rule(rule3)) == rule3


def test_replace_feature_name():
    rule = "__C__0 <= 3 and __C__1 > 4"
    real_rule = "$b <= 3 and c(4) > 4"
    replace_dict = {
        "__C__0": "$b",
        "__C__1": "c(4)"
    }
    assert replace_feature_name(rule, replace_dict=replace_dict) == real_rule
