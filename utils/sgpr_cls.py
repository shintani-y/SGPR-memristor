import pyro.contrib.gp as gp
import torch
import pyro
from pyro.nn.module import pyro_method, PyroParam, PyroModule, PyroSample
from torch.distributions import constraints
import pyro.distributions as dist
from torch.nn import Parameter

class SparseGPRegression(gp.models.SparseGPRegression):
    def __init__(
        self, X, y, kernel, Xu, noise=None, mean_function=None, approx=None, jitter=1.
    ):
        gp.models.GPModel.__init__(self, X, y, kernel, mean_function, jitter)
        self.jitter = PyroParam(torch.tensor(jitter), constraints.positive)

        test = Xu.view(-1)[0]
        if not (type(test) == torch.Tensor
                and test.requires_grad):
            self.Xu = Parameter(Xu)
        else:
            # For DGPLVM
            self.Xu = Xu

        noise = self.X.new_tensor(1.0) if noise is None else noise
        self.noise = PyroParam(noise, constraints.positive)

        if approx is None:
            self.approx = "VFE"
        elif approx in ["DTC", "FITC", "VFE"]:
            self.approx = approx
        else:
            raise ValueError(
                "The sparse approximation method should be one of "
                "'DTC', 'FITC', 'VFE'."
            )

        # For forward
        self.tmp2_cached = None
        self.Luu_cached = None
        self.L_cached = None

    def cache_preds(self):
        self.set_mode("guide")

        N = self.X.size(0)
        M = self.Xu.size(0)

        Kuu = self.kernel(self.Xu).contiguous()
        Kuu.view(-1)[:: M + 1] += self.jitter  # add jitter to the diagonal
        Luu = torch.linalg.cholesky(Kuu)

        Kuf = self.kernel(self.Xu, self.X)

        W = Kuf.triangular_solve(Luu, upper=False)[0]
        D = self.noise.expand(N)
        if self.approx == "FITC":
            Kffdiag = self.kernel(self.X, diag=True)
            Qffdiag = W.pow(2).sum(dim=0)
            D = D + Kffdiag - Qffdiag

        W_Dinv = W / D
        K = W_Dinv.matmul(W.t()).contiguous()
        K.view(-1)[:: M + 1] += 1  # add identity matrix to K
        L = torch.linalg.cholesky(K) # TODO: cache

        # get y_residual and convert it into 2D tensor for packing
        y_residual = self.y - self.mean_function(self.X)
        y_2D = y_residual.reshape(-1, N).t()
        W_Dinv_y = W_Dinv.matmul(y_2D) # TODO: cache

        c = W_Dinv_y.triangular_solve(L, upper=False)[0] #ok
        tmp1 = c.triangular_solve(L.t(), upper=True)[0]
        tmp2 = tmp1.triangular_solve(Luu.t(), upper=True)[0]
        self.tmp2_cached = tmp2 # W_vec

        self.Luu_cached = Luu
        self.L_cached = L

    def forward(self, Xnew, full_cov=False, noiseless=True, no_cov=False):
        r"""
        Computes the mean and covariance matrix (or variance) of Gaussian Process
        posterior on a test input data :math:`X_{new}`:
        .. math:: p(f^* \mid X_{new}, X, y, k, X_u, \epsilon) = \mathcal{N}(loc, cov).
        .. note:: The noise parameter ``noise`` (:math:`\epsilon`), the inducing-point
            parameter ``Xu``, together with kernel's parameters have been learned from
            a training procedure (MCMC or SVI).
        :param torch.Tensor Xnew: A input data for testing. Note that
            ``Xnew.shape[1:]`` must be the same as ``self.X.shape[1:]``.
        :param bool full_cov: A flag to decide if we want to predict full covariance
            matrix or just variance.
        :param bool noiseless: A flag to decide if we want to include noise in the
            prediction output or not.
        :returns: loc and covariance matrix (or variance) of :math:`p(f^*(X_{new}))`
        :rtype: tuple(torch.Tensor, torch.Tensor)
        """
        self._check_Xnew_shape(Xnew)
        self.set_mode("guide")

        # W = inv(Luu) @ Kuf
        # Ws = inv(Luu) @ Kus
        # D as in self.model()
        # K = I + W @ inv(D) @ W.T = L @ L.T
        # S = inv[Kuu + Kuf @ inv(D) @ Kfu]
        #   = inv(Luu).T @ inv[I + inv(Luu)@ Kuf @ inv(D)@ Kfu @ inv(Luu).T] @ inv(Luu)
        #   = inv(Luu).T @ inv[I + W @ inv(D) @ W.T] @ inv(Luu)
        #   = inv(Luu).T @ inv(K) @ inv(Luu)
        #   = inv(Luu).T @ inv(L).T @ inv(L) @ inv(Luu)
        # loc = Ksu @ S @ Kuf @ inv(D) @ y = Ws.T @ inv(L).T @ inv(L) @ W @ inv(D) @ y
        # cov = Kss - Ksu @ inv(Kuu) @ Kus + Ksu @ S @ Kus
        #     = kss - Ksu @ inv(Kuu) @ Kus + Ws.T @ inv(L).T @ inv(L) @ Ws

        N = self.X.size(0)
        M = self.Xu.size(0)

        if self.tmp2_cached is None:
            self.cache_preds()

        tmp2 = self.tmp2_cached # W_vec

        Kus = self.kernel(self.Xu, Xnew)


        C = Xnew.size(0)
        loc_shape = self.y.shape[:-1] + (C,)

        loc = Kus.t().matmul(tmp2).reshape(loc_shape) + self.mean_function(Xnew)

        if no_cov:
            return loc, loc.new_zeros(loc_shape)

        Luu = self.Luu_cached
        L = self.L_cached

        Ws = Kus.triangular_solve(Luu, upper=False)[0]
        Linv_Ws = Ws.triangular_solve(L, upper=False)[0]

        if full_cov:
            Kss = self.kernel(Xnew).contiguous()
            if not noiseless:
                Kss.view(-1)[:: C + 1] += self.noise  # add noise to the diagonal
            Qss = Ws.t().matmul(Ws)
            cov = Kss - Qss + Linv_Ws.t().matmul(Linv_Ws)
            cov_shape = self.y.shape[:-1] + (C, C)
            cov = cov.expand(cov_shape)
        else:
            Kssdiag = self.kernel(Xnew, diag=True)
            if not noiseless:
                Kssdiag = Kssdiag + self.noise
            Qssdiag = Ws.pow(2).sum(dim=0)
            cov = Kssdiag - Qssdiag + Linv_Ws.pow(2).sum(dim=0)
            cov_shape = self.y.shape[:-1] + (C,)
            cov = cov.expand(cov_shape)

        return loc, cov
