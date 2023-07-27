import pandas as pd


def readlis(file_name):
    with open(file_name, "r") as f:
        kw_list = f.read().split("\n")

    start = (
        kw_list.index(" ****** transient analysis tnom=  25.000 temp=  25.000 ******")
        + 6
    )
    end = kw_list.index("          ***** job concluded") - 2
    d = [x.strip() for x in kw_list[start:end]]
    d = [x.replace("   ", " ") for x in d]
    n = [x.replace("  ", " ") for x in d]
    out = [x.split(" ") for x in n]
    return out


def strTofloat(str):
    n = [x.replace("e-0", "e-") for x in str]
    d = [x.replace("e+0", "e+") for x in n]
    n = [x.replace("e", "*10**") for x in d]
    out = [eval(x) for x in n]
    return out


def readCurrent(file_name):
    n = readlis(file_name)
    out = [x[2] for x in n]
    out = strTofloat(out)
    return out


def readVoltage(file_name):
    n = readlis(file_name)
    out = [x[1] for x in n]
    out = strTofloat(out)
    return out


def readTime(file_name):
    n = readlis(file_name)
    out = [x[0] for x in n]
    out = strTofloat(out)
    out = [(x * 10**9) for x in out]
    return out


def readState(file_name):
    n = readlis(file_name)
    out = [x[3] for x in n]
    out = strTofloat(out)
    return out


def read_tran(file_dir):
    Time = readTime(file_dir)
    State = readState(file_dir)
    Current = readCurrent(file_dir)
    Voltage = readVoltage(file_dir)

    return pd.DataFrame(
        {
            "Time": Time,
            "S": State,
            "Voltage": Voltage,
            "Current": Current,
        }
    ).astype(float)
