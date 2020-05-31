from cs50 import get_float
import math

while True:
    change = get_float("Changed owed: ")
    if change > 0:
        break

c = change * 100
q = math.floor(c / 25)
d = math.floor(c % 25 / 10)
n = math.floor(c % 25 % 10 / 5)
p = math.floor(c % 25 % 10 % 5)
print(q + d + n + p)