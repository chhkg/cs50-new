import csv
import sys
from sys import argv, exit

# check if user provide correcnt command
if len(argv) != 3:
    print("Usage: python dna.py data.csv sequence.txt")
    exit(1)

# read databases csv into memory, use reader / DictReader
with open(argv[1], newline='') as csvfile:
    reader = list(csv.reader(csvfile))

# read dna sequences into memory, use sys.argv
with open(argv[2], "r") as s_file:
    dna = s_file.read()

# check max count of STR, reference: https://stackoverflow.com/questions/18776238/count-the-number-of-max-consecutive-as-from-a-string-python-3
STR_max_list = []
for i in range(len(reader[0]) - 1):
    len_STR = len(reader[0][i + 1])
    count = round(len(dna) / len_STR)
    max_count = 0
    keep_going = True
    while count > 0 and keep_going:
        checker = reader[0][i + 1] * count
        if checker in dna:
            max_count = count
            keep_going = False
        count -= 1
    STR_max_list.append(max_count)

# check if each STR count matches each row in the databases file
match = False
for r in range(len(reader) - 1):
    # turn list of string to list of int, reference: https://www.geeksforgeeks.org/python-converting-all-strings-in-list-to-integers/
    if [int(i) for i in reader[r + 1][1:]] == STR_max_list:
        print(reader[r + 1][0])
        match = True
        break

if match == False:
    print("No match")