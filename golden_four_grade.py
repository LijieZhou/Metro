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


def initial_golden_four():
    return {'A1': set(), 'A2': set(), 'A3': set(), 'B4': set()}


def main():
    args = parse_args()
    raw_header_row, rows = read_cnv(args.infile, args.outfile)

    ID = raw_header_row.index("Id")
    SUBJECT = raw_header_row.index("SubjAreaCode")
    COURSE_NUMBER = raw_header_row.index("CrseNo")
    GOLDEN_FOUR_CODE = raw_header_row.index("CSU_GE")
    GRADE = raw_header_row.index("Grde_Code_Final")

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

    header_row = [
        "CCSF_STUDENT_ID__C", "A1_ORAL_COMMUNICATION__C", "A1_COMPLETED__C",
        "A2_WRITTEN_COMMUNICATION__C", "A2_COMPLETED__C",
        "A3_CRITICAL_THINKING__C", "A3_COMPLETED__C",
        "B4_MATH_QR__C", "B4_COMPLETED__C",
    ]
    ID = header_row.index("CCSF_STUDENT_ID__C")
    A1_COURSE = header_row.index("A1_ORAL_COMMUNICATION__C")
    A1_COMPLETION = header_row.index("A1_COMPLETED__C")
    A2_COURSE = header_row.index("A2_WRITTEN_COMMUNICATION__C")
    A2_COMPLETION = header_row.index("A2_COMPLETED__C")
    A3_COURSE = header_row.index("A3_CRITICAL_THINKING__C")
    A3_COMPLETION = header_row.index("A3_COMPLETED__C")
    B4_COURSE = header_row.index("B4_MATH_QR__C")
    B4_COMPLETION = header_row.index("B4_COMPLETED__C")

    csv_rows = []
    for student_id, golden_four_dict in student_id2golden_four.iteritems():
        new_row = [''] * len(header_row)
        new_row[ID] = student_id
        new_row[A1_COURSE] = format_courses(golden_four_dict['A1'])
        new_row[A1_COMPLETION] = is_complete(golden_four_dict['A1'])
        new_row[A2_COURSE] = format_courses(golden_four_dict['A2'])
        new_row[A2_COMPLETION] = is_complete(golden_four_dict['A2'])
        new_row[A3_COURSE] = format_courses(golden_four_dict['A3'])
        new_row[A3_COMPLETION] = is_complete(golden_four_dict['A3'])
        new_row[B4_COURSE] = format_courses(golden_four_dict['B4'])
        new_row[B4_COMPLETION] = is_complete(golden_four_dict['B4'])
        csv_rows.append(new_row)

    csv_rows.sort()


    write_csv(args.outfile, [header_row] + csv_rows)


def format_courses(course_tuples):
    # Iterate course_tuples and join each tuple with " "
    # map(func, iterable) is equivalent to map(f(x) for x in iterable)

    formatted_courses = map(" ".join, course_tuples)
    
    # join each formatted_course with ","
    return ",".join(formatted_courses)


def is_complete(course_tuples):

    PASSING_GRADES = ["A", "B", "C"]

    # extract the grades from each course tuple
    # operator.itemgetter constructs a callable that assumes iterable object (list, set, tuple) as input
    # and fetches n-th element out of it
    # def get_second_elem(iterable)
    #     return iterable[1]

    grades = map(operator.itemgetter(1), course_tuples)
    #any return true if any element of the iterable is true
    # if iterable is empty, return false
    return any([grade in grades for grade in PASSING_GRADES])


if __name__ == '__main__':
    main()
