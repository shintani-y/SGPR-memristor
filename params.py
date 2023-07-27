import numpy as np
from utils.temp import temp


def main():
    out_dir = "./verilog"

    create_verilog(out_dir, "_state")
    print("generate state verilog file")

    create_verilog(out_dir, "_current")
    print("generate current verilog file")


def create_verilog(out_dir, suffix):
    base_dir = "./save_sgpr"
    temp_dir = "./temp"

    xu = np.loadtxt(f"{base_dir}/sgpr_xu{suffix}.txt")
    tmp2 = np.loadtxt(f"{base_dir}/sgpr_tmp2{suffix}.txt")
    rbf_var = np.loadtxt(f"{base_dir}/sgpr_rbf_var{suffix}.txt")
    rbf_len = np.loadtxt(f"{base_dir}/sgpr_rbf_len{suffix}.txt")

    ## variables
    subst = {
        "N": len(xu),
        "X_DIM": 2,
        "LENGTHSCALE": ",\\\n".join(map(str, rbf_len)) + "\\",
        "VARIANCE": rbf_var,
    }
    temp(
        f"{temp_dir}/variables{suffix}.temp.va",
        f"{out_dir}/variables{suffix}.va",
        subst,
    )

    ## w_vec
    subst = {"w": ",\\\n".join(map(str, tmp2)) + "\\"}
    temp(f"{temp_dir}/w_vec{suffix}.temp.va", f"{out_dir}/w_vec{suffix}.va", subst)

    ## xu
    subst = {"xu": ",\\\n".join([",".join(map(str, x)) for x in xu]) + "\\"}
    temp(f"{temp_dir}/xu{suffix}.temp.va", f"{out_dir}/xu{suffix}.va", subst)


if __name__ == "__main__":
    main()
