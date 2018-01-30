#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Bradley Gram-Hansen
Time created:  02:07
Date created:  30/01/2018

License: MIT
'''
from pyfo.pyfoppl.foppl import imports
import exp as test
from pyfo.inference.dhmc import DHMCSampler as dhmc

burn_in = 50
n_samples = 50
stepsize_range = [0.05, 0.25]
n_step_range = [10, 20]
# test.model.display_graph()
dhmc_ = dhmc(test)
stats = dhmc_.sample(n_samples=n_samples, burn_in=burn_in, stepsize_range=stepsize_range, n_step_range=n_step_range, seed=123, print_stats=True)
