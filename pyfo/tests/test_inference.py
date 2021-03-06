#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Bradley Gram-Hansen
Time created:  14:31
Date created:  15/03/2018

License: MIT
'''

import unittest
import sys
import math
import torch
import time
import numpy as np
from ..inference.dhmc import DHMCSampler as dhmc
from ..pyfoppl.foppl import imports
from ..pyfoppl.foppl import compilers

# Global variables

TEST_MODELS = ['bin', 'cat', 'gamma', 'gauss_1d', 'gmm_1d_a', 'gmm_1d_b','gmm_1d_c', 'hmm', 'if_1d','lr', 'nested_if', 'poisson']

burn_in = 500
n_samples = 500
stepsize_range = [0.05, 0.18]
n_step_range = [10, 20]
seed= 123456

class BinomialOneSuccessTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        class BinomialOneSuccess():

            def __init__(self):
                self.n = 1
                self.p = 0.8
                self.q = 1 - self.p
                self.true_posterior_mean = 0.8
                self.true_posterior_std = np.sqrt(0.16)
                self.model_code = '(let [x1 (sample (binomial  1 [0.8]))]' \
                             'x1)'
                graph, expr = compilers.compile(self.model_code)
                self.model = graph.create_model(result_expr=expr)
                super().__init__()
        self._model = BinomialOneSuccess()
        super().__init__(*args,**kwargs)

    def test_run(self):
        dhmc_ = dhmc(self._model.model)
        stats = dhmc_.sample(chain_num=0, n_samples=n_samples, burn_in=burn_in, stepsize_range=stepsize_range,
                             n_step_range=n_step_range, seed=seed)
        self.samples = stats['samples']
        self.test_mean = np.mean(self.samples)
        self.test_std = np.std(self.samples)
        self.assertAlmostEqual(self._model.true_posterior_mean, self.test_mean, msg='The binomial one trial inferred mean are too different',delta=0.04)
        self.assertAlmostEqual(self._model.true_posterior_std, self.test_std, msg='The binomial one trial inferred std are too different', delta=0.04)

# @unittest.skip('Not working')
# class Categorical1dTestCase(unittest.TestCase):
#     def __init__(self):
#         self.probs = [0.7,0.15,0.15]
#         self.categories = [i for i in range(len(self.probs))]
#         self.true_posterior_mean = np.array(self.probs)
#
#     def testrun(self):
#         from ..pyfoppl.foppl import imports
#         import cat as test
#         dhmc_ = dhmc(test)
#         stats = dhmc_.sample(chain_num=0, n_samples=n_samples, burn_in=burn_in, stepsize_range=stepsize_range,
#                              n_step_range=n_step_range, seed=seed)
#         self.samples = stats['samples']
#         self.test_inferred_categorical = []
#         for i in self.categories:
#             self.test_inferred_categorical.append(self.calc_true(i))
#         self.test_inferred_categorical = np.array(self.test_inferred_categorical)
#         self.assertAlmostEqual(self.test_inferred_categorical, self.probs ,msg='1d categorical inferred probability values are not the same', delta=0.04)
#
#     def calc_true(self, i):
#         samples = self.samples
#         cols = list(samples)
#         for j in range(len(cols)):
#             score = samples[cols[j]] == i
#             sum_of = score.sum()
#             return sum_of / len(samples[cols[j]])
#
#
#
class ConjugateGaussianTestCase(unittest.TestCase):


    def __init__(self):
        self.true_posterior_mean = 5.5
        # self.true_posterior_std =


    def testrun(self):
        from ..pyfoppl.foppl import imports
        import gauss_1d as test
        dhmc_ = dhmc(test)
        stats = dhmc_.sample(chain_num=0, n_samples=n_samples, burn_in=burn_in, stepsize_range=stepsize_range,
                             n_step_range=n_step_range, seed=seed)
        self.samples = stats['samples']
        self.test_mean = np.mean(self.samples)
        self.test_std = np.std(self.samples)
        self.assertAlmostEqual(self.true_posterior_mean, self.test_mean, msg='The Gaussian 1d trial inferred mean are too different',delta=0.04)
        # self.assertAlmostEqual(self.true_posterior_std, self.test_std, msg='The binomial one trial inferred std are too different', delta=0.04)

if __name__ == '__main__':
    tests = []
    tests.append('BinomialOneSuccessTestCase')
    tests.append('Categorical1dTestCase')
    tests.append('ConjugateGaussianTestCase')

    time_start = time.time()
    success = unittest.main(exit=False,verbosity=2)
    print('\nDuration             : {}'.format(time.time() - time_start))
    print('Models run           : {}'.format(' '.join(tests)))
    print('\nInference tests complete')
    sys.exit(0 if success else 1)