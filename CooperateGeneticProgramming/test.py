import random
from main import Robot

def test1():
    lst1 = [0, 1, 2, 3, 4]
    lst2 = [5, 6, 7, 8, 9]
    l1 = 0
    r1 = 5
    l2 = 0
    r2 = 4
    print(lst1[:l1]+lst2[l2:r2]+lst1[r1:])
    print(lst2[:l2] + lst1[l1:r1] + lst2[r2:])

def test2():
    i = random.randint(0, 5)
    k = 0
    while i != 0 and k < 1000:
        i = random.randint(0, 5)
        k += 1
    print(i, k)

def test3():
    lst1 = [0, 1, 2, 3, 4]
    print(lst1[:10])

def test4():
    row1, = 2

    if row1 == row2 and column1 == column2:
        return True
    elif column1 == column2 and row1 - row2 == 1:
        if r1.state == Robot.States.MOVED_DOWN and r2.state == Robot.States.MOVED_UP:
            return True
        else:
            return False
    elif column1 == column2 and row1 - row2 == -1:
        if r1.state == Robot.States.MOVED_UP and r2.state == Robot.States.MOVED_DOWN:
            return True
        else:
            return False
    elif row1 == row2 and column1 - column2 == 1:
        if r1.state == Robot.States.MOVED_RIGHT and r2.state == Robot.States.MOVED_LEFT:
            return True
        else:
            return False
    elif row1 == row2 and column1 - column2 == -1:
        if r1.state == Robot.States.MOVED_LEFT and r2.state == Robot.States.MOVED_RIGHT:
            return True
        else:
            return False
    else:
        return False
if __name__ == "__main__":
    test3()