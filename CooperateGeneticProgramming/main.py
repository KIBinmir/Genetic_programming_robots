import random
import sys, pygame
from pygame.locals import *
import math
import enum
import random
import copy

colors = {"black": (0,0,0), "white": (255, 255, 255), "red": (250, 0, 0),
              "green": (0, 250, 0), "blue": (0,0,250)}

pygame.font.init()
font = pygame.font.SysFont("Comic Sans MS", 20)
def drawText(screen, str, x,y):
    surf = font.render(str,False, (0,0,0))
    screen.blit(surf,(x,y))

class TypeCells(enum.IntEnum):
    FREE = 0
    OBSTACLE = -1
    GOAL1 = 1
    GOAL2 = 2
    GOAL3 = 3

def distAbs(x1, y1, x2, y2):
    return abs(x2 - x1) + abs(y2 - y1)
class Cell:

    width, height = 50, 50


    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.V = 0
        self.w = Cell.width
        self.h = Cell.height
        self.typeCell = TypeCells.FREE
        self.isRobot = False
        self.robotNum = 0

    def draw(self, screen):
        rect = ((self.x + self.w / 2), (self.y + self.h / 2), self.w, self.h)
        pygame.draw.rect(screen, colors["black"], rect, 2)
        if self.typeCell: pygame.draw.circle(screen, (0,0,0), (self.x, self.y), 3, 2)
        # drawText(screen, str(round(self.V)), (self.x + self.w / 2), (self.y + self.h / 2))
        #for c in self.neighbours:
        #    pygame.draw.line(screen, (255,0,0), ((self.x + self.w), (self.y + self.h)),
        #                     ((c.x + c.w), (c.y + c.h)))

class Table:
    colorCells = {"black": (0, 0, 0), "white": (255, 255, 255)}
    colorRobots = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255)}
    def __init__(self, nRow, nColumn, w, h):
        self.nRow = nRow
        self.nColumn = nColumn
        self.width = w
        self.height = h
        self.obstacles = []
        self.cells = [[TypeCells.FREE for i in range(nColumn)] for j in range(nRow)]
        self.goals = [None, None, None]
        self.robots = [None, None, None]
        self.startPositionRobots = [None, None, None]

    def draw(self, screen):
        # rect = (0, 0, self.width, self.height)
        # pygame.draw.rect(screen, colors["black"], rect, 2)
        kw = self.width // self.nColumn
        kh = self.height // self.nRow

        colR = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        colG = [(192, 0, 0), (0, 192, 0), (0, 0, 192)]

        for o in self.obstacles:
            row, column = o
            pygame.draw.rect(screen, colors["black"], [column*kw, row*kh, kw, kh])

        for i in range(3):
            if self.goals[i] != None:
                self.goals[i].draw(screen, colG[i])

        for j in range(3):
            if self.robots[j] != None:
                self.robots[j].draw(screen, colR[j])


        # Рисуем линии, разделяющие строки таблицы
        for i in range(0, self.nRow+1):
            pygame.draw.line(screen, colors["black"], [0, i*kh], [self.width, i*kh], 2)

        # Рисуем линии, разделяющие столбцы таблицы
        for j in range(0, self.nColumn + 1):
            pygame.draw.line(screen, colors["black"], [j*kw, 0], [j*kw, self.height], 2)




    def setObstacle(self, row, column):
        self.cells[row][column] = TypeCells.OBSTACLE
        self.obstacles.append((row, column))

    def setObstacles(self, lst):
        for el in lst:
            self.setObstacle(el[0], el[1])

    def setBlockObsctacles(self, row, column, nRow, nColumn):
        for r in range(row, row + nRow):
            for c in range(column, column + nColumn):
                self.setObstacle(r, c)

    def setRobot(self, robot, row, column, ind):
        if self.robots[ind] is not None:
            r, c = self.robots[ind].getPos()
            self.cells[r][c] = TypeCells.FREE
        self.robots[ind] = robot
        robot.setPos(row, column)
        self.startPositionRobots[ind] = (row, column)

    def setGoal(self, goal, row, column, ind):
        if self.goals[ind] is not None:
            r, c = self.goals[ind].getPos()
            self.cells[r][c] = TypeCells.FREE
        self.goals[ind] = goal
        if ind == 0:
            self.cells[row][column] = TypeCells.GOAL1
        elif ind == 1:
            self.cells[row][column] = TypeCells.GOAL2
        elif ind == 2:
            self.cells[row][column] = TypeCells.GOAL3

    def isCollisionRobots(self, i, j):
        r1, r2 = self.robots[i], self.robots[j]
        row1, column1 = r1.getPos()
        row2, column2 = r2.getPos()
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

    def isCollisionRobots3(self):
        return self.isCollisionRobots(0, 1) or self.isCollisionRobots(1, 2) or self.isCollisionRobots(0, 2)

    def move3(self, com):
        for i in range(3):
            self.robots[i].move(com[i])
            if self.isObstacleCollision(i):
                if self.robots[i].state == Robot.States.MOVED_UP:
                    self.robots[i].row += 1
                elif self.robots[i].state == Robot.States.MOVED_DOWN:
                    self.robots[i].row -= 1
                elif self.robots[i].state == Robot.States.MOVED_LEFT:
                    self.robots[i].column += 1
                elif self.robots[i].state == Robot.States.MOVED_RIGHT:
                    self.robots[i].column -= 1

    def isObstacleCollision(self, ind):
        r1, c1 = self.robots[ind].getPos()
        return self.cells[r1][c1] == TypeCells.OBSTACLE

    def isObstacleCollision3(self):
        flag = False
        for i in range(3):
            flag = flag or self.isObstacleCollision(i)

        return flag

    def returnRobotsToStartPosition(self):
        for ind in range(3):
            self.robots[ind].setPos(*(self.startPositionRobots[ind]))
            self.robots[ind].state = Robot.States.STAYED

    def isGoal(self, ind):
        rowR, colR = self.robots[ind].getPos()
        rowG, colG = self.goals[ind].getPos()
        return (rowR == rowG) and (colR == colG)

    def isGoal3(self):
        flag = True
        for i in range(3):
            flag = flag and self.isGoal(i)

        return flag

class Goal:
    colors = {"red": (250, 0, 0), "green": (0, 250, 0), "blue": (0, 0, 250)}
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def draw(self, screen, color=colors["red"]):
        x = self.column*50
        y = self.row*50
        pygame.draw.rect(screen, color, [x, y, 50, 50])

    def getPos(self):
        return (self.row, self.column)

class Robot:
    class Moving(enum.IntEnum):
        UP = 4
        DOWN = 3
        RIGHT = 2
        LEFT = 1
        STAY = 0

    class States(enum.IntEnum):
        MOVED_UP = 5
        MOVED_DOWN = 4
        MOVED_RIGHT = 3
        MOVED_LEFT = 2
        STAYED = 1

    def __init__(self, row, column):
        self.row = row
        self.column = column
        # self.sensors = [[TypeCells.OBSTACLE for i in range(3)] for j in range(3)]
        self.state = Robot.States.STAYED

    def draw(self, screen, color=colors["red"]):
        x = self.column*50 + 26
        y = self.row*50 + 26
        pygame.draw.circle(screen, color, [x, y], 22)
        pygame.draw.circle(screen, (0, 0, 0), [x, y], 22, 2)

    def move(self, comand):
        match comand:
            case Robot.Moving.UP:
                self.row -= 1
                self.state = Robot.States.MOVED_UP
            case Robot.Moving.DOWN:
                self.row += 1
                self.state = Robot.States.MOVED_DOWN
            case Robot.Moving.LEFT:
                self.column -= 1
                self.state = Robot.States.MOVED_LEFT
            case Robot.Moving.RIGHT:
                self.column += 1
                self.state = Robot.States.MOVED_RIGHT
            case Robot.Moving.STAY:
                self.state = Robot.States.STAYED

    def getPos(self):
        return (self.row, self.column)

    def setPos(self, row, column):
        self.column, self.row = column, row


