#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: Bradley Gram-Hansen
Time created:  11:27
Date created:  08/03/2018

License: MIT
'''
from collections import OrderedDict

import torch
from torch.distributions import constraints
from torch.distributions import biject_to, constraints

import pyro
import pyro.distributions as dist
import pyro.poutine as poutine
from pyro.infer.mcmc.trace_kernel import TraceKernel
from pyro.ops.integrator import velocity_verlet
from pyro.util import ng_ones, ng_zeros, is_nan, is_inf

class HMC(TraceKernel):
    """
    Simple Hamiltonian Monte Carlo kernel, where ``step_size`` and ``num_steps``
    need to be explicitly specified by the user.

    **Reference**
    "MCMC Using Hamiltonian Dynamics", R Neal. `pdf <https://arxiv.org/pdf/1206.1901.pdf>`_


    :param model: python callable containing pyro primitives.
    :param float step_size: determines the size of a single step taken by the
        verlet integrator while computing the trajectory using Hamiltonian
        dynamics.
    :param int num_steps: The number of discrete steps over which to simulate
        Hamiltonian dynamics. The state at the end of the trajectory is
        returned as the proposal.
    :param dict transforms: Optional dictionary that specifies a transform
        for a sample site with constrained support to unconstrained space. The
        transform should be invertible, and implement `log_abs_det_jacobian`.
        If not specified and the model has sites with constrained support,
        automatic transformations will be applied, as specified in
        :mod:`torch.distributions.constraint_registry`.
    """

    def __init__(self, model, step_size=0.5, num_steps=3, transforms=None):
        self.model = model
        self.step_size = step_size
        self.num_steps = num_steps
        self.transforms = {} if transforms is None else transforms
        self._automatic_transform_enabled = True if transforms is None else False
        self._reset()
        super(HMC, self).__init__()

    def _get_trace(self, z):
        z_trace = self._prototype_trace
        for name, value in z.items():
            z_trace.nodes[name]['value'] = value
        trace_poutine = poutine.trace(poutine.replay(self.model, trace=z_trace))
        trace_poutine(*self._args, **self._kwargs)
        return trace_poutine.trace

    def _kinetic_energy(self, r):
        return 0.5 * torch.sum(torch.stack([r[name]**2 for name in r]))

    def _potential_energy(self, z):
        # Since the model is specified in the constrained space, transform the
        # unconstrained R.V.s `z` to the constrained space.
        z_constrained = z.copy()
        for name, transform in self.transforms.items():
            z_constrained[name] = transform.inv(z_constrained[name])
        trace = self._get_trace(z_constrained)
        potential_energy = -trace.log_pdf()
        # adjust by the jacobian for this transformation.
        for name, transform in self.transforms.items():
            potential_energy += transform.log_abs_det_jacobian(z_constrained[name], z[name]).sum()
        return potential_energy

    def _energy(self, z, r):
        return self._kinetic_energy(r) + self._potential_energy(z)

    def _reset(self):
        self._t = 0
        self._r_dist = OrderedDict()
        self._args = None
        self._kwargs = None
        self._accept_cnt = 0
        self._prototype_trace = None

    def _validate_trace(self, trace):
        trace_log_pdf = trace.log_pdf()
        if is_nan(trace_log_pdf) or is_inf(trace_log_pdf):
            raise ValueError('Model specification incorrect - trace log pdf is NaN, Inf or 0.')

    def initial_trace(self):
        return self._prototype_trace

    def setup(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        # set the trace prototype to inter-convert between trace object
        # and dict object used by the integrator
        self._prototype_trace = poutine.trace(self.model).get_trace(*args, **kwargs)
        # momenta distribution - currently standard normal
        for name, node in sorted(self._prototype_trace.iter_stochastic_nodes(),
                                 key=lambda x: x[0]):
            r_mu = torch.zeros_like(node['value'])
            r_sigma = torch.ones_like(node['value'])
            self._r_dist[name] = dist.Normal(mu=r_mu, sigma=r_sigma)
            if node['fn'].support is not constraints.real and self._automatic_transform_enabled:
                self.transforms[name] = biject_to(node['fn'].support).inv
        self._validate_trace(self._prototype_trace)

    def cleanup(self):
        self._reset()

    def sample(self, trace):
        z = {name: node['value'] for name, node in trace.iter_stochastic_nodes()}
        # automatically transform `z` to unconstrained space, if needed.
        for name, transform in self.transforms.items():
            z[name] = transform(z[name])
        r = {name: pyro.sample('r_{}_t={}'.format(name, self._t), self._r_dist[name])
             for name in self._r_dist}
        z_new, r_new = velocity_verlet(z, r,
                                       self._potential_energy,
                                       self.step_size,
                                       self.num_steps)
        # apply Metropolis correction.
        energy_proposal = self._energy(z_new, r_new)
        energy_current = self._energy(z, r)
        delta_energy = energy_proposal - energy_current
        rand = pyro.sample('rand_t='.format(self._t), dist.Uniform(ng_zeros(1), ng_ones(1)))
        if rand.log() < -delta_energy:
            self._accept_cnt += 1
            z = z_new
        self._t += 1

        # get trace with the constrained values for `z`.
        for name, transform in self.transforms.items():
            z[name] = transform.inv(z[name])
        return self._get_trace(z)

    def diagnostics(self):
        return 'Acceptance rate: {}'.format(self._accept_cnt / self._t)

    def velocity_verlet(z, r, potential_fn, step_size, num_steps):
        """
        Second order symplectic integrator that uses the velocity verlet algorithm.
        :param dict z: dictionary of sample site names and their current values
            (type ``torch.autograd.Variable``).
        :param dict r: dictionary of sample site names and corresponding momenta
            (type ``torch.autograd.Variable``).
        :param callable potential_fn: function that returns potential energy given z
            for each sample site. The negative gradient of the function with respect
            to ``z`` determines the rate of change of the corresponding sites'
            momenta ``r``.
        :param float step_size: step size for each time step iteration.
        :param int num_steps: number of discrete time steps over which to integrate.
        :param dict transforms: Optional dictionary that specifies a transform
            for a sample site with constrained support to unconstrained space. The
            transform should be invertible, and implement `log_abs_det_jacobian`.
        :return tuple (z_next, r_next): final position and momenta, having same types as (z, r).
        """
        z_next = z.copy()
        r_next = r.copy()
        grads, _ = _grad(potential_fn, z_next)

        for _ in range(num_steps):
            for site_name in z_next:
                # r(n+1/2)
                r_next[site_name] = r_next[site_name] + 0.5 * step_size * (-grads[site_name])
                # z(n+1)
                z_next[site_name] = z_next[site_name] + step_size * r_next[site_name]
            grads, _ = _grad(potential_fn, z_next)
            for site_name in r_next:
                # r(n+1)
                r_next[site_name] = r_next[site_name] + 0.5 * step_size * (-grads[site_name])
        return z_next, r_next

    def single_step_velocity_verlet(z, r, potential_fn, step_size, z_grads=None):
        """
        A special case of ``velocity_verlet`` integrator where ``num_steps=1``. It is particular
        helpful for NUTS kernel.
        :param torch.Tensor z_grads: optional gradients of potential energy at current ``z``.
        :return tuple (z_next, r_next, z_grads, potential_energy): next position and momenta,
            together with the potential energy and its gradient w.r.t. ``z_next``.
        """
        z_next = z.copy()
        r_next = r.copy()
        grads = _grad(potential_fn, z_next)[0] if z_grads is None else z_grads

        for site_name in z_next:
            r_next[site_name] = r_next[site_name] + 0.5 * step_size * (-grads[site_name])
            z_next[site_name] = z_next[site_name] + step_size * r_next[site_name]
        grads, potential_energy = _grad(potential_fn, z_next)
        for site_name in r_next:
            r_next[site_name] = r_next[site_name] + 0.5 * step_size * (-grads[site_name])
        return z_next, r_next, grads, potential_energy

    def _grad(potential_fn, z):
        z = {k: Variable(v, requires_grad=True) for k, v in z.items()}
        z_keys, z_nodes = zip(*z.items())
        potential_energy = potential_fn(z)
        grads = grad(potential_energy, z_nodes)
        grads = [v.data for v in grads]
        return dict(zip(z_keys, grads)), potential_energy