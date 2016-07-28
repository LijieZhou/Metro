import os
import argparse
import operator
import csv


def main():
    p = argparse.ArgumentParser(description="Golden Four grade.")
    p.add_argument("infile", help="Name of RST raw file", nargs='?')
    p.add_argument("outfile", help="Name of the created file.",
                   default="00-Golden_Four_Grade.csv", nargs='?')
    args = p.parse_args()

    if not args.infile:
        print("Searching for CSV file")
        for filename in os.listdir("./"):
            is_csv = os.path.splitext(filename)[1] == ".csv"
            if is_csv and filename != args.outfile:
                print("Found: " + filename)
                args.infile = filename
                break

    print("Opening: " + args.infile)
    with open(args.infile) as f:
        raw_rows = [row for row in csv.reader(f.read().splitlines())]

    header_row = raw_rows[0]
    rows = raw_rows[1:]

    # Sort rows by Id then SubjAreaCode then CrseNo then Grde_Code_Final
    print("Sorting rows by Id then SubjAreaCode then CrseNo "
          "then Grde_Code_Final")
    ID = header_row.index("Id")
    SUBJECT = header_row.index("SubjAreaCode")
    COURSE_NUMBER = header_row.index("CrseNo")
    GRADE = header_row.index("Grde_Code_Final")
    rows.sort(key=operator.itemgetter(ID, SUBJECT, COURSE_NUMBER, GRADE))

    # Filter out any duplicates
    # Since we sorted by grade, we know the first occurrence of
    # (ID, SUBJECT, COURSE_NUMBER) is going to have the highest grade
    print("Filtering out duplicates (keeping the highest grade)")
    prev_row = rows[0]
    filtered_rows = [prev_row]
    for row in rows:
        same_id_as_prev = row[ID] == prev_row[ID]
        same_subject_as_prev = row[SUBJECT] == prev_row[SUBJECT]
        same_course_as_prev = row[COURSE_NUMBER] == prev_row[COURSE_NUMBER]
        duplicate_of_prev = (same_id_as_prev and
                             same_subject_as_prev and
                             same_course_as_prev)
        if not duplicate_of_prev:
            filtered_rows.append(row)
        prev_row = row

    # Create filtered csv file
    print("Creating filtered RST Query for enrollments: " + args.outfile)
    csv_lines = [header_row] + filtered_rows
    with open(args.outfile, 'wb') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(csv_lines)

    print("DONE")


if __name__ == '__main__':
    main()
