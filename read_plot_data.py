import pandas as pd
from utils.read_tran import read_tran
from utils.plot_MLmodel import plot_MLmodel as MLM
import sys


def main(train_file, test_file):

    train_data = pd.read_csv(train_file)
    test_data = pd.read_csv(test_file)

    verilog_train_data = read_tran("./HSPICE_train/output/output.lis")
    verilog_test_data = read_tran("./HSPICE_test/output/output.lis")

    # train data predict check
    mlm_train = MLM("train", train_data, verilog_train_data)
    mlm_train.plot_IV()
    mlm_train.plot_IVS()
    mlm_train.plot_TVI()
    mlm_train.evaluation_error()

    # test data predict check
    mlm_test = MLM("test", test_data, verilog_test_data)
    mlm_test.plot_IV()
    mlm_test.plot_IVS()
    mlm_test.plot_TVI()
    mlm_test.evaluation_error()

    with open("./log_hspice.txt", mode="a") as f:
        f.write("\n\n")


if __name__ == "__main__":
    lines = sys.argv
    main(lines[1], lines[2])
