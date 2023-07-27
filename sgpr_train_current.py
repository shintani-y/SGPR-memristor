import time
import sys
from tqdm import tqdm
import torch
import numpy as np
import pandas as pd

import pyro
import pyro.contrib.gp as gp
from utils.sgpr_cls import SparseGPRegression as SGPR


def main(train_file):

    torch.set_num_threads(10)
    pyro.set_rng_seed(0)
    pyro.clear_param_store()

    scale = 10**4

    train_data = pd.read_csv(train_file)

    x1 = torch.Tensor(train_data["S"].values)
    x2 = torch.Tensor(train_data["Voltage"].values)
    y1 = torch.Tensor(train_data["Current"].values * scale)
    X = torch.stack((x1, x2), dim=1)
    y = y1

    kernel = gp.kernels.RBF(input_dim=2, lengthscale=torch.tensor([1.0, 1.0]))

    xu = 50

    x_inducing = torch.Tensor(
        [[_x1, _x2] for _x1 in [0.0] for _x2 in np.linspace(-1.5, 1.5, xu // 2)]
        + [[_x1, _x2] for _x1 in [1.0] for _x2 in np.linspace(-1.5, 1.0, xu // 2)]
    )

    sgpr = SGPR(X, y, kernel, Xu=x_inducing, jitter=1e-6, noise=X.new_tensor(0.001))

    optimizer = torch.optim.Adam(sgpr.parameters(), lr=0.1)
    loss_fn = pyro.infer.TraceMeanField_ELBO().differentiable_loss
    losses = []
    epoc = 200
    mod_jitter = 2

    start = time.time()
    with tqdm(range(epoc), desc="[train]") as pbar:
        for i in pbar:
            try:
                optimizer.zero_grad()
                loss = loss_fn(sgpr.model, sgpr.guide)
                loss.backward()
                optimizer.step()
                losses.append(loss.item())
                pbar.set_postfix({"Loss": f"{loss.item():.1f}"})
                sgpr.cache_preds()
                if loss.item() < 0:
                    break
            except ValueError as e:
                print(e)
                sgpr.jitter = sgpr.jitter * mod_jitter
                print(f"jitter set to {sgpr.jitter}")
                if sgpr.jitter > 1.0:
                    break
            except RuntimeError as e:
                print(e)
                sgpr.jitter = sgpr.jitter * mod_jitter
                print(f"jitter set to {sgpr.jitter}")
                if sgpr.jitter > 1.0:
                    break

    process_time = time.time() - start
    print(process_time)

    save_model(sgpr)
    return process_time


# save model
def save_model(sgpr: SGPR):
    file_path = f"./save_sgpr/"
    suffix = "_" + "current"
    torch.save(sgpr.state_dict(), f"{file_path}sgpr{suffix}.model")
    sgpr.cache_preds()
    np.savetxt(f"{file_path}sgpr_xu{suffix}.txt", sgpr.Xu.detach().numpy())
    np.savetxt(f"{file_path}sgpr_tmp2{suffix}.txt", sgpr.tmp2_cached.detach().numpy())
    np.savetxt(
        f"{file_path}sgpr_rbf_var{suffix}.txt",
        [sgpr.kernel.variance.detach().numpy()],
    )
    np.savetxt(
        f"{file_path}sgpr_rbf_len{suffix}.txt",
        sgpr.kernel.lengthscale.detach().numpy(),
    )
    print(f"save model and hyperparameter{suffix}")


if __name__ == "__main__":
    lines = sys.argv
    train_file = lines[1]
    main(train_file)
