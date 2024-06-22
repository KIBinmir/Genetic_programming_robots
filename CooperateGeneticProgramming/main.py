import random
import sys, pygame
from pygame.locals import *
import math
import enum
import random

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

        for i in range(3):
            if self.goals[i] != None:
                self.goals[i].draw(screen, colG[i])

        for j in range(3):
            if self.robots[j] != None:
                self.robots[j].draw(screen, colR[j])

        for o in self.obstacles:
            row, column = o
            pygame.draw.rect(screen, colors["black"], [column*kw, row*kh, kw, kh])

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
        else:
            self.cells[row][column] = TypeCells.GOAL3

    def isCollisionRobots(self, i, j):
        r1, r2 = self.robots[i], self.robots[j]
        y1, x1 = r1.getPos()
        y2, x2 = r2.getPos()
        if x1 == x1 and y1 == y2:
            return True
        elif x1 == x2 and y1 - y2 == 1:
            if r1.state == Robot.States.MOVE_UP and r2.state == Robot.States.MOVE_DOWN:
                return True
        elif x1 == x2 and y1 - y2 == -1:
            if r1.state == Robot.States.MOVE_DOWN and r2.state == Robot.States.MOVE_UP:
                return True
        elif y1 == y2 and x1 - x2 == 1:
            if r1.state == Robot.States.MOVE_LEFT and r2.state == Robot.States.MOVE_RIGHT:
                return True
        elif y1 == y2 and x1 - x2 == -1:
            if r1.state == Robot.States.MOVE_RIGHT and r2.state == Robot.States.MOVE_LEFT:
                return True

        return False

    def isCollisionRobots3(self):
        return self.isCollisionRobots(0, 1) or self.isCollisionRobots(1, 2) or self.isCollisionRobots(0, 2)

    def move3(self, com):
        for i in range(3):
            self.robots[i].move(com[i])

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
        self.ind = 0

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
        MOVE_UP = 5
        MOVE_DOWN = 4
        MOVE_RIGHT = 3
        MOVE_LEFT = 2
        STAY = 1
        AT_START = 0
        REACHED_GOAL = 6

    def __init__(self, row, column):
        self.row = row
        self.column = column
        # self.sensors = [[TypeCells.OBSTACLE for i in range(3)] for j in range(3)]
        self.state = Robot.States.STAY
        self.comand = Robot.Moving.STAY

    def draw(self, screen, color=colors["red"]):
        x = self.column*50 + 26
        y = self.row*50 + 26
        pygame.draw.circle(screen, color, [x, y], 22)
        pygame.draw.circle(screen, (0, 0, 0), [x, y], 22, 2)

    def move(self, comand):
        match comand:
            case Robot.Moving.UP:
                self.row -= 1
                self.state = Robot.States.MOVE_UP
            case Robot.Moving.DOWN:
                self.row += 1
                self.state = Robot.States.MOVE_DOWN
            case Robot.Moving.LEFT:
                self.column -= 1
                self.state = Robot.States.MOVE_LEFT
            case Robot.Moving.RIGHT:
                self.column += 1
                self.state = Robot.States.MOVE_RIGHT


    """def sense(self, table):
        for r in range(self.row - 1, self.row + 2):
            for c in range(self.row - 1, self.row + 2):
                if r == self.row and c == self.column:
                    continue
                else:
                    if 0 <= r < table.nRow and 0 <= c < table.nColumn:
                        self.sensors[r][c] = table.cells[r][c]
                    else:
                        self.sensors[r][c] = TypeCells.OBSTACLE"""


    def getPos(self):
        return (self.row, self.column)

    def setPos(self, row, column):
        self.column, self.row = column, row


