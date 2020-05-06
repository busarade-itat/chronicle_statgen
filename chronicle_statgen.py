#!/usr/bin/env python3

import sys
import re
import statistics
from argparse import ArgumentParser


# in order to separate the outputs to different files
# when utilizing output redirecting, the stats are written to stdout
# while the specific chronicles are written to stderr
def main():
    pars = ArgumentParser()
    pars.add_argument("--category", dest="category", type=str, default=None)
    pars.add_argument("--chrofile", dest="chrofile", type=str, default=None)
    pars.add_argument("--logfile", dest="logfile", type=str, default=None)
    pars.add_argument("--vecsize", dest="vecsize", type=str, default=None)
    pars.add_argument("--minspec", dest="minspec", type=str, default=None)

    args = pars.parse_args(sys.argv[1:])

    if args.minspec is not None:
        print("-------------------------------------------------", file=sys.stderr)

    if args.chrofile is not None and args.chrofile is not None and args.vecsize is not None:
        chronicles = []
        frequent_mset_count = 0
        valid_mset_count = 0
        specific_count = 0

        with open(args.chrofile, "r") as chronicle_lines, open(args.logfile, "r") as log_lines:
            chronicles = parse_chronicle_list(chronicle_lines)
            frequent_mset_count = get_frequent_mset_count(log_lines)

        valid_mset_count = get_valid_mset_count(chronicles)

        specificities = []

        for chronicle in chronicles:
            chro_specificity = compute_specificity(chronicle, args.vecsize)
            specificities.append(chro_specificity)

            if args.minspec is not None and chro_specificity >= float(args.minspec):
                specific_count += 1
                print("SPECIFIC AND DISCRIMINANT (specificity=" + str(chro_specificity) + ")", file=sys.stderr)
                print(chronicle, file=sys.stderr)

        if args.category is not None:
            print(args.category + ",", end="") # category

        print(str(frequent_mset_count) + ",", end="") # |M|
        print(str(valid_mset_count) + ",", end="") # {E | E \in M AND E is in a discriminant chronicle from C}
        print(str(max(specificities)) + ",", end = "") #max(S(C))
        print(str(specific_count)) # s(C, t_s)

        exit(0)
    else:
        print("The --chrofile, --logfile and --vecsize arguments must be supplied to stats generator.", file=sys.stderr)

        exit(2)


def compute_specificity(chronicle, vecsize):
    chronicle_lines = chronicle.split("\n")

    chronicle_lines.remove("") # remove trailing blank line if present
    chronicle_lines.pop(0) # remove multiset line
    chronicle_lines.pop(-1) # remove computed supports
    chronicle_lines.pop(-1) # remove class

    tc_count = len(chronicle_lines)
    specific_count = 0

    for tc in chronicle_lines:
        if tc.find(get_unspecific_interval(vecsize)) == -1:
            specific_count += 1

    return specific_count/tc_count if tc_count != 0 else 0


def get_unspecific_interval(vecsize):
    return ": (" + get_lb_infinity(vecsize) + ", " + get_ub_infinity(vecsize) + ")"


def get_lb_infinity(vecsize):
    out = "<"

    for i in range(int(vecsize)):
        out += "-inf"

        if i < int(vecsize)-1:
            out += ","

    out += ">"

    return out


def get_ub_infinity(vecsize):
    out = "<"

    for i in range(int(vecsize)):
        out += "inf"

        if i < int(vecsize)-1:
            out += ","

    out += ">"

    return out


def parse_chronicle_list(chronicle_lines):
    out = []
    buffer = ""

    for chro_line in chronicle_lines:
        if chro_line.rstrip() == "":
            out.append(buffer)
            buffer = ""
        else:
            buffer += chro_line

    return out


def get_frequent_mset_count(log_lines):
    out = 0

    for log_line in log_lines:
        regex = r"^\[INFO\] Multisets number: (\d+)$"
        matches = re.finditer(regex, log_line.rstrip())

        for _, match in enumerate(matches, start=1):
            out += int(match.group(1))

    return out


def get_valid_mset_count(chronicles):
    pos_chronicles = list(filter(lambda c: c.find("class: pos") != -1, chronicles))
    neg_chronicles = list(filter(lambda c: c.find("class: neg") != -1, chronicles))

    out = 0

    for chronicle_set in [pos_chronicles, neg_chronicles]:
        multisets = []

        for chro in chronicle_set:
            regex = r"C\d+: \{(.+), \}"
            matches = re.finditer(regex, chro)

            for _, match in enumerate(matches, start=1):
                multisets.append(convert_mset_to_string(match.group(1)))

        out += len(set(multisets)) # casting a list to a set removes duplicates

    return out

def convert_mset_to_string(mset_match):
    mset_elements = []
    filter_regex = r"([A-Z]+)\(\d\)(?:, |$)"

    matches = re.finditer(filter_regex, mset_match)

    for _, match in enumerate(matches, start=1):
        mset_elements.append(match.group(1))

    mset_elements.sort()
    return "".join(mset_elements)


if __name__ == "__main__":
    main()
