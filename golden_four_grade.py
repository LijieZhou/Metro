import os
import argparse
import operator
import csv



def main():
	p = argparse.ArgumentParser (description="Golden Four grade.")
	p.add_argument("infile", help="Name of RST raw file", nargs='?')
	p.add_argument("outfile", help="Name of the created file.", default="00-Golden_Four_Grade.csv", nargs='?')
	
	args = p.parse_args()

	if not args.infile:
		print "Searching for CSV file"
		for filename in os.listdir("./"):
			if os.path.splitext(filename)[1] == ".csv" and filename != args.outfile:
				print "Found: " + filename
				args.infile = filename
				break

	print "Opening: " + args.infile
	with open(args.infile) as f:
		raw_rows = [row for row in csv.reader(f.read().splitlines())]

	header_row = raw_rows[0]
	rows = raw_rows[1:]

	# Sort rows by Id then by SubjAreaCode then by CrseNo then by Grde_Code_Final
	print "Sorting rows by Id then by SubjAreaCode then by CrseNo then Grde_Code_Final"
	# header_row.index("Id") will return the index of the "Id" column which can in turn be used to sort "rows" by SubjAreaCode,CrseNo,and Grde_Code_Final 
	rows.sort(key=operator.itemgetter(header_row.index("Id"), header_row.index("SubjAreaCode"), header_row.index("CrseNo"), header_row.index("Grde_Code_Final") ))

	# Filters out rows whose level field is not Golden4
	# print "Filtering out Post Bachelor rows"
	# rows = [row for row in rows if row[header_row.index("Level")] != "Golden4"]

	# Filter out any duplicates
	print "Filtering out duplicates"
	filtered_rows = []
	for row_num in xrange(len(rows)):
		same_id_as_next = row_num != len(rows) - 1 and rows[row_num][header_row.index("Id")] == rows[row_num + 1][header_row.index("Id")]
		same_subjAreaCode_as_next = row_num != len(rows) - 1 and rows[row_num][header_row.index("SubjAreaCode")] == rows[row_num + 1][header_row.index("SubjAreaCode")]
		same_CrseNo_as_next = row_num != len(rows) - 1 and rows[row_num][header_row.index("CrseNo")] == rows[row_num + 1][header_row.index("CrseNo")]
		same_Grde_Code_Final = row_num != len(rows) - 1 and rows[row_num][header_row.index("Grde_Code_Final")] == rows[row_num + 1][header_row.index("Grde_Code_Final")]
		if same_id_as_next and same_subjAreaCode_as_next and same_CrseNo_as_next and same_Grde_Code_Final:
	    # if (row_num not in same_id_as_next) and (row_num not in same_subjAreaCode_as_next) and (row_num not in same_CrseNo_as_next):
	    	filtered_rows.append(raw_rows-rows[row_num])
			# filtered_rows.append(rows[row_num])

		

	# Create filtered csv file
	print "Creating filtered RST Query for enrollments: " + args.outfile
	csv_lines = [header_row] + filtered_rows
	with open(args.outfile, 'wb') as f:
		csv_writer = csv.writer(f)
		csv_writer.writerows(csv_lines)


	print "DONE"


if __name__ == '__main__':
	main()
