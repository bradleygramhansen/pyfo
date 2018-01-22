#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Bradley Gram-Hansen
Time created:  14:12
Date created:  22/11/2017

License: MIT
'''
import torch
from torch.autograd import Variable
from collections import deque
import copy
import math
from pyfo.utils.core import VariableCast
from pyfo.utils.unembed import Unembed


"""
Each vertex has the following helper functions:

vertex.is_conditional
vertex.is_continuous
vertex.is_discrete
vertex.is_observed
vertex.is_sampled
vertex.get_all_ancestors

"""
class State(object):
    """
    Stores the state of the object

    """

    def __init__(self, cls):
        """

        :param cls: this is the interface cls of the model.
        """
        ### These functions still exists
        self._state_init = cls.gen_prior_samples()
        self._gen_logpdf = cls.gen_pdf # returns logp
        self._cont_vars = cls.gen_cont_vars() #includes the piecewise variables for now.
        self._disc_vars = cls.gen_disc_vars()
        self._if_vars = cls.gen_if_vars()
        self._cond_vars=  cls.gen_cond_vars()
        self._vertices = cls.get_vertices()
        self._arcs = cls.get_arcs()
        self._disc_dist = cls.get_discrete_distributions()
        self._cont_disc = cls.get_continuous_distributions()
        #####
        # self._discontinuities = cls.gen_discontinuities()
        self._unembed_state = Unembed(self._dist_arg_size)
        # True names of parameters

    def get_support(self, key):
        """
        Returns the support of the parameter

        vetex.support_size
        self._disc_dist
        :param key:
        :return:
        """
    def gen_vars(self):
        """

        :return:
        """
        return [vertex.name for vertex in self._vertices if vertex.is_sampled]
    def get_ancestors(self):
        """
        object.dist_ancestors only direct parents of variable , does not include the predicate.
        object.ancestors includes only direct parents of the ancestor history including predicate itself
        object.get_all_ancestors - includes the entire history of the variable, includes the predicate aswell

        :return:
        """
        ancestors = {}
        for vertex in self._vertices:
            ancestors[self._vertices.name] = vertex.get_all_ancestors

    def get_original_names(self, keys):
        """

        :param keys:
        :return:
        """
        names = {}
        for vertex in self._vertices:
            names[vertex] = vertex.original_name
        self._names = cls.get_original_names()
        # for
        #     for self.

    def intiate_state(self):
        """
        A dictionary of the state.
        :param
        :return: state type: intialized state
        """
        return self._state_init

    def _return_disc_list(self):  #change the return type from None to [], since easier to operate on lists than None with list
        if len(self._disc_vars) == 0:
            return None
        else:
            return self._disc_vars

    def _return_cont_list(self):
        if len(self._cont_vars) == 0:
            return None
        else:
            return self._cont_vars

    def _return_if_list(self):
        if len(self._if_vars) == 0:
            return None
        else:
            return self._if_vars

    def _return_cond_list(self):
        if len(self._cond_vars) == 0:
            return None
        else:
            return self._cond_vars

    # def _return_arcs(self):
    #     if len(self._arcs) == 0:
    #         return None
    #     else:
    #         return self._arcs

    def _return_vertices(self):
        if len(self._vertices) == 0:
            return None
        else:
            return self._vertices

    def _return_all_list(self):
        if len(self._all_vars) == 0:
            return None
        else:
            return self._all_vars

    def _return_true_names(self):
        if len(self._names) == 0:
            return None
        else:
            return self._names

    @staticmethod
    def detach_nodes(x):
        """
        Takes either the momentum or latents
        :param x:
        :return:
        """
        for key, value in x.items():
            x[key] = Variable(value.data, requires_grad=True)

    def _log_pdf(self, state, set_leafs=False, unembed=False, partial_unembed=False, key=None):
        """
        The compiled pytorch function, log_pdf, should automatically
        return the pdf.
        :param keys type: list of discrete embedded discrete parameters
        :return: log_pdf

        Do I need to convert the variables within state, to requires grad = True
        here? Then they will be passed to gen_logpdf to create the differentiable logpdf
        . Answer: yes, because
        """

        if unembed:
            _temp =self._unembed(state)
            if isinstance(_temp, Variable) and math.isinf(_temp.data[0]):
                return _temp
            else:
                state = _temp
        if partial_unembed:
            _temp = self._partial_unembed(state, key)
            if isinstance(_temp, Variable) and math.isinf(_temp.data[0]):
                return _temp
            else:
               state[key] = _temp[key]

        if set_leafs:
            state = self._to_leaf(state)

        return self._gen_logpdf(state)

    def _embed(self, state, disc_key):
        """

        :param state:
        :param disc_key: Discrete parameter being embedded
        :return: embedded state with embedded parameter value

        else

        TO DO
        embedding : π(n)/ (a(n + 1/2) - a(n)) * I(a_{n-1/2} <  where a(n) = n n \mathbb{Z}^{+}
        This embedding essentially just divides by 1. Other embeddings for discrete parameters
         will be implemented later in the pipeline
        """
        embed_state = {}
        for key in disc_key:
            embed_state[key] = copy.copy(state[key])
        return embed_state

    def _partial_unembed(self, state, key):
        """
        Un-embeds only one parameter, to save on computation within the coordinate wise
        integrator.

        :param state:
        :param disc_key:
        :param feature to add later, regarding the support of the discrete param
        :return: state with unembedded value

        If embedded value falls outside of domain of discrete
        parameter return -inf
        simple embedding defined as:

         "Bernoulli", - support x \in {0,1}
        "Categorical", - x \in {0, \dots, k-1} where k \in \mathbb{Z}^{+}
        "Multinomial", - x_{i} \in {0,\dots ,n\}, i \in {0,\dots ,k-1} where sum(x_{i}) =n }
        "Poisson" - x_{i} \in {0,\dots ,+inf}  where x_{i} \in \mathbb{Z}^{+}

        """
        dist_name = 'unembed_' + self._disc_dist[key]
        unembed_var = getattr(self._unembed_state, dist_name)(state, key)
        return unembed_var
    def _unembed(self,state):
        """

        Un-embeds the entire state

        :param state:
        :param disc_key:
        :param feature to add later, regarding the support of the discrete param
        :return: state with unembedded value

        If embedded value falls outside of domain of discrete
        parameter return -inf
        simple embedding defined as:

         "Bernoulli", - support x \in {0,1}
        "Categorical", - x \in {0, \dots, k-1} where k \in \mathbb{Z}^{+}
        "Multinomial", - x_{i} \in {0,\dots ,n\}, i \in {0,\dots ,k-1} where sum(x_{i}) =n }
        "Poisson" - x_{i} \in {0,\dots ,+inf}  where x_{i} \in \mathbb{Z}^{+}

        """
##      TODO will have to append this function to deal with discrete if vars at a later date
        for key in self._disc_vars:
            dist_name = 'unembed_'+self._disc_dist[key]
            state = getattr(self._unembed_state, dist_name)(state, key)
        return state

    def _log_pdf_update(self, state, step_size, log_prev, disc_params,j):
        """
        NOT USED Currently

        Implements the 'f_update' in the coordinate wise integrator, to calculate the
        difference in log probabiities.
        def f_update(x, dx, j, aux):

            logp_prev = aux

            x_new = x.clone()
            x_new.data[j] = x_new.data[j] + dx

            logp, _ , _  = f(x_new, False)
            logp_diff = logp - logp_prev
            aux_new = logp
            return logp_diff, aux_new

        :param state: dictionary of parameters
        :param step_size: torch.autograd.Variable
        :param log_prev: torch.autograd.Variable contains the value of the log_pdf before the change point
        :param disc_params: list of discrete params gen_sen keys
        :param j: permutated index, type int
        :return: log_diff , aux_new (the updated logp)?

        """
        update_parameter = disc_params[j]
        state[update_parameter] = state[update_parameter] + step_size
        current_logp = self._gen_logpdf(state)
        logp_diff = self.current_logpdf - log_prev
        return logp_diff, current_logp

    def _grad_logp(self, logp, param):
        """
        Returns the gradient of the log pdf, with respect for
        each parameter
        :param state:
        :return: torch.autograd.Variable
        """

        gradient_of_param = torch.autograd.grad(outputs=logp, inputs=param, retain_graph=True)[0]
        return gradient_of_param

    def _to_leaf(self, state):
        """
        Ensures that all latent parameters are reset to leaf nodes, before
        calling
        :param state:
        :return:
        """
        for key in state:
            tmp = VariableCast(state[key])
            state[key] = VariableCast(tmp.data, grad=True)
            # state[key] = VariableCast(state[key].data, grad=True)
        return state

    @staticmethod
    def _return_tensor(val1):
        """
        Takes a values, checks to see if it is a variable, if so returns tensor,
        else returns a tensor of the value
        :param val1:
        :return:
        """
        if isinstance(val1, Variable):
            return val1.data
        else:
            return val1

    def _gradient_field(self, key, state):
        """
        For RRHMC

        :param state: dict of all latent variables
        :param key: the value of predicate
        :return: unit grad Vector type: List of Variables
        Tobias has now created a dictionary of the predicates,
        that has for the value a lambda function that returns
        the scalar field .

        To DO: Finish once tobias gets back, as the function is including variables that
        do not exist in the outputted parameter fields. Will need to use ancestor to generate the keys for the history,
        so that we know what to differentiate with respect to
        """
        ancestors = self._ancestors(key) # returns set
        scalar_field = [] #TODO Complete scalar field construction
        grad_vec = []
        for ancestor in ancestors:
            grad_vec.append(torch.autograd.grad(scalar_field, ancestor, retain_graph=True))

        return grad_vec

    @staticmethod
    def convert_dict_vars_to_numpy(state):
        """

        :param state:
        :return:

        Converts variables in stat to numpy arrays for plotting purposes
        """
        for i in state:
            state[i] =  VariableCast(state[i]).data.numpy()
            # state[i] = state[i].data.numpy()
        return state