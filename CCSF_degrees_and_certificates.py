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
    If there are no CSV files in the folder this will do nothing.
    If there is more than one CSV file it will pick the first one it finds that
    doesn't have the same name as args.outfile (which is defaulted to
    "00-CCSF_Degrees_and_Certificates.csv").
    You may specify the name of the RST file and/or the name of the new file if
    you run from terminal.

For running from terminal help:
    Run 'python CCSF_degrees_and_certificates.py -h'
"""


def parse_args():
    p = argparse.ArgumentParser(description="Extract degrees/certificates.")
    p.add_argument("infile", help="Name of input file", nargs='?')
    p.add_argument(
        "outfile", help="Name of output file.",
        default="00-CCSF_Degrees_and_Certificates.csv", nargs='?'
    )
    args = p.parse_args()
    return args


def read_cnv(infile, outfile):
    if not infile:
        print "Searching for CSV file"
        for filename in os.listdir("./"):
            if (os.path.splitext(filename)[1] == ".csv" and
                    filename != outfile):
                print "Found: " + filename
                infile = filename
                break

    print "Opening: " + infile
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
    header_row, rows = read_cnv(args.infile, args.outfile)
    ID = header_row.index("StudentId")
    ALL_DEGREES = header_row.index("All_DegreesEarned_Code")
    students = [("STUDENT_ID", "DEGREE_EARNED")]
    for row in rows:
        if row[ALL_DEGREES]:
            students.append((row[ID], extract_degree(row[ALL_DEGREES])))
    write_csv(args.outfile, students)


if __name__ == '__main__':
    main()
