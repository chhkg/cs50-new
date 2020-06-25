from cs50 import SQL
import csv
from sys import argv, exit

# Check command-line arguments
if len(argv) != 2:
    print("Usage: python import.py characters.csv")
    exit(1)

db = SQL("sqlite:///students.db")

# Open csv file
with open("characters.csv", "r") as characters:
    reader = csv.DictReader(characters)

    # Parse name for each row
    for row in reader:
        namesplit = row["name"].split()
        if len(namesplit) == 3:
            db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES(?, ?, ?, ?, ?)",
                       namesplit[0], namesplit[1], namesplit[2], row["house"], row["birth"])
        else:
            db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES(?, ?, ?, ?, ?)",
                       namesplit[0], None, namesplit[1], row["house"], row["birth"])