class GP:
    def __init__(self, sizePopulation, minSizeIndivid, maxSizeIndivid, chanceMutation = 0.2, chanceCrossover= 0.8):
        self.numberPopulation = 0
        self.sizePopulation = sizePopulation
        self.maxSizeIndivid = maxSizeIndivid
        self.minSizeIndivid = minSizeIndivid
        self.chanceMutation = chanceMutation
        self.chanceCrossover = chanceCrossover
        self.population = []
        self.parents = []
        self.children = []
        self.otherHalfPopulation = []
        self.fitnessPopulation = []
        self.sumFitnessPopulation = []
        self.meanFitnessPopulation = []
        self.maxFitnessPopulation = []
        self.minFitnessPopulation = []
        self.isGoal3 = False
        #self.maxSizePartCode = 5

    def initial_population(self, sizePopulation, minSizeIndivid, maxSizeIndivid):
        self.population = [Individ(maxSizeIndivid, minSizeIndivid) for i in range(self.sizePopulation)]
        for i in self.population:
            i.createProgramm(False)
        self.numberPopulation = 1

    def initial_population2(self, sizePopulation, minSizeIndivid, maxSizeIndivid):
        self.population = [Individ(maxSizeIndivid, minSizeIndivid) for i in range(self.sizePopulation)]
        for i in self.population:
            i.createProgramm2(minSizeIndivid)
        self.numberPopulation = 1

    def crossoverOnePoint(self, individ1, individ2):
        point = random.randint(1, min(individ1.size, individ2.size)-1)
        n1 = individ1.prog[:point] + individ2.prog[point:]
        n2 = individ2.prog[:point] + individ1.prog[point:]
        return (Individ(self.maxSizeIndivid, n1, len(n1)), Individ(self.maxSizeIndivid, n2, len(n2)))

    def crossoverTwoPoint(self, individ1, individ2):
        point1 = random.randint(1, min(individ1.size, individ2.size) - 1)
        point2 = random.randint(1, min(individ1.size, individ2.size) - 1)
        if point1 > point2:
            point1, point2 = point2, point1
        elif point1 == point2:
            point2 = random.randint(point1, min(individ1.size, individ2.size) - 1)
        n1 = individ1.prog[:point1] + individ2.prog[point1:point2] + individ1.prog[point2:]
        n2 = individ2.prog[:point2] + individ1.prog[point1:point2] + individ2.prog[point2:]
        return (Individ(self.maxSizeIndivid, n1, len(n1)), Individ(self.maxSizeIndivid, n2, len(n2)))

    def crossoverTwoPointAndSize(self, individ1, individ2, sizePartCode=7):
        sizePart = random.randint(1, sizePartCode)
        p1left = random.randint(0, individ1.size - sizePart)

        p2left = random.randint(0, individ2.size - sizePart)
        p1right = p1left + sizePart
        p2right = p2left + sizePart
        n1 = individ1.prog[:p1left] + individ2.prog[p2left:p2right] + individ1.prog[p1right:]
        n2 = individ2.prog[:p2left] + individ1.prog[p1left:p1right] + individ2.prog[p2right:]
        minsize = self.minSizeIndivid
        maxsize = self.minSizeIndivid
        return (Individ(minsize, maxsize, n1, len(n1)), Individ(minsize, maxsize, n2, len(n2)))

    def crossoverUniversal(self, individ1, individ2):
        l1 = random.randint(0, individ1.size-1)
        r1 = random.randint(l1+1, min(l1+5,individ1.size))
        l2 = random.randint(0, individ2.size-1)
        r2 = random.randint(l2+1, min(l2+5,individ2.size))
        n1 = individ1.prog[:l1] + individ2.prog[l2:r2] + individ1.prog[r1:]
        n2 = individ2.prog[:l2] + individ1.prog[l1:r1] + individ2.prog[r2:]
        size = self.maxSizeIndivid
        n1 = n1[:size]
        n2 = n2[:size]
        return (Individ(size, n1, len(n1)), Individ(size, n2, len(n2)))

    def crossoverPopulation(self, population):
        lst = []
        for i in range(0, len(population), 2):
            n1, n2 = self.crossoverTwoPointAndSize(population[i], population[i+1], 5)
            lst.append(n1)
            lst.append(n2)
        return lst


    def mutationComand(self, individ):
        cm = [Robot.Moving.STAY,
              Robot.Moving.UP,
              Robot.Moving.LEFT,
              Robot.Moving.DOWN,
              Robot.Moving.RIGHT]
        numberComand = random.randint(0, individ.size - 1)
        numberRobot = random.randint(0, 2)
        choiceComand = random.choice(cm)
        individ.prog[numberComand][numberRobot] = choiceComand

    def mutationReplace(self, individ):
        cm = [Robot.Moving.STAY,
              Robot.Moving.UP,
              Robot.Moving.LEFT,
              Robot.Moving.DOWN,
              Robot.Moving.RIGHT]
        numberComand = random.randint(0, individ.size - 1)
        individ.prog[numberComand] = [random.choice(cm), random.choice(cm), random.choice(cm)]


    def mutationInsert(self, individ):
        if individ.size < self.maxSizeIndivid:
            cm = [Robot.Moving.STAY,
                  Robot.Moving.UP,
                  Robot.Moving.LEFT,
                  Robot.Moving.DOWN,
                  Robot.Moving.RIGHT]
            numberComand = random.randint(0, individ.size - 1)
            individ.prog.insert(numberComand, [random.choice(cm), random.choice(cm), random.choice(cm)])
            individ.size += 1

    def mutationDelete(self, individ):
        if individ.size > self.minSizeIndivid:
            cm = [Robot.Moving.STAY,
                  Robot.Moving.UP,
                  Robot.Moving.LEFT,
                  Robot.Moving.DOWN,
                  Robot.Moving.RIGHT]
            numberComand = random.randint(0, individ.size - 1)
            individ.prog.pop(numberComand)
            individ.size -= 1

    def mutationPopulation(self, population, propability=0.2, chanceMC = 0.4, chanceMR = 0.3, chanceMI=0.2, chanceMD=0.1):
        for i in range(len(population)):
            if random.random() <= propability:
                for j in range(random.randint(1, 2)):
                    chance = random.random()
                    if chance < chanceMD:
                        self.mutationDelete(population[i])
                    elif chance < chanceMI + chanceMD:
                        self.mutationInsert(population[i])
                    elif chance < chanceMR + chanceMI + chanceMD:
                        self.mutationReplace(population[i])
                    else:
                        self.mutationComand(population[i])

    def calculateFitnessPopulation(self, table):
        sumFitnessPopulation = 0
        maxFitnessPopulation = -1
        minFitnessPopulation = 1000000
        self.isGoal3 = False
        for i in range(self.sizePopulation):
            self.population[i].calculateFitness(table)
            # self.fitnessPopulation = self.population[i].fitness
            sumFitnessPopulation += self.population[i].fitness
            maxFitnessPopulation = max(maxFitnessPopulation, self.population[i].fitness)
            minFitnessPopulation = min(minFitnessPopulation, self.population[i].fitness)
            self.isGoal3 = self.isGoal3 or self.population[i].isGoal3

        meanFitnessPopulation = sumFitnessPopulation/self.sizePopulation
        self.maxFitnessPopulation.append(maxFitnessPopulation)
        self.minFitnessPopulation.append(minFitnessPopulation)
        self.sumFitnessPopulation.append(sumFitnessPopulation)
        self.meanFitnessPopulation.append(meanFitnessPopulation)

    def selectionTournament(self, population):
        #lst = random.sample(population, len(population))
        lst = sorted(population, key=lambda x: x.fitness)
        winners = []
        losers = []
        for i in range(0, len(lst), 2):
            if lst[i].fitness < lst[i + 1].fitness:
                winners.append(lst[i])
                losers.append(lst[i + 1])
            else:
                winners.append(lst[i+1])
                losers.append(lst[i])

        return winners, losers

    def selectionRang(self, population, numParents=2):
        winners = []
        losers = []
        lst = sorted(population, key= lambda x: x.fitness)
        rangs = [i*i for i in range(self.sizePopulation, 0,-1)]
        sum_rangs = sum(rangs)
        probe = [k / sum_rangs for k in lst]
        spin = [sum(probe[:i]) for i in range(1, len(probe) + 1)]
        chosed = [False for i in range(self.sizePopulation)]
        for k in range(numParents):
            arrow = random.random()
            for i in range(len(spin)):
                if arrow < spin[i]:
                    winners.append(lst[i])
                    break
        return winners

    def sim(self, table):
        if self.numberPopulation == 0:
            self.initial_population(self.sizePopulation, self.minSizeIndivid, self.maxSizeIndivid)
        self.calculateFitnessPopulation(table)
        if not self.isGoal3:
            self.parents, self.children = self.selectionTournament(self.population)
            self.children = self.crossoverPopulation(self.parents)
            self.mutationPopulation(self.children, propability=self.chanceMutation)
            self.population = self.parents + self.children
            self.numberPopulation += 1

    def sim2(self, table):
        if self.numberPopulation == 0:
            self.initial_population2(self.sizePopulation, self.minSizeIndivid, self.maxSizeIndivid)
        self.calculateFitnessPopulation(table)
        if not self.isGoal3:
            self.parents = copy.copy(self.population[0])
            self.children = copy.copy(self.parents)
            probeInsert = 0.1
            if random.random() < probeInsert and self.children.size < self.maxSizeIndivid:
                self.children.appendRandomComand()
            else:
                self.mutationReplace(self.children)
            self.children.calculateFitness(table)
            if self.children.fitness < self.parents.fitness:
                self.population[0]=copy.copy(self.children)
            self.numberPopulation += 1


