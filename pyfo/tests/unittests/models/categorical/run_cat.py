#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Bradley Gram-Hansen
Time created:  21:34
Date created:  20/01/2018

License: MIT
'''
from ..pyfoppl.foppl import imports
import cat as test

# print(test.model)
# print(test.model.gen_pdf_code)
from ..inference.dhmc import DHMCSampler as dhmc

dhmc_ = dhmc(test)
burn_in = 500
n_sample = 1500
stepsize_range = [0.05,0.1]
n_step_range = [10, 20]

stats = dhmc_.sample(n_samples=n_sample,burn_in=burn_in,stepsize_range=stepsize_range,n_step_range=n_step_range,plot=True, print_stats=True, save_samples=True)

# samples =  stats['samples']
# all_samples = stats['samples_wo_burin'] # type, panda dataframe
# print(stats['accept_prob'])