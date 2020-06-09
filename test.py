s = "daslakndlaaaaajnjndibniaaafijdnfijdnsijfnsdinifaaaaaaaaaaafnnasm"
print(s)
a_len = len(s)
found_a_len = 0
keep_going = True
while a_len>0 and keep_going:
    aas = "a" * a_len
    if aas in s:
        found_a_len = a_len
        keep_going = False
    a_len=a_len -1
print ("max length of a:" , found_a_len)
"""
keep_going = True
while keep_going:
    s=s.replace("aaa","aa")
    if "aaa" not in s:
        keep_going = False
print(s)
"""