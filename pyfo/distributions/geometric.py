import torch

from ..distributions.distribution_wrapper import TorchDistribution
from ..utils.core import VariableCast as vc


class Geometric(TorchDistribution):
    r"""
    Creates a Fisher-Snedecor distribution parameterized by `df1` and `df2`.

    Example::

        >>> m = FisherSnedecor(torch.Tensor([1.0]), torch.Tensor([2.0]))
        >>> m.sample()  # Fisher-Snedecor-distributed with df1=1 and df2=2
         0.2453
        [torch.FloatTensor of size 1]

    Args:
        df1 (float or Tensor or Variable): degrees of freedom parameter 1
        df2 (float or Tensor or Variable): degrees of freedom parameter 2
    """
    def __init__(self, probs, logits):
        self.probs = vc(probs)
        self.logits = vc(logits)
        torch_dist = torch.distributions.Gamma(probs=self.probs, logits=self.logits)
        super(Geometric, self).__init__(torch_dist)