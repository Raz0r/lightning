import numpy as np
import scipy.sparse as sp

from numpy.testing import assert_array_equal, assert_array_almost_equal, \
                          assert_almost_equal
from nose.tools import assert_raises, assert_true, assert_equal, \
                       assert_not_equal
from sklearn.utils.testing import assert_greater

from sklearn.datasets.samples_generator import make_classification
from lightning.sgd import SGDClassifier, SGDClassifier


bin_dense, bin_target = make_classification(n_samples=200, n_features=100,
                                            n_informative=5,
                                            n_classes=2, random_state=0)

mult_dense, mult_target = make_classification(n_samples=300, n_features=100,
                                              n_informative=5,
                                              n_classes=3, random_state=0)

def test_binary_linear_sgd():
    for clf in (SGDClassifier(random_state=0, loss="hinge", fit_intercept=True,
                              learning_rate="pegasos"),
                SGDClassifier(random_state=0, loss="hinge", fit_intercept=False,
                              learning_rate="pegasos"),
                SGDClassifier(random_state=0, loss="hinge", fit_intercept=True,
                              learning_rate="invscaling"),
                SGDClassifier(random_state=0, loss="hinge", fit_intercept=True,
                              learning_rate="constant"),
                SGDClassifier(random_state=0, loss="log", fit_intercept=True,
                              learning_rate="constant"),
                SGDClassifier(random_state=0, loss="modified_huber",
                              fit_intercept=True, learning_rate="constant"),
                ):

        clf.fit(bin_dense, bin_target)
        assert_greater(clf.score(bin_dense, bin_target), 0.94)


def test_binary_sgd_equivalence():
    clf = SGDClassifier(kernel="linear",
                              random_state=0)
    clf.fit(bin_dense, bin_target)
    decisions = clf.decision_function(bin_dense)
    predictions = clf.predict(bin_dense)

    clf = SGDClassifier(random_state=0)
    clf.fit(bin_dense, bin_target)
    decisions2 = clf.decision_function(bin_dense)
    predictions2 = clf.predict(bin_dense)

    assert_array_almost_equal(decisions, decisions2)
    assert_array_almost_equal(predictions, predictions2)


def test_binary_kernel_sgd():
    for fit_intercept in (True, False):
        clf = SGDClassifier(kernel="rbf", gamma=0.1,
                                  fit_intercept=fit_intercept,
                                  random_state=0)
        clf.fit(bin_dense, bin_target)
        assert_equal(clf.score(bin_dense, bin_target), 1.0)


def test_multiclass_kernel_sgd():
    for fit_intercept in (True, False):
        clf = SGDClassifier(kernel="rbf", gamma=0.1,
                                  fit_intercept=fit_intercept,
                                  random_state=0)
        clf.fit(mult_dense, mult_target)
        assert_equal(clf.score(mult_dense, mult_target), 1.0)


def test_multiclass_sgd():
    clf = SGDClassifier(random_state=0)
    clf.fit(mult_dense, mult_target)
    assert_greater(clf.score(mult_dense, mult_target), 0.80)


def test_multiclass_sgd_equivalence():
    clf = SGDClassifier(kernel="linear",
                              random_state=0)
    clf.fit(mult_dense, mult_target)
    decisions = clf.decision_function(mult_dense)
    predictions = clf.predict(mult_dense)

    clf = SGDClassifier(random_state=0)
    clf.fit(mult_dense, mult_target)
    decisions2 = clf.decision_function(mult_dense)
    predictions2 = clf.predict(mult_dense)

    assert_array_almost_equal(decisions, decisions2)
    assert_array_almost_equal(predictions, predictions2)


def test_multiclass_hinge_sgd():
    for fit_intercept in (True, False):
        clf = SGDClassifier(loss="hinge", multiclass="natural",
                            fit_intercept=fit_intercept, random_state=0)
        clf.fit(mult_dense, mult_target)
        assert_greater(clf.score(mult_dense, mult_target), 0.78)


def test_multiclass_hinge_kernel_sgd():
    for fit_intercept in (True, False):
        clf = SGDClassifier(kernel="rbf", gamma=0.1,
                                  loss="hinge", multiclass="natural",
                                  fit_intercept=fit_intercept,
                                  random_state=0)
        clf.fit(mult_dense, mult_target)
        assert_greater(clf.score(mult_dense, mult_target), 0.90)


def test_multiclass_natural_kernel_sgd_equivalence():
    for loss in ("hinge", "log"):
        clf = SGDClassifier(kernel="linear",
                                  loss=loss, multiclass="natural",
                                  random_state=0)
        clf.fit(mult_dense, mult_target)
        decisions = clf.decision_function(mult_dense)
        predictions = clf.predict(mult_dense)

        clf = SGDClassifier(random_state=0, loss=loss, multiclass="natural")
        clf.fit(mult_dense, mult_target)
        decisions2 = clf.decision_function(mult_dense)
        predictions2 = clf.predict(mult_dense)

        assert_array_almost_equal(decisions, decisions2)
        assert_array_almost_equal(predictions, predictions2)


def test_multiclass_log_sgd():
    for fit_intercept in (True, False):
        clf = SGDClassifier(loss="log", multiclass="natural",
                            fit_intercept=fit_intercept,
                            random_state=0)
        clf.fit(mult_dense, mult_target)
        assert_greater(clf.score(mult_dense, mult_target), 0.78)


def test_multiclass_log_kernel_sgd():
    for fit_intercept in (True, False):
        clf = SGDClassifier(kernel="rbf", gamma=0.1,
                                  loss="log", multiclass="natural",
                                  fit_intercept=fit_intercept,
                                  random_state=0)
        clf.fit(mult_dense, mult_target)
        assert_equal(clf.score(mult_dense, mult_target), 1.0)


def test_n_components_binary():
    clf = SGDClassifier(kernel="rbf", gamma=0.1, loss="hinge",
                              random_state=0, n_components=50)
    clf.fit(bin_dense, bin_target)
    assert_equal(clf.n_nonzero(), 50)
    assert_greater(clf.score(bin_dense, bin_target), 0.6)


def test_n_components_multiclass():
    clf = SGDClassifier(kernel="rbf", gamma=1.0, loss="hinge",
                              random_state=0, n_components=50)
    clf.fit(mult_dense, mult_target)
    assert_equal(clf.n_nonzero(), 55)
    assert_greater(clf.score(mult_dense, mult_target), 0.3)


def test_n_components_multiclass_natural():
    for loss in ("hinge", "log"):
        clf = SGDClassifier(loss=loss, multiclass="natural",
                                  kernel="rbf", gamma=0.1, n_components=50,
                                  random_state=0)
        clf.fit(mult_dense, mult_target)
        assert_equal(clf.n_nonzero(), 50)
        assert_greater(clf.score(mult_dense, mult_target), 0.38)
