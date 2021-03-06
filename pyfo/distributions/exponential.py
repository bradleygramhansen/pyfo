import torch

from ..distributions.distribution_wrapper import TorchDistribution
from ..utils.core import VariableCast as vc


class Exponential(TorchDistribution):
    r"""
    Creates a Exponential distribution parameterized by `rate`.

    Example::

        >>> m = Exponential(torch.Tensor([1.0]))
        >>> m.sample()  # Exponential distributed with rate=1
         0.1046
        [torch.FloatTensor of size 1]

    Parameters:
        rate (float or Tensor or Variable): rate = 1 / scale of the distribution
    """
    def __init__(self, rate, transformed=False):
        self.rate =vc(rate)
        torch_dist = torch.distributions.Exponential(rate=self.rate)
        super(Exponential, self).__init__(torch_dist)