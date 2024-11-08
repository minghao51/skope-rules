"""
Testing for SkopeRules algorithm (skrules.skope_rules).
"""

import numpy as np
import pytest
from sklearn.model_selection import ParameterGrid
from sklearn.datasets import load_iris, make_blobs
from sklearn.metrics import accuracy_score
from sklearn.utils import check_random_state
from skrules import SkopeRules

rng = check_random_state(0)

# load the iris dataset
# and randomly permute it
iris = load_iris()
perm = rng.permutation(iris.target.size)
iris.data = iris.data[perm]
iris.target = iris.target[perm]

def test_skope_rules():
    """Check various parameter settings."""
    X_train = [[-2, -1], [-1, -1], [-1, -2], [1, 1], [1, 2], [2, 1],
               [6, 3], [-4, -7]]
    y_train = [0] * 6 + [1] * 2
    X_test = np.array([[2, 1], [1, 1]])

    grid = ParameterGrid({
        "feature_names": [None, ['a', 'b']],
        "precision_min": [0.],
        "recall_min": [0.],
        "n_estimators": [1],
        "max_samples": [0.5, 4],
        "max_samples_features": [0.5, 2],
        "bootstrap": [True, False],
        "bootstrap_features": [True, False],
        "max_depth": [2],
        "max_features": ["sqrt", 1, 0.1],
        "min_samples_split": [2, 0.1],
        "n_jobs": [-1, 2]})

    for params in grid:
        SkopeRules(random_state=rng, **params).fit(X_train, y_train).predict(X_test)

    # additional parameters:
    SkopeRules(n_estimators=50,
               max_samples=1.,
               recall_min=0.,
               precision_min=0.).fit(X_train, y_train).predict(X_test)


def test_skope_rules_error():
    """Test that it gives proper exception on deficient input."""
    X = iris.data
    y = iris.target
    y = (y != 0)

    # Test max_samples
    with pytest.raises(ValueError):
        SkopeRules(max_samples=-1).fit(X, y)
    
    with pytest.raises(ValueError):
        SkopeRules(max_samples=0.0).fit(X, y)
        
    with pytest.raises(ValueError):
        SkopeRules(max_samples=2.0).fit(X, y)

    # Test warnings
    with pytest.warns(UserWarning, match="max_samples will be set to n_samples for estimation"):
        SkopeRules(max_samples=1000).fit(X, y)

    # explicitly setting max_samples > n_samples should result in a warning.
    @pytest.mark.parametrize("max_samples", [int(2), 'foobar', 1.5])
    def test_skope_rules_max_samples_validation(max_samples, X, y):
        with pytest.raises(ValueError):
            SkopeRules(max_samples=max_samples).fit(X, y)


    def test_skope_rules_max_depth_duplication_validation(X, y):
        with pytest.raises(ValueError):
            SkopeRules(max_depth_duplication=1.5).fit(X, y)


    def test_skope_rules_predict_validation(X, y):
        model = SkopeRules().fit(X, y)
        with pytest.raises(ValueError):
            model.predict(X[:, 1:])


    def test_skope_rules_decision_function_validation(X, y):
        model = SkopeRules().fit(X, y)
        with pytest.raises(ValueError):
            model.decision_function(X[:, 1:])


    def test_skope_rules_rules_vote_validation(X, y):
        model = SkopeRules().fit(X, y)
        with pytest.raises(ValueError):
            model.rules_vote(X[:, 1:])


    def test_skope_rules_score_top_rules_validation(X, y):
        model = SkopeRules().fit(X, y)
        with pytest.raises(ValueError):
            model.score_top_rules(X[:, 1:])


def test_max_samples_attribute():
    X = iris.data
    y = iris.target
    y = (y != 0)

    # Test max_samples as float (proportion)
    clf = SkopeRules(max_samples=0.4).fit(X, y)
    assert clf.max_samples_ == int(0.4 * X.shape[0])

    # Test max_samples as integer (exact value)
    clf = SkopeRules(max_samples=500).fit(X, y)
    with pytest.warns(UserWarning, match=r"max_samples will be set to n_samples for estimation"):
        clf.fit(X, y)
    assert clf.max_samples_ == X.shape[0]

    # Test max_samples as invalid value (set to n_samples)
    clf = SkopeRules(max_samples=1.)
    assert clf.max_samples_ == X.shape[0]

def test_skope_rules_works():
    # toy sample (the last two samples are outliers)
    X = [[-2, -1], [-1, -1], [-1, -2], [1, 1], [1, 2], [2, 1], [6, 3], [4, -7]]
    y = [0] * 6 + [1] * 2
    X_test = [[-2, -1], [-1, -1], [-1, -2], [1, 1], [1, 2], [2, 1],
              [10, 5], [5, -7]]
    # Test LOF
    clf = SkopeRules(random_state=rng, max_samples=1.)
    clf.fit(X, y)
    decision_func = clf.decision_function(X_test)
    rules_vote = clf.rules_vote(X_test)
    score_top_rules = clf.score_top_rules(X_test)
    pred = clf.predict(X_test)
    pred_score_top_rules = clf.predict_top_rules(X_test, 1)
    # assert detect outliers:
    assert np.min(decision_func[-2:]) > np.max(decision_func[:-2])
    assert np.min(rules_vote[-2:]) > np.max(rules_vote[:-2])
    assert np.min(score_top_rules[-2:]) > np.max(score_top_rules[:-2])
    assert np.array_equal(pred, 6 * [0] + 2 * [1])
    assert np.array_equal(pred_score_top_rules, 6 * [0] + 2 * [1])


def test_deduplication_works():
    # toy sample (the last two samples are outliers)
    X = [[-2, -1], [-1, -1], [-1, -2], [1, 1], [1, 2], [2, 1], [6, 3], [4, -7]]
    y = [0] * 6 + [1] * 2
    X_test = [[-2, -1], [-1, -1], [-1, -2], [1, 1], [1, 2], [2, 1],
              [10, 5], [5, -7]]
    # Test LOF
    clf = SkopeRules(random_state=rng, max_samples=1., max_depth_duplication=3)
    clf.fit(X, y)
    decision_func = clf.decision_function(X_test)
    rules_vote = clf.rules_vote(X_test)
    score_top_rules = clf.score_top_rules(X_test)
    pred = clf.predict(X_test)
    pred_score_top_rules = clf.predict_top_rules(X_test, 1)


def test_performances():
    X, y = make_blobs(n_samples=1000, random_state=0, centers=2)

    # make labels imbalanced by remove all but 100 instances from class 1
    indexes = np.ones(X.shape[0]).astype(bool)
    ind = np.array([False] * 100 + list(((y == 1)[100:])))
    indexes[ind] = 0
    X = X[indexes]
    y = y[indexes]
    n_samples, n_features = X.shape

    clf = SkopeRules()
    # fit
    clf.fit(X, y)
    # with lists
    clf.fit(X.tolist(), y.tolist())
    y_pred = clf.predict(X)
    assert y_pred.shape == (n_samples,)
    # training set performance
    assert accuracy_score(y, y_pred) > 0.83

    # decision_function agrees with predict
    decision = -clf.decision_function(X)
    assert decision.shape == (n_samples,)
    dec_pred = (decision.ravel() < 0).astype(int)
    assert np.array_equal(dec_pred, y_pred)


def test_similarity_tree():
    # Test that rules are well splitted
    rules = [("a <= 2 and b > 45 and c <= 3 and a > 4", (1, 1, 0)),
             ("a <= 2 and b > 45 and c <= 3 and a > 4", (1, 1, 0)),
             ("a > 2 and b > 45", (0.5, 0.3, 0)),
             ("a > 2 and b > 40", (0.5, 0.2, 0)),
             ("a <= 2 and b <= 45", (1, 1, 0)),
             ("a > 2 and c <= 3", (1, 1, 0)),
             ("b > 45", (1, 1, 0)),
             ]

    sk = SkopeRules(max_depth_duplication=2)
    rulesets = sk._find_similar_rulesets(rules)
    # Assert some couples of rules are in the same bag
    idx_bags_rules = []
    for idx_rule, r in enumerate(rules):
        idx_bags_for_rule = []
        for idx_bag, bag in enumerate(rulesets):
            if r in bag:
                idx_bags_for_rule.append(idx_bag)
        idx_bags_rules.append(idx_bags_for_rule)

    assert idx_bags_rules[0] == idx_bags_rules[1]
    assert idx_bags_rules[0] != idx_bags_rules[2]
    # Assert the best rules are kept
    final_rules = sk.deduplicate(rules)
    assert rules[0] in final_rules
    assert rules[2] in final_rules
    assert rules[3] not in final_rules


def test_f1_score():
    clf = SkopeRules()
    rule0 = ('a > 0', (0, 0, 0))
    rule1 = ('a > 0', (0.5, 0.5, 0))
    rule2 = ('a > 0', (0.5, 0, 0))

    assert clf.f1_score(rule0) == 0
    assert clf.f1_score(rule1) == 0.5
    assert clf.f1_score(rule2) == 0
