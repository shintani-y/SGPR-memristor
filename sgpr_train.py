from sgpr_train_current import main as main_current
from sgpr_train_state import main as main_state
import sys


def main(train_file):

    # generate state
    state_train_time = main_state(train_file)

    # generate current
    current_train_time = main_current(train_file)

    train_time = state_train_time + current_train_time

    with open("./log_python.txt", mode="a") as f:
        f.write(f"State+Current:TrainTime({train_time}[sec])" + "\n\n")


if __name__ == "__main__":
    lines = sys.argv
    train_file = lines[1]
    main(train_file)
