from string import Template
import sys
import json


def temp(from_f, to_f, subst):
    with open(from_f) as inputf:
        t = Template(inputf.read())

    outs = t.substitute(subst)

    with open(to_f, "w") as outf:
        outf.write(outs)


if __name__ == "__main__":
    from_f = sys.argv[1]
    to_f = sys.argv[2]
    subst_json = sys.argv[3]

    subst = json.loads(subst_json)

    temp(from_f, to_f, subst)