class Individ:
    def __init__(self, maxSize, minSize=0, code=None, size=0):
        self.maxSize = maxSize
        self.minSize = minSize
        self.prog = code
        self.fitness = 100
        self.size = size
        self.isGoal3 = False

    def createProgramm(self, randomSize = False, size=None):
        cm = [Robot.Moving.STAY,
              Robot.Moving.UP,
              Robot.Moving.LEFT,
              Robot.Moving.DOWN,
              Robot.Moving.RIGHT]
        if not randomSize and size != None:
            self.size = min(size, self.maxSize)
        else:
            self.size = random.randint(self.minSize, self.maxSize)
        self.prog = []
        for i in range(self.size):
            self.prog.append([random.choice(cm), random.choice(cm), random.choice(cm)])

    def createProgramm2(self, size, prog = None):
        if prog is None:
            self.prog = []
            for i in range(size):
                self.appendRandomComand()
                self.size += 1
        else:
            self.prog = prog
            self.size = size

    def appendRandomComand(self):
        cm = [Robot.Moving.STAY,
              Robot.Moving.UP,
              Robot.Moving.LEFT,
              Robot.Moving.DOWN,
              Robot.Moving.RIGHT]
        self.prog.append([random.choice(cm), random.choice(cm), random.choice(cm)])
        self.size += 1

    def calculateFitness(self, table):
        table.returnRobotsToStartPosition()
        self.fitness = 100
        k= 0
        for p in self.prog:
            k += 1
            table.move3(p)
            self.fitness += 10
            if table.isCollisionRobots3():
                self.fitness += 30000

            for i in range(3):
                if table.isGoal(i):
                    self.fitness -= 3

            if table.isGoal3():
                self.isGoal3 = True
                self.fitness = 0
                self.prog = self.prog[:k]
                break

        for i in range(3):
            self.fitness += 200*distAbs(*table.robots[i].getPos(),*table.goals[i].getPos())
        table.returnRobotsToStartPosition()

    def messageComand(self):
        s = ""
        cmd = Robot.Moving
        str_comand = {cmd.UP: "UP", cmd.DOWN: "DOWN", cmd.RIGHT: "RIGHT", cmd.LEFT: "LEFT", cmd.STAY: "STAY"}
        for c in self.prog:
            s += "move"+str(self.numberRobots)+"("+", ".join(c)+")"+"\n"
        for com in Robot.Moving:
            s.replace(str(com), str_comand[com])
        return s

