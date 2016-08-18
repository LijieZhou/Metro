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
    Run 'python golden_four.py -help'

"""


def parse_args():
    """
    Parse the arguments given to the script.

    `python golden_four.py --help` to display usage message.
    """
    p = argparse.ArgumentParser(description="Extract Golden Four")
    p.add_argument("infile", help="Name of input file", nargs='?')
    p.add_argument(
        "outfile", help="Name of output file.",
        default="00-CCSF_Golden_Four.csv", nargs='?'
    )
    args = p.parse_args()
    return args


class FileNotFound(Exception):
    pass


def find_csv_file(infile, outfile):
    """
    Finds a CSV file in the current directory. If no `infile` is given,
    the first CSV file in the current directory that isn't `outfile` is
    returned. Otherwise, `infile` is checked to make sure it exists and
    is a CSV file.

    Args:
        infile - file path or None
        outfile - file path

    Returns:
        string - file path to CSV file

    Raises:
        FileNotFound - when a proper CSV file is not found
    """
    if not infile:
        print("Searching for CSV file")
        for filename in os.listdir("./"):
            if (os.path.splitext(filename)[1] == ".csv" and
                    filename != outfile):
                print("Found: " + filename)
                infile = filename
                break
        if not infile:
            raise FileNotFound(
                "Could not find a CSV file in current directory")

    if os.path.splitext(infile)[1] != ".csv":
        raise FileNotFound("'" + infile + "' is not a CSV file")

    if not os.path.exists(infile):
        raise FileNotFound(
            "'" + infile + "' could not be found in current directory")

    return infile


def read_cnv(csv_file):
    """
    Reads a CSV file and separates the header row from the rest.

    Args:
        csv_file - file path to a CSV file

    Returns:
        2-tuple - header_row, rows
            header_row - list representing the first row in the CSV file
            rows - list of lists which each represent a row in the CSV file
    """
    print("Opening: " + csv_file)
    with open(csv_file) as f:
        raw_rows = list(
            csv.reader(
                f.read().splitlines(),
                delimiter=',',
                quotechar='"'
            )
        )

    header_row = raw_rows[0]
    # Using python list splicing to take all but the first row
    rows = raw_rows[1:]
    return header_row, rows


def write_csv(outfile, csv_lines):
    """
    Creates a CSV file and writes all the given rows to it.

    Args:
        outfile - file path of CSV output file
        csv_lines - list of lists each representing a row to write
    """
    print("Creating CSV file: " + outfile)
    with open(outfile, 'wb') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(csv_lines)

    print("DONE")


def filter_duplicates(rows, sort_indices, filter_indices):
    """
    Filters duplicate rows.

    Works by sorting the rows and the removing any row that is a duplicate of
    the previous row.

    Args:
        rows - list of lists each representing a row of a CSV file
        sort_indices - list of indices to sort the rows by
        filter_indices - list of indices to use for for checking equality
                         of rows

    Returns:
        filtered_rows - same format as rows, minues duplicate rows and sorted
    """
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


def format_courses(course_tuples):
    """
    Formats a set of course tuples (course, grade) into a comma separated list
    of courses and grades.

    e.g.
    set([("MATH 90", "A"), ("ANAT 25", "C")]) ->
        "MATH 90 A,ANAT 25 C"

    Args:
        course_tuples - a set of 2-tuples of strings (course, grade)

    Returns:
        string - formatted courses and grades
    """
    # Iterate course_tuples and join each tuple with " "
    # map(func, iterable) is equivalent to map(f(x) for x in iterable)
    formatted_courses = map(" ".join, course_tuples)

    # join each formatted_course with ","
    return ",".join(formatted_courses)


def is_complete(course_tuples):
    """
    Determines if the set of courses and grades satisfies a golden four
    requirement.

    Args:
        course_tuples - a set of 2-tuples of strings (course, grade)

    Returns:
        boolean - if there is a passing grade in `course_tuples`
    """

    PASSING_GRADES = ["A", "B", "C"]

    # extract the grades from each course tuple
    # operator.itemgetter constructs a callable that assumes iterable
    # object (list, set, tuple) as input and fetches n-th element out of it

    grades = map(operator.itemgetter(1), course_tuples)
    # any return true if any element of the iterable is true
    # if iterable is empty, return false
    return any([grade in grades for grade in PASSING_GRADES])


def main():
    """
    The main body of the script. Orchestrates reading in the CSV file
    and constructing the DataLoader ready output file.
    """
    # parse the arguments and read in the CSV file
    args = parse_args()
    csv_file = find_csv_file(args.infile, args.outfile)
    raw_header_row, rows = read_cnv(csv_file)

    # Create indices used to sort and filter the rows by
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

    print("Extracting Golden Four courses")

    def initial_golden_four():
        return {'A1': set(), 'A2': set(), 'A3': set(), 'B4': set()}

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

    # Create the header row for the output CSV file
    header_row = [
        "CCSF_STUDENT_ID__C", "A1_ORAL_COMMUNICATION__C", "A1_COMPLETED__C",
        "A2_WRITTEN_COMMUNICATION__C", "A2_COMPLETED__C",
        "A3_CRITICAL_THINKING__C", "A3_COMPLETED__C",
        "B4_MATH_QR__C", "B4_COMPLETED__C",
    ]

    # Create inidices for output CSV file
    ID = header_row.index("CCSF_STUDENT_ID__C")
    A1_COURSE = header_row.index("A1_ORAL_COMMUNICATION__C")
    A1_COMPLETION = header_row.index("A1_COMPLETED__C")
    A2_COURSE = header_row.index("A2_WRITTEN_COMMUNICATION__C")
    A2_COMPLETION = header_row.index("A2_COMPLETED__C")
    A3_COURSE = header_row.index("A3_CRITICAL_THINKING__C")
    A3_COMPLETION = header_row.index("A3_COMPLETED__C")
    B4_COURSE = header_row.index("B4_MATH_QR__C")
    B4_COMPLETION = header_row.index("B4_COMPLETED__C")

    # Create rows of output CSV file
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

    # sorts the CSV file by ID (the first row)
    csv_rows.sort()

    write_csv(args.outfile, [header_row] + csv_rows)


if __name__ == '__main__':
    main()