class GP:
    def __init__(self, sizePopulation, maxSizeIndivid, chanceMutation = 0.2, chanceCrossover= 0.8):
        self.numberPopulation = 0
        self.sizePopulation = sizePopulation
        self.maxSizeIndivid = maxSizeIndivid
        self.chanceMutation = chanceMutation
        self.chanceCrossover = chanceCrossover
        self.population = []
        self.parents = []
        self.children = []
        self.otherHalfPopulation = []
        self.fitnessPopulation = []
        self.sumFitnessPopulation = 0
        self.meanFitnessPopulation = 0
        self.maxFitnessPopulation = 0
        self.minFitnessPopulation = 0
        self.isGoal3 = False
        #self.maxSizePartCode = 5

    def initial_population(self):
        self.population = [Individ(self.maxSizeIndivid) for i in range(self.sizePopulation)]
        for i in self.population:
            i.createProgramm()
        self.numberPopulation = 1

    def crossover(self, individ1, individ2):
        l1 = random.randint(0, individ1.size-1)
        r1 = random.randint(l1+1, individ1.size)
        l2 = random.randint(0, individ2.size-1)
        r2 = random.randint(l2+1, individ2.size)
        n1 = individ1.prog[:l1] + individ2.prog[l2:r2] + individ1.prog[r1:]
        n2 = individ2.prog[:l2] + individ1.prog[l1:r1] + individ2.prog[r2:]
        size = self.maxSizeIndivid
        n1 = n1[:size]
        n2 = n2[:size]
        return (Individ(size, n1, len(n1)), Individ(size, n2, len(n2)))

    def crossoverPopulation(self, population):
        lst = []
        for i in range(0, len(population), 2):
            n1, n2 = self.crossover(population[i], population[i+1])
            lst.append(n1)
            lst.append(n2)
        return lst


    def mutationComand(self, individ):
        cm = [Robot.Moving.STAY,
              Robot.Moving.UP,
              Robot.Moving.LEFT,
              Robot.Moving.DOWN,
              Robot.Moving.RIGHT]
        Ncomand = random.randint(1, individ.size)
        for i in range(Ncomand):
            numberComand = random.randint(0, individ.size - 1)
            numberRobot = random.randint(0, 2)
            choiceComand = random.choice(cm)
            individ.prog[numberComand][numberRobot] = choiceComand

    def mutationPopulation(self, population, propability=0.2):
        for i in range(len(population)):
            if random.random() <= propability:
                self.mutationComand(population[i])

    def calculateFitnessPopulation(self, table):
        self.sumFitnessPopulation = 0
        self.maxFitnessPopulation = 0
        self.minFitnessPopulation = 10000
        self.isGoal3 = False
        for i in range(self.sizePopulation):
            self.population[i].calculateFitness2(table)
            self.fitnessPopulation = self.population[i].fitness
            self.sumFitnessPopulation += self.population[i].fitness
            self.maxFitnessPopulation = max(self.maxFitnessPopulation, self.population[i].fitness)
            self.minFitnessPopulation = min(self.minFitnessPopulation, self.population[i].fitness)
            self.isGoal3 = self.isGoal3 or self.population[i].isGoal3

        self.meanFitnessPopulation = self.sumFitnessPopulation/self.sizePopulation

    def chooseIndivids(self, population):
        lst = random.sample(population, len(population))
        winners = []
        losers = []
        for i in range(0, len(lst), 2):
            if lst[i].fitness > lst[i + 1].fitness:
                winners.append(lst[i])
                losers.append(lst[i + 1])
            else:
                winners.append(lst[i+1])
                losers.append(lst[i])

        return winners, losers

    def sim(self, table):
        if self.numberPopulation == 0:
            self.initial_population()
        self.calculateFitnessPopulation(table)
        self.parents, self.children = self.chooseIndivids(self.population)
        self.children = self.crossoverPopulation(self.parents)
        self.mutationPopulation(self.children, propability=self.chanceMutation)
        self.population = self.parents + self.children
        self.numberPopulation += 1