def main():
    sz=(800, 600)
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    r = 10; x = 130; y = 130;
    fps = 30
    table = Table(12,12,600,600)

    robot1 = Robot(1, 1)
    robot2 = Robot(1, 10)
    robot3 = Robot(10, 6)
    table.setRobot(robot1, *(robot1.getPos()), 0)
    table.setRobot(robot2, *(robot2.getPos()), 1)
    table.setRobot(robot3, *(robot3.getPos()), 2)

    goal1 = Goal(10, 10)
    goal2 = Goal(10, 1)
    goal3 = Goal(1, 5)
    table.setGoal(goal1, *goal1.getPos(),0)
    table.setGoal(goal2, *goal1.getPos(), 1)
    table.setGoal(goal3, *goal1.getPos(), 2)

    # Препятствия вокруг поля
    table.setBlockObsctacles(0, 0, 1, 12)
    table.setBlockObsctacles(11, 0, 1, 12)
    table.setBlockObsctacles(1, 0, 10, 1)
    table.setBlockObsctacles(1, 11, 10, 1)

    # Остальные препятствия
    table.setBlockObsctacles(2, 1, 1, 4)
    table.setBlockObsctacles(2, 6, 1, 5)
    table.setBlockObsctacles(9, 1, 1, 5)
    table.setBlockObsctacles(9, 7, 1, 4)
    table.setBlockObsctacles(3, 7, 4, 1)
    table.setBlockObsctacles(6, 8, 1, 2)
    table.setBlockObsctacles(5, 4, 4, 1)
    table.setBlockObsctacles(5, 2, 1, 2)


    genProg = GP(1, 1, 20, chanceMutation=1.0)
    while genProg.numberPopulation < 1000 and genProg.isGoal3 == False:
        genProg.sim2(table)

    print(genProg.population[0].fitness)
    print(genProg.population[0].size, len(genProg.population[0].prog))
    lst = genProg.population[0].prog
    k = 0
    for el in lst:
        print(el)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    table.returnRobotsToStartPosition()
                    k = 0
                if event.key == pygame.K_p:
                    if k < len(lst):
                        table.move3(lst[k])
                        k += 1

        screen.fill( (255,255,255) )
        x += 1
        y += 1
        table.draw(screen)

        pygame.display.flip()
        timer.tick(fps)


if __name__ == '__main__':
    main()