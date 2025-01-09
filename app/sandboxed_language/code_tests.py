from main import main_loop
from singleton import realm

realm.MODE = "test"

main_loop(steps=5)

code = """

a = "a"
b = "b"
x = 1
z = {'x':1,'y':3}

#s = find_nearest(8, 2,'Cow')
m = get_index(z,'x')

if (x < 10 ):
    y = x + (x*2)
    
    if x==1:
        a = 3
else:
    y = 20

c = 'c'

"""

# print(eval_math('3 == 0'))
evaluate_code(code)
