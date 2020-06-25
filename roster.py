from sys import argv, exit
import sqlite3

# Check command-line arguments
if len(argv) != 2:
    print("Usage: python roster.py house")
    exit(1)

# Query db for all students in house
sqliteConnection = sqlite3.connect('students.db')
db = sqliteConnection.cursor()

db.execute("SELECT first, middle, last, birth FROM students WHERE house = ? ORDER BY last, first", (argv[1],))

reader = db.fetchall()

# Print out each student's full name and birth year
for row in reader:
    if row[1] != None:
        print(f"{row[0]} {row[1]} {row[2]}, born {row[3]}")
    else:
        print(f"{row[0]} {row[2]}, born {row[3]}")