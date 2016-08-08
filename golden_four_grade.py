import os
import argparse
import operator
import csv
from collections import defaultdict
"""
Extract the Golden Four courses for each CCSF student
and create a Saleforce DataLoader ready CSV file.

How to USE:

STEP 1:

    Copy this script into a folder containing only the CSV file version of the
    CCSF Banner query.

STEP 2:
    Windows: Double click this file

    OSX/Linux: Change directory to the folder and run
    'python golden_four.py'


NOTES:
    If there are no CSV files in the folder this will do nothing.
    If there is more than one CSV file it will pick the first one it finds that
    doesn't have the same name as args.outfile (which is defaulted to
    "00-CCSF_Golden_Four.csv").
    You may specify the name of the RST file and/or the name of the new file if
    you run from terminal.

For running from terminal help:
    Run 'python golden_four.py -h'
"""


def parse_args():
    p = argparse.ArgumentParser(description="Extract Golden Four")
    p.add_argument("infile", help="Name of input file", nargs='?')
    p.add_argument(
        "outfile", help="Name of output file.",
        default="00-CCSF_Golden_Four.csv", nargs='?'
    )
    args = p.parse_args()
    return args


def read_cnv(infile, outfile):
    if not infile:
        print("Searching for CSV file")
        for filename in os.listdir("./"):
            if (os.path.splitext(filename)[1] == ".csv" and
                    filename != outfile):
                print("Found: " + filename)
                infile = filename
                break

    print("Opening: " + infile)
    with open(infile) as f:
        raw_rows = list(
            csv.reader(
                f.read().splitlines(),
                delimiter=',',
                quotechar='"'
            )
        )

    header_row = raw_rows[0]
    rows = raw_rows[1:]
    return header_row, rows


def write_csv(outfile, csv_lines):
    print("Creating CSV file: " + outfile)
    with open(outfile, 'wb') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(csv_lines)

    print("DONE")


def filter_duplicates(rows, sort_indices, filter_indices):
    rows.sort(key=operator.itemgetter(*sort_indices))

    prev_row = rows[0]
    filtered_rows = [prev_row]
    for row in rows:
        duplicate_of_prev = True
        for index in filter_indices:
            if row[index] != prev_row[index]:
                duplicate_of_prev = False

        if not duplicate_of_prev:
            filtered_rows.append(row)
        else:
            print("Filtered out row: " + repr(row))
        prev_row = row
    return filtered_rows


def extract_golden_four():
    pass


def initial_golden_four():
    return {'A1': set(), 'A2': set(), 'A3': set(), 'B4': set()}


def main():
    args = parse_args()
    header_row, rows = read_cnv(args.infile, args.outfile)

    ID = header_row.index("Id")
    SUBJECT = header_row.index("SubjAreaCode")
    COURSE_NUMBER = header_row.index("CrseNo")
    GOLDEN_FOUR_CODE = header_row.index("CSU_GE")
    GRADE = header_row.index("Grde_Code_Final")

    print("Sorting rows by Id then SubjAreaCode then CrseNo "
          "then CSU_GE then Grde_Code_Final")
    print("Filtering out duplicates (keeping the highest grade)")
    rows = filter_duplicates(
        rows,
        sort_indices=(ID, SUBJECT, COURSE_NUMBER, GOLDEN_FOUR_CODE, GRADE),
        filter_indices=(ID, SUBJECT, COURSE_NUMBER, GOLDEN_FOUR_CODE)
    )

    print("Extract Golden Four courses")
    student_id2golden_four = defaultdict(initial_golden_four)
    for row in rows:
        for code in row[GOLDEN_FOUR_CODE].split("|"):
            if code in ["A1", "A2", "A3", "B4"]:
                course = " ".join(
                    (row[SUBJECT].strip(), row[COURSE_NUMBER].strip())
                )
                student_id2golden_four[row[ID]][code].add(
                    (course, row[GRADE])
                )

    # write_csv(args.outfile, [header_row] + rows)


if __name__ == '__main__':
    main()
