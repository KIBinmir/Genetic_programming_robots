import random
import copy
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
    lst = [1, 2, 3, 4, 5]
    lst.insert(3, 7)
    print(lst)

def test5():
    lst = [1, 2, 3, 4, 5]
    lst.pop(2)
    print(lst)

def test6():
    print([i for i in range(6,0,-1)])

def test7():
    print(sorted([i for i in range(6,0,-1)]))

def test8():
    lst = [i*i for i in range(6,0,-1)]
    sm = sum(lst)
    probe = [k/sm for k in lst]
    spin = [sum(probe[:i]) for i in range(1, len(probe)+1)]
    print(spin)
    print(probe)
    arrow = random.random()
    for i in range(len(spin)):
        if arrow < spin[i]:
            print(lst[i])
            break

def test9():
    class Example:
        def __init__(self, fitness):
            self.fitness = fitness

    lst = [Example(i) for i in range(10)]
    lst = random.sample(lst, len(lst))
    lst = sorted(lst, key= lambda x: x.fitness)
    print(lst[5].fitness)

def test10():
    class Example:
        def __init__(self, fitness):
            self.fitness = fitness

    ex1 = Example(100)
    ex2 = copy.copy(ex1)
    ex3 = ex1
    ex1.fitness = 1
    ex2.fitness = 500

    print(ex1.fitness, ex2.fitness, ex3.fitness)

if __name__ == "__main__":
    test10()