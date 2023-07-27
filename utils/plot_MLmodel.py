import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class plot_MLmodel:
    def __init__(
        self,
        data_type: str,
        real_data: pd.DataFrame,
        pred_data: pd.DataFrame,
    ):

        xu = np.loadtxt(f"./save_sgpr/sgpr_xu_current.txt")
        self.xu_num = str(len(xu))

        self.s_label = "State"
        self.v_label = "Voltage[V]"
        self.c_label = "Current[mA]"
        self.t_label = "Time[nsec]"

        self.scale = 10**3

        self.Time = real_data["Time"]
        self.S = real_data["S"]
        self.Voltage = real_data["Voltage"]
        self.Current = real_data["Current"]

        self.Time_pred = pred_data["Time"]
        self.S_pred = pred_data["S"]
        self.Voltage_pred = pred_data["Voltage"]
        self.Current_pred = pred_data["Current"]

        self.img_path = "./img/"
        self.model_label = f"SGPR({self.xu_num})"
        self.log_file = "./log_hspice.txt"
        self.color = "red"

        if data_type == "train":
            self.img_path += "train/"
            self.real_label = "train data"
        elif data_type == "test":
            self.img_path += "test/"
            self.real_label = "test data"

        plt.rcParams["font.size"] = 15
        self.font = "DejaVu Sans"

    def plot_IV(self):

        file_name = "I-V2D"

        fig = plt.figure(tight_layout=True)
        ax = fig.add_subplot()

        ax.plot(
            self.Voltage_pred,
            self.Current_pred * self.scale,
            color=self.color,
            label=self.model_label,
            zorder=3,
        )
        ax.scatter(
            self.Voltage,
            self.Current * self.scale,
            s=40,
            marker=".",
            color="black",
            label=self.real_label,
            zorder=1,
        )

        self.legend_wrap(ax)
        self.label_wrap(ax, self.v_label, self.c_label)
        plt.grid(linestyle="dotted", alpha=0.6)
        self.savefig_wrap(file_name)

    def plot_IVS(self):

        file_name = "I-V-S3D"

        fig = plt.figure(tight_layout=True)
        ax = fig.add_subplot(projection="3d")

        self.label_wrap(ax, self.s_label, self.v_label, self.c_label)

        ax.plot(
            self.S_pred,
            self.Voltage_pred,
            self.Current_pred * self.scale,
            color=self.color,
            label=self.model_label,
            zorder=6,
        )
        ax.scatter(
            self.S,
            self.Voltage,
            self.Current * self.scale,
            s=60,
            marker=".",
            color="black",
            label=self.real_label,
            zorder=1,
        )

        ax.legend(
            frameon=False,
            prop={"family": self.font},
            bbox_to_anchor=(0.45, 1.10),
            loc="upper left",
        )

        self.savefig_wrap(file_name)

    def legend_wrap(self, ax):
        ax.legend(frameon=False, prop={"family": self.font})

    def label_wrap(self, ax, x, y, z=None):
        ax.set_xlabel(x, fontname=self.font)
        ax.set_ylabel(y, fontname=self.font)
        if z is not None:
            ax.set_xlabel(x, labelpad=10, fontname=self.font)
            ax.set_ylabel(y, labelpad=10, fontname=self.font)
            ax.set_zlabel(z, labelpad=10, fontname=self.font)

    def savefig_wrap(self, file_name):
        print(f"plot:{self.img_path}{file_name}.png")
        plt.savefig(self.img_path + f"{file_name}.png")
        plt.close()

    def evaluation_error(self):

        rmse_sgpr = self.cmp_rmse(self.Current, self.Current_pred)
        rmsle_sgpr = self.cmp_rmsle(self.Current, self.Current_pred)

        print(f"RMSE:{rmse_sgpr}")
        print(f"RMSLE:{rmsle_sgpr}")

        with open(self.log_file, mode="a") as f:
            f.write(f"SGPR({self.xu_num}){self.real_label}" + "\n")
            f.write(f"RMSE:{rmse_sgpr}[A]" + f" ({rmse_sgpr*1000}[mA])" + "\n")
            f.write(f"RMSLE:{rmsle_sgpr}[A]" + f" ({rmsle_sgpr*1000}[mA])" + "\n")

    def cmp_rmse(self, y_true, y_pred):
        mse = np.mean((y_true - y_pred) ** 2)
        rmse = np.sqrt(mse)
        return rmse

    def cmp_rmsle(self, y_true: pd.Series, y_pred: pd.Series):
        y_true_log = np.log1p(np.abs(y_true))
        y_pred_log = np.log1p(np.abs(y_pred))
        rmsle = self.cmp_rmse(y_true_log, y_pred_log)
        return rmsle

    def plot_TVI(self):

        file_name = "T-V-I"

        fig = plt.figure(figsize=(8, 8), tight_layout=True)
        ax1 = fig.add_subplot(2, 1, 1)

        ax1.scatter(
            self.Time,
            self.Voltage,
            s=40,
            marker=".",
            color="black",
            zorder=1,
        )

        self.label_wrap(ax1, self.t_label, self.v_label)
        plt.grid(linestyle="dotted", alpha=0.6)
        ax2 = fig.add_subplot(2, 1, 2)

        ax2.plot(
            self.Time_pred,
            self.Current_pred * self.scale,
            color=self.color,
            label=self.model_label,
            zorder=3,
        )
        ax2.scatter(
            self.Time,
            self.Current * self.scale,
            s=40,
            marker=".",
            color="black",
            label=self.real_label,
            zorder=1,
        )

        self.legend_wrap(ax2)
        self.label_wrap(ax2, self.t_label, self.c_label)
        plt.grid(linestyle="dotted", alpha=0.6)
        self.savefig_wrap(file_name)