class Individ:
    def __init__(self, maxSize, code=None, size=0):
        self.maxSize = maxSize
        self.prog = code
        self.fitness = 1000
        self.size = size
        self.isGoal3 = False

    def createProgramm(self, fullSize = True):
        cm = [Robot.Moving.STAY,
              Robot.Moving.UP,
              Robot.Moving.LEFT,
              Robot.Moving.DOWN,
              Robot.Moving.RIGHT]
        if fullSize:
            self.size = self.maxSize
        else:
            self.size = random.randint(1, self.maxSize)
        self.prog = []
        for i in range(self.size):
            self.prog.append([random.choice(cm), random.choice(cm), random.choice(cm)])

    def calculateFitness(self, table):
        table.returnRobotsToStartPosition()
        self.fitness = 1000
        k=0
        for p in self.prog:
            table.move3(p)
            self.fitness -= 1
            k+=1
            if table.isCollisionRobots3() or table.isObstacleCollision3():
                self.fitness -= 100
                table.returnRobotsToStartPosition()
                break
            if table.isGoal3():
                self.isGoal3 = True
                self.fitness += 600
                self.prog = self.prog[:k]
                table.returnRobotsToStartPosition()
                break

    def calculateFitness2(self, table):
        table.returnRobotsToStartPosition()
        self.fitness = 1000
        step = 0

        for p in self.prog:
            table.move3(p)
            self.fitness += 1
            for i in range(3):
                self.fitness -= 2*distAbs(*table.robots[i].getPos(), *table.goals[i].getPos())
                self.fitness += 10*distAbs(*table.robots[i].getPos(), *table.startPositionRobots[i])

            step+=1
            if table.isCollisionRobots3() or table.isObstacleCollision3():
                self.fitness -= 1000
                table.returnRobotsToStartPosition()
                break
            if table.isGoal3():
                self.isGoal3 = True
                self.fitness += 3000
                self.prog = self.prog[:step]
                table.returnRobotsToStartPosition()
                break


        # if table.isGoal3: self.fitness += 300

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

    robot1 = Robot(5, 9)
    robot2 = Robot(1, 3)
    robot3 = Robot(9, 2)
    table.setRobot(robot1, *(robot1.getPos()), 0)
    table.setRobot(robot2, *(robot2.getPos()), 1)
    table.setRobot(robot3, *(robot3.getPos()), 2)

    goal1 = Goal(1, 1)
    goal2 = Goal(5, 8)
    goal3 = Goal(1, 10)
    table.setGoal(goal1, *goal1.getPos(),0)
    table.setGoal(goal2, *goal1.getPos(), 1)
    table.setGoal(goal3, *goal1.getPos(), 2)

    table.setBlockObsctacles(0, 0, 1, 12)
    table.setBlockObsctacles(11, 0, 1, 12)
    table.setBlockObsctacles(1, 0, 10, 1)
    table.setBlockObsctacles(1, 11, 10, 1)
    table.setBlockObsctacles(2, 1, 1, 5)
    table.setBlockObsctacles(2, 7, 1, 4)
    table.setBlockObsctacles(3, 7, 4, 1)
    table.setBlockObsctacles(6, 8, 1, 2)

    genProg = GP(52, 20, chanceMutation=1.0)
    while genProg.numberPopulation < 100 and genProg.isGoal3 == False:
        genProg.sim(table)

    print(genProg.maxFitnessPopulation)
    for p in genProg.children:
        print(p.prog)
    print(genProg.population[0].prog)
    print(genProg.isGoal3)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    table.movingRobots([Robot.Moving.UP])
                if event.key == pygame.K_a:
                    table.movingRobots([Robot.Moving.LEFT])
                if event.key == pygame.K_d:
                    table.movingRobots([Robot.Moving.RIGHT])
                if event.key == pygame.K_s:
                    table.movingRobots([Robot.Moving.DOWN])

        screen.fill( (255,255,255) )
        x += 1
        y += 1
        table.draw(screen)

        pygame.display.flip()
        timer.tick(fps)


if __name__ == '__main__':
    main()