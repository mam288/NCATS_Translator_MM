
a = [1]
b = [2,2]
c = [3,3,3]
d = [4,4]
e= [5]
f = [6,6,6]
lp = [(a, b),(b,c ),(c, d),(d, e),(e, f)]
l = [a, b, c]

for ke1, ke2 in lp:
    print(ke1)
    print(ke2)
    for e in ke1:
        print(e)
        for e2 in ke2:
            print(e2)

for i, ke in enumerate(l):
    for e in ke:
        print (e)
    if i < len(l)-1:
        for f in l[i + 1]:
            print (e, f)