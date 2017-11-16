import numpy as np
from torch.autograd import Variable
import torch
import scipy.stats as ss


def VariableCast(value):
    if isinstance(value, torch.autograd.variable.Variable):
        return value
    elif torch.is_tensor(value):
        return Variable(value)
    else:
        return Variable(torch.Tensor([value]), requires_grad = True)

def TensorCast(value):
    if isinstance(value, torch.Tensor):
        return value
    else:
        return torch.Tensor([value])


class Normal():
    """1d Normal random variable"""
    def __init__(self, mean, std):
        """Initialize this distribution with mean, variance.

        input:
            mean: 
            std:  standard deviation
        """

        self.mean = VariableCast(mean)
        if len(mean.data.shape) == 1:
            self.mean = mean.unsqueeze(1)
        self.std = VariableCast(std)


    def sample(self, num_samples = 1):
        x = torch.randn(1)
        sample = Variable(x * self.std.data + self.mean.data, requires_grad = True)
        return sample #.detach()


    def logpdf(self, value):
        mean = self.mean
        var = self.std ** 2
        value = VariableCast(value)
        if len(value.data.shape) == 1:
            value = value.unsqueeze(1)
        if isinstance(mean, torch.IntTensor):
            mean = mean.type(torch.FloatTensor)
        # pdf: 1 / torch.sqrt(2 * var * np.pi) * torch.exp(-0.5 * torch.pow(value - mean, 2) / var)
        return (-0.5 * torch.pow(value - mean, 2) / var - 0.5 * torch.log(2 * var * np.pi))


class MultivariateNormal():
    """Normal random variable"""
    def __init__(self, mean, cov):
        """Initialize this distribution with mean, cov.

        input:
            mean: n by 1
            cov: covariance matrix, n by n 
        """
        self.mean = VariableCast(mean)
        self.cov = VariableCast(cov)
        assert self.mean.data.size()[0] == self.cov.data.size()[0] #, "ERROR! mean and cov have different size!")
        self.dim = self.mean.data.size()[0]
        self.chol_std = VariableCast(torch.t(torch.potrf(self.cov.data)))  # lower triangle
        self.chol_std_inv = torch.inverse(self.chol_std)

    def sample(self, num_samples=1 ):
        zs = torch.randn(self.dim, 1)
        # print("zs", zs)
        samples = Variable( self.mean.data + torch.matmul(self.chol_std.data, zs), requires_grad = True)
        return samples

    def logpdf(self, value):
        """
        value : obs value, should be n by 1
        :return: scalar, log pdf value
        """
        value = VariableCast(value)
        cov_det = self.chol_std.diag().prod() ** 2
        log_norm_constant = 0.5 * self.dim * torch.log(torch.Tensor([2 * np.pi])) \
                            + 0.5*torch.log(cov_det.data)
        right = torch.matmul( self.chol_std_inv, value - self.mean)
        # print(value, self.mean, value - self.mean)
        log_p = - Variable(log_norm_constant) - 0.5 * torch.matmul(torch.t(right), right)
        return log_p

class Categorical():
    """categorical Normal random variable"""

    def __init__(self, p):
        """Initialize this distribution with p =[p0, p1, ..., pn].

        input:
            mean: 
            std:  standard deviation

        output:
            integer in [1, ..., n]
        """

        self.p = VariableCast(p)

    def sample(self):
        onedraw = np.random.multinomial(1, self.p.data.numpy())
        index = np.argwhere(onedraw == 1)[0,0]
        var = Variable(torch.Tensor([int(index)]) +1 ,requires_grad = True)
        return var

    def logpdf(self, value):
        int_value =  int(value.data.numpy())
        index = int_value -1
        if 1 <= int_value <= self.p.data.shape[0]:
            return torch.log(self.p[index])
        else:
            return torch.Tensor([-np.inf])

class Categorical_Trans():
    """categorical Tranformed random variable"""

    def __init__(self, p, method=None):
        """Initialize this distribution with p =[p0, p1, ..., pn].

        input:
            mean: 
            std:  standard deviation

        output:
            integer in [1, ..., n]
        """

        self.p = VariableCast(p)
        if method is None:
            self.method = "standard"
        else:
            self.method = method

    def logpdf(self, value):  # logp: 1*1
        if self.method == "standard":

            value =  VariableCast(value)
            if len(value.data.shape) == 1:
                value = value.unsqueeze(1)

            int_value = int(torch.floor(value.data)[0,0])
            index = int_value - 1

            #returning logp is [-0.93838], wrapped by tensor
            if 1 <= value.data[0,0] <= self.p.data.shape[0] + 1:
                logp = torch.log(self.p[index])   # grad does not survive through this embedding
                if len(logp.data.shape) == 1:
                    logp = logp.unsqueeze(1)
                return logp
            else:
                return Variable(torch.Tensor([[-np.inf]]))
        else:
            raise ValueError("implement categorical transformed method")
            return 0


class Binomial_Trans():
    """ binomial distribution, into contnuous space
       discrete distribution does not support grad for now
    """

    def __init__(self, n, p, method=None):
        """Initialize this distribution with 
        :parameter 
         n; N_0, non-negative integar
         p: [0, 1]

        output:
            integer in [0, 1, ..., n]
        """

        self.p = VariableCast(p)
        self.n = VariableCast(n)
        if method is not None:
            self.method = method
        else:
            self.method = "standard"

    def logpdf(self, k):  # logp: 1*1
        k = VariableCast(k)
        n = self.n
        p = self.p
        if len(k.data.shape) == 1:
            k = k.unsqueeze(1)
        if len(self.n.data.shape) == 1:
            n = n.unsqueeze(1)
        if len(self.p.data.shape) == 1:
            p = p.unsqueeze(1)

        if self.method == "standard":
            int_k = int(torch.floor(k.data)[0,0])
            int_n = int(torch.floor(n.data)[0,0])
            np_p = p.data[0,0]

            #returning logp is [-0.93838], wrapped by tensor
            if 0 <= int_k <= int_n:
                logpmf = ss.binom.logpmf(int_k, int_n, np_p)
                logp = Variable(torch.Tensor([logpmf]))
                if len(logp.data.shape) == 1:
                    logp = logp.unsqueeze(1)
                return logp
            else:
                return Variable(torch.Tensor([[-np.inf]]))
        else:
            raise ValueError("implement categorical transformed method")
            return 0


class Bernoulli_Trans():
    """ bernoulli distribution, into contnuous space
       discrete distribution does not support grad for now
    """

    def __init__(self, p, method=None):
        """Initialize this distribution with 
        :parameter 
         p: [0, 1]
        """

        self.p = VariableCast(p)
        if len(self.p.data.shape) == 1:
            self.p = self.p.unsqueeze(1)
        if method is not None:
            self.method = method
        else:
            self.method = "standard"
    def sample(self):
        """
        :return: x in [0,1], [1, 2]
        """
        x = torch.bernoulli(self.p) + Variable(torch.rand(1))
        if len(x.data.shape) == 1:
            x = x.unsqueeze(1)
        return x

    def logpdf(self, x):  # logp: 1*1
        x = VariableCast(x)
        p = self.p
        if len(x.data.shape) == 1:
            x = x.unsqueeze(1)

        if self.method == "standard":

            #returning logp is 1 by 1
            if 0 <= x.data[0,0] < 1:
                logp = torch.log(1-p)
                if len(logp.data.shape) == 1:
                    logp = logp.unsqueeze(1)
                return logp
            elif 1 <= x.data[0, 0] < 2:
                logp = torch.log(p)
                if len(logp.data.shape) == 1:
                    logp = logp.unsqueeze(1)
                return logp
            else:
                return Variable(torch.Tensor([[-np.inf]]))
        else:
            raise ValueError("implement categorical transformed method")
            return 0
