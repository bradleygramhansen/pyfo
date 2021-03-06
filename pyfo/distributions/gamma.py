import torch

from ..distributions.distribution_wrapper import TorchDistribution
from ..utils.core import VariableCast as vc

class Gamma(TorchDistribution):
    r"""
    """
    def __init__(self, alpha, beta, transformed=True):
        self.alpha = vc(alpha)
        self.beta= vc(beta)
        # if transformed:
        #     torch_dist = LogGamma(concentration=self.alpha, rate=self.beta)
        #     super(Gamma, self).__init__(torch_dist, Transformed=transformed)
        # else:
        torch_dist = torch.distributions.Gamma(concentration=self.alpha, rate=self.beta)
        super(Gamma, self).__init__(torch_dist)

