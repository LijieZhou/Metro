import os
import argparse
import operator
import csv

"""
Extract the most relavent degree/certificate for each CCSF student
and create a Saleforce DataLoader ready CSV file.

How to USE:

STEP 1:

    Copy this script into a folder containing only the CSV file version of the
    CCSF Banner query.

STEP 2:
    Windows: Double click this file

    OSX/Linux: Change directory to the folder and run
    'python CCSF_degrees_and_certificates.py'


NOTES:
    If there are no CSV files in the folder this will do nothing, but will
    yell at you a bit about that.
    If there is more than one CSV file it will pick the first one it finds that
    doesn't have the same name as args.outfile (which is defaulted to
    "00-CCSF_Degrees_and_Certificates.csv").
    You may specify the name of the input file and/or the name of the output
    file if you run from terminal.

For running from terminal help:
    Run 'python CCSF_degrees_and_certificates.py -h'
"""


def parse_args():
    """
    Parse the arguments given to the script.

    `python golden_four.py --help` to display usage message.
    """
    p = argparse.ArgumentParser(description="Extract degrees/certificates.")
    p.add_argument("infile", help="Name of input file", nargs='?')
    p.add_argument(
        "outfile", help="Name of output file.",
        default="00-CCSF_Degrees_and_Certificates.csv", nargs='?'
    )
    args = p.parse_args()
    return args


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


DEGREE_CODES = [
    "AA-T",
    "AS-T",
    "AA",
    "AS",
    "AW_T",
    "AWARD",
    "CACC",
    "CACC_E",
    "CACH_T",
    "CACH_L",
    "CACH_B",
    "CACH",
    "CC",
    "CCE",
    "CCL",
    "CCT",
]

CODE_TO_DESCRIPTION = {
    "AA-T/AS-T": "Associate in Arts and Sci. for Transfer",
    "AA-T": "Associate in Arts for Transfer",
    "AS-T": "Associate in Sci. for Transfer",
    "AA/AS": "Associate in Arts and Science",
    "AA": "Associate in Arts",
    "AS": "Associate in Science",
    "AW_T": "Award of Achievement",
    "AWARD": "Award of Achievement",
    "CACC": "Certificate of Accomplishment",
    "CACC_E": "Certificate of Accomplishment",
    "CACH": "Certificate of Achievement",
    "CACH_L": "Certificate of Achievement",
    "CACH_T": "Certificate of Achievement",
    "CACH_B": "Certificate of Achievement",
    "CC": "Certificate of Completion",
    "CCE": "Certificate of Completion",
    "CCL": "Certificate of Completion",
    "CCT": "Certificate of Completion",
}


def extract_degree(all_degrees):
    """
    Extracts the most important degree from a list of degrees.
    It does this by splitting out all the degrees and sorting them, using
    DEGREE_CODES above for order of importance.

    Note: This expects there to be at least one degree. Don't call this
          function on an empty string.

    Args:
        all_degrees - string of degrees seperated by |'s (vertical bars)
            e.g. AWARD on 22-MAY-2009 (200930)|AA on 21-DEC-2008 (200870)

    Returns:
        string - the most important degree
    """
    degrees = map(lambda d: d.split(" ")[0], all_degrees.split("|"))
    degrees.sort(key=lambda d: DEGREE_CODES.index(d))
    degree_code = degrees[0]
    if len(degrees) > 1:
        if degrees[0] == "AA-T" and degrees[1] == "AS-T":
            degree_code = "AA-T/AS-T"
        elif degrees[0] == "AA" and degrees[1] == "AS":
            degree_code = "AA/AS"

    return CODE_TO_DESCRIPTION[degree_code]


def main():
    args = parse_args()
    csv_file = find_csv_file(args.infile, args.outfile)
    header_row, rows = read_cnv(csv_file)

    # Create indices for the input CSV file
    ID = header_row.index("StudentId")
    ALL_DEGREES = header_row.index("All_DegreesEarned_Code")
    students = [("STUDENT_ID", "DEGREE_EARNED")]
    print("Extracting degrees")
    for row in rows:
        # Check if there are any degrees
        if row[ALL_DEGREES]:
            students.append((row[ID], extract_degree(row[ALL_DEGREES])))
    write_csv(args.outfile, students)


if __name__ == '__main__':
    main()
