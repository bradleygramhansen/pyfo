#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Bradley Gram-Hansen
Time created:  23:07
Date created:  17/01/2018

License: MIT
'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Bradley Gram-Hansen
Time created:  11:08
Date created:  08/12/2017

License: MIT
'''

import math
import time
from itertools import permutations

import numpy as np
import pandas as pd
import torch
import copy
from torch.autograd import Variable
# the state interacts with the interface, where ever that is placed....
from utils import state
from utils.core import VariableCast
from utils.eval_stats import extract_stats
from utils.eval_stats import save_data
from utils.plotting import Plotting as plot

class BHMCSampler(object):
    """
    In general model will be the output of the foppl compiler, it is not entirely obvious yet where this
    will be stored. But for now, we will inherit the model from pyro.models.<model_name>
    """

    def __init__(self, object, chains=0,  scale=None):

        # Note for self:
        ## state is a class that contains a dictionary of the system.
        ## to get log_posterior and log_update call the methods on the
        ## state
        # Note:
        ## Need to deal with a M matrix. Using the identity matrix for now.

        self.model_graph =object.model # i graphical model object
        self._state = state.State(self.model_graph)
        self._chains = chains

        ## Debugging:::
        #####
        print('Debug flug in BHMC sampler is one \n')
        self._state.debug()

        # Parameter keys
        self._disc_keys = self._state._return_disc_list()
        self._cont_keys = self._state._return_cont_list()
        self._cond_keys = self._state._return_cond_list()
        self._if_keys = self._state._return_if_list()
        # True latent variable names
        self._names = self._state.get_original_names()
        # Generate sample sizes
        self._sample_sizes = self._state.get_sample_sizes()

        self.grad_logp = self._state._grad_logp
        self.init_state = self._state.intiate_state() # this is just x0
        # self.n_disc = len(self._disc_keys)
        # self.n_cont = len(self._cont_keys)
        # self.n_params =  self.n_disc + self.n_cont

        self.M = 1 #Assumes the identity matrix and assumes everything is 1d for now.

        self.log_posterior = self._state._log_pdf  # returns a function that is the current state as argument

    def random_momentum(self, branch_trig=False):
        """
        Constructs a momentum dictionary where for the discrete keys we have laplacian momen tum
        and for continous keys we have gaussian
        :return:
        """
        p = {}
        if self._disc_keys is not None:
            for key in self._disc_keys:
                p[key] = self.M * VariableCast(np.random.laplace(size=self._sample_sizes[key])) #in the future add support for multiple dims
        if self._cont_keys is not None:
            for key in self._cont_keys:
                p[key] = VariableCast(self.M * np.random.randn(self._sample_sizes[key]))
        if branch_trig:
            for key in self._if_keys:
                p[key] = self.M * VariableCast(np.random.laplace(size=self._sample_sizes[key]))
            if self._if_keys is not None:
                p[key] = VariableCast(self.M * np.random.randn(self._sample_sizes[key]))
        return p

    def coordInt(self,x,x_embed,p,stepsize,key, unembed=False):
        """
        Performs the coordinate wise update. The permutation is done before the
        variables are executed within the function.

        :param x: Dict of state of positions
        :param p: Dict of state of momentum
        :param stepsize: Float
        :param key: unique parameter String
        :param unembed: type: bool If if statement which is continous, in the models we currently run, it will not
         need to be embedded. # TODO in the future if_keys may be discrete and will need embedding.
         To resolve this issue add another check before calling the coordinate wise integrator, to see if the key exists
         in the self._if_cont_vars or self._if_disc_vars
        :return: Updated x and p indicies
        """

        x_star = copy.copy(x)
        x_star[key] = x_star[key] + stepsize*self.M*torch.sign(p[key]) # Need to change M here again
        x_star_embed = copy.copy(x_star)
        logp_diff = self.log_posterior(x_star, set_leafs=False, partial_unembed=unembed, key=key) - self.log_posterior(x, set_leafs=False, partial_unembed=unembed, key=key)
        # If the discrete parameter is outside of the support, returns -inf and breaks loop and integrator.
        if math.isinf(logp_diff.data[0]):
            return x[key], p[key], logp_diff.data[0]

        cond = torch.gt(self.M*torch.abs(p[key]),-logp_diff)
        if cond.data[0]:
            p[key] = p[key] + torch.sign(p[key])*self.M*logp_diff
            return x_star_embed[key], p[key], 0
        else:
            p[key] = -p[key]
            return x_embed[key],p[key], 0

    def append_keys(self, if_cont=False, if_disc=False):
        if if_cont:
            if self._if_cont_keys is not None:
                if self._cont_keys is not None:
                    self._cont_keys = self._cont_keys.append(self._if_cont_keys)
        if if_disc:
            if self._if_disc_keys is not None:
                if self._disc_keys is not None:
                    temp_disc_keys = self._disc_keys
                    return temp_disc_keys.append(self._if_disc_keys)
        if if_cont is False:
            self._cont_keys = [key for key in self._cont_keys not in self._if_cont_keys]
        if if_disc is False:
            self._disc_keys = [key for key in self._disc_keys not in self._if_disc_keys]

    def branching_integrator(self, x0, p0, stepsize, t):
        """
        Performs the full DHMC update step. It updates the continous parameters using
        the standard integrator and the discrete parameters via the coordinate wie integrator.

        :param x: Type dictionary
        :param p: Type dictionary
        :param stepsize: Type: Variable
        :param t Type: int trajectory number
        :return: x, p the proposed values as dict.
        """

        # number of function evaluations and fupdates for discrete parameters
        n_feval = 0
        n_fupdate = 0

        # performs shallow copy
        x = copy.copy(x0)
        p = copy.copy(p0)

        if t is 0:
            self.append_keys(if_cont=True, if_disc=True)

        # perform first step of leapfrog integrators
        if self._cont_keys is not None:
            logp = self.log_posterior(x, set_leafs=True)
            for key in self._cont_keys:
                p[key] = p[key] + 0.5 * stepsize * self.grad_logp(logp, x[key])


        if self._disc_keys is None and self._if_keys is None:
            for key in self._cont_keys:
                x[key] = x[key] + stepsize * self.M * p[key]  # full step for postions
            logp = self.log_posterior(x, set_leafs=True)
            for key in self._cont_keys:
                p[key] = p[key] + 0.5 * stepsize * self.grad_logp(logp, x[key])
            return x, p, n_feval, n_fupdate, 0

        else:
            permuted_keys_list = []
            if self._disc_keys is not None:
                permuted_keys_list = permuted_keys_list + self._disc_keys
            if self._if_keys is not None:
                permuted_keys_list = permuted_keys_list + self._if_keys
            permuted_keys = permutations(permuted_keys_list, 1)
            # permutates all keys into one permutated config. It deletes in memory as each key is called
            # returns a tuple ('key', []), hence to call 'key' requires [0] index.

            if self._cont_keys is not None:
                for key in self._cont_keys:
                    x[key] = x[key] + 0.5 * stepsize * self.M * p[key]
            x_embed = copy.copy(x)
            for key in permuted_keys:
                # print('Debug statement in dhmc.gauss_leapfrog() \n'
                #       'print the permuted_key : {0} \n'
                #       'and key[0]: {1}'.format(key, key[0]))
                if self._if_keys is not None and key[0] in self._if_keys:
                    x[key[0]], p[key[0]], _ = self.coordInt(x, x_embed, p, stepsize, key[0], unembed=False)
                else:
                    x[key[0]], p[key[0]], _ = self.coordInt(x, x_embed, p, stepsize, key[0], unembed=True)
                if math.isinf(_):
                    return x0, p, n_feval, n_fupdate, _
            n_fupdate += 1

            if self._cont_keys is not None:
                for key in self._cont_keys:
                    x[key] = x[key] + 0.5 * stepsize * self.M * p[key]  # final half step for position

            if self._cont_keys is not None:
                logp = self.log_posterior(x, set_leafs=True)
                for key in self._cont_keys:
                    p[key] = p[key] + 0.5 * stepsize * self.grad_logp(logp, x[key])  # final half step for momentum
                n_feval += 1
            return x, p, n_feval, n_fupdate, 0

    def _energy(self, x, p):
        """
        Calculates the hamiltonian for calculating the acceptance ration (detailed balance)
        :param x:
        :param p:
        :return: Tensor
        """
        if self._disc_keys is not None:
            kinetic_disc = torch.sum(torch.stack([self.M * torch.abs(p[name]) for name in self._disc_keys]))
        else:
            kinetic_disc = VariableCast(0)
        if self._cont_keys is not None:
            kinetic_cont = 0.5 * torch.sum(torch.stack([self.M*p[name]**2 for name in self._cont_keys]))
        else:
            kinetic_cont = VariableCast(0)
        if self._if_keys is not None:
            kinetic_if =  torch.sum(torch.stack([self.M * torch.abs(p[name]) for name in self._if_keys]))
        else:
            kinetic_if = VariableCast(0)
        kinetic_energy = kinetic_cont + kinetic_disc + kinetic_if
        potential_energy = -self.log_posterior(x)

        return self._state._return_tensor(kinetic_energy) + self._state._return_tensor(potential_energy)

    def hmc(self, stepsize, n_step, x0):
        """

        :param stepsize_range: List
        :param n_step_range: List
        :param x0:
        :param logp0: probably won't require as will be handled by state self.log_posterior
        :param grad0: probably won't require as will be handled by state self._grad_log
        :param aux0:
        :return:
        """

        p = self.random_momentum()
        intial_energy = self._energy(x0,p)
        n_feval = 0
        n_fupdate = 0
        x = copy.copy(x0)
        for i in range(n_step):
            x,p, n_feval_local, n_fupdate_local, _ = self.branching_integrator(x,p,stepsize,t=i)
            if math.isinf(_):
                break
            n_feval += n_feval_local
            n_fupdate += n_fupdate_local


        final_energy = self._energy(x,p)
        acceptprob  = torch.min(torch.ones(1),torch.exp(final_energy - intial_energy)) # Tensor
        if acceptprob[0] < np.random.uniform(0,1):
            x = x0

        return x, acceptprob[0], n_feval, n_fupdate
    def sample(self,n_samples= 1000, burn_in= 1000, stepsize_range= [0.05,0.20], n_step_range=[5,20],seed=None, n_update=10, lag=20, print_stats=False , plot=False, plot_graphmodel=False, save_samples=False, plot_burnin=False, plot_ac=False):
        # Note currently not doing anything with burn in

        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
        else:
            print('seed deactivated')
        x = self.init_state
        n_per_update = math.ceil((n_samples + burn_in)/n_update)
        n_feval = 0
        n_fupdate = 0
        x_dicts = []
        accept =[]

        tic = time.process_time()
        print(50*'=')
        print('The sampler is now performing inference....')
        print(50*'=')
        for i in range(n_samples+burn_in):
            stepsize = VariableCast(np.random.uniform(stepsize_range[0], stepsize_range[1])) #  may need to transforms to variables.
            n_step = np.ceil(np.random.uniform(n_step_range[0], n_step_range[1])).astype(int)
            x, accept_prob, n_feval_local, n_fupdate_local = self.hmc(stepsize,n_step,x)
            # TODO I should apply an unembed function here too!
            n_feval += n_feval_local
            n_fupdate += n_fupdate_local
            accept.append(accept_prob)
            x_numpy = self._state._unembed(copy.copy(x)) # There should be a quicker way to do this at the very end,
            #  using the whole dataframe series. It will require processing a whole byte vector
            x_dicts.append(self._state.convert_dict_vars_to_numpy(x_numpy))
            if (i + 1) % n_per_update == 0:
                print('{:d} iterations have been completed.'.format(i + 1))
        toc = time.process_time()
        time_elapsed = toc - tic
        n_feval_per_itr = n_feval / (n_samples + burn_in)
        n_fupdate_per_itr = n_fupdate / (n_samples + burn_in)
        if self._disc_keys is not None and self._if_keys is not None:
            print('Each iteration of DHMC on average required '
                + '{:.2f} conditional density evaluations per discontinuous parameter '.format(n_fupdate_per_itr / (len(self._disc_keys)+ len(self._if_keys)))
                + 'and {:.2f} full density evaluations.'.format(n_feval_per_itr))
        if self._disc_keys is None and self._if_keys is not None:
            print('Each iteration of DHMC on average required '
                + '{:.2f} conditional density evaluations per discontinuous parameter '.format(n_fupdate_per_itr / len(self._if_keys))
                + 'and {:.2f} full density evaluations.'.format(n_feval_per_itr))
        if self._disc_keys is not None and self._if_keys is None:
            print('Each iteration of DHMC on average required '
                + '{:.2f} conditional density evaluations per discontinuous parameter '.format(n_fupdate_per_itr / len(self._disc_keys))
                + 'and {:.2f} full density evaluations.'.format(n_feval_per_itr))

        print(50*'=')
        print('Sampling has now been completed....')
        print(50*'=')
        all_samples = pd.DataFrame.from_dict(x_dicts, orient='columns', dtype=float)
        all_samples = all_samples[self._state.all_vars]
        all_samples.rename(columns=self._names, inplace=True)
        # here, names.values() are the true keys
        samples =  all_samples.loc[burn_in:, :]
        # WORKs REGARDLESS OF type of params (i.e np.arrays, variables, torch.tensors, floats etc) and size. Use samples['param_name'] to extract
        # all the samples for a given parameter
        stats = {'samples':samples, 'samples_wo_burin':all_samples, 'stats':extract_stats(samples, keys=list(self._names.values())), 'stats_wo_burnin': extract_stats(all_samples, keys=list(self._names.values())), 'accept_prob': np.sum(accept[burn_in:])/len(accept), 'number_of_function_evals':n_feval_per_itr, \
                 'time_elapsed':time_elapsed, 'param_names': list(self._names.values())}
        if print_stats:
            print(stats['stats'])
            print('The acceptance ratio is: {0}'.format(stats['accept_prob']))
        if save_samples:
            save_data(stats['samples'], stats['samples_wo_burin'], stats['param_names'])
        if plot:
            self.create_plots(stats['samples'], stats['samples_wo_burin'], keys=stats['param_names'],lag=lag, burn_in=plot_burnin, ac=plot_ac)
        if plot_graphmodel:
            self.model_graph.display_graph()
        return stats

    def create_plots(self, dataframe_samples,dataframe_samples_woburin, keys, lag, all_on_one=True, save_data=False, burn_in=False, ac=False):
        """

        :param keys:
        :param ac: bool
        :return: Generates plots
        """

        plot_object = plot(dataframe_samples=dataframe_samples,dataframe_samples_woburin=dataframe_samples_woburin, keys=keys,lag=lag, burn_in=burn_in )
        plot_object.plot_density(all_on_one)
        plot_object.plot_trace(all_on_one)
        if ac:
            plot_object.auto_corr()



