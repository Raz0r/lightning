# Author: Mathieu Blondel
# License: BSD

import numpy as np

from scipy.sparse.linalg import cg

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelBinarizer
from sklearn.utils import check_random_state
from sklearn.metrics.pairwise import pairwise_kernels

from .base import BaseKernelClassifier

class PrimalNewton(BaseKernelClassifier, ClassifierMixin):

    def __init__(self, lmbda=1.0, max_iter=50, tol=1e-3, preconditioning=True,
                 kernel="linear", gamma=0.1, coef0=1, degree=4,
                 random_state=0, verbose=0, n_jobs=1):
        self.lmbda = lmbda
        self.tol = tol
        self.max_iter = max_iter
        self.preconditioning = preconditioning
        self.kernel = kernel
        self.gamma = gamma
        self.coef0 = coef0
        self.degree = degree
        self.random_state = random_state
        self.verbose = verbose
        self.n_jobs = n_jobs

    def _fit_binary(self, K, y):
        coef = np.zeros(K.shape[0])
        sv = np.ones(K.shape[0], dtype=bool)

        for t in xrange(1, self.max_iter + 1):
            if self.verbose:
                print "Iteration", t, "#SV=", np.sum(sv)

            K_sv = K[sv][:, sv]
            I = np.diag(self.lmbda * np.ones(K_sv.shape[0]))

            if self.preconditioning:
                coef_sv, info = cg(K_sv + I, y[sv], tol=self.tol, M=K_sv)
            else:
                coef_sv, info = cg(K_sv + I, y[sv], tol=self.tol)

            coef *= 0
            coef[sv] = coef_sv
            pred = np.dot(K, coef)
            errors = 1 - y * pred
            last_sv = sv
            sv = errors > 0

            if np.array_equal(last_sv, sv):
                if self.verbose:
                    print "Converged at iteration", t
                break

        return coef

    def fit(self, X, y):
        n_samples, n_features = X.shape
        rs = check_random_state(self.random_state)

        X = np.asfortranarray(X, dtype=np.float64)

        self.label_binarizer_ = LabelBinarizer(neg_label=-1, pos_label=1)
        Y = self.label_binarizer_.fit_transform(y)
        self.classes_ = self.label_binarizer_.classes_.astype(np.int32)
        n_vectors = Y.shape[1]

        K = pairwise_kernels(X, filter_params=True, **self._kernel_params())

        coef = [self._fit_binary(K, Y[:, i]) for i in xrange(n_vectors)]
        self.coef_ = np.array(coef)
        self.intercept_ = np.zeros(n_vectors, dtype=np.float64)

        self._post_process(X)

        return self

