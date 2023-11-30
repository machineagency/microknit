from py.silversend import Silversend


print("we can do things and we're starting")

s = Silversend(-20, 20)

pattern = [False, True, False, False] * 10
s.load(pattern)

while True:
    s.update()
