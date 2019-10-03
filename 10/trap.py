import random

class Trap: 
    def __init__(self):
        self.TRAP = 0
        self.ROAD = 1
        self.PEOPLE = 2
        self.EXIT = 3
        self.DEAD = 10
        self.LIVE = 11
        self.ESCAPED = 12
        self.maplist=[[0,0,0],
                      [0,0,0],
                      [0,0,0]]
        self.playerPosition = [random.choice([r for r in range(2)]),random.choice([c for c in range(3)])]
        self.exitPosition =[2,1]
        self.playerStatus = self.LIVE
        
        
    def changeMap(self):
        self.generateMap()
        return self.drawMap()

    def getmap(self):
        return self.maplist
    

    def generateMap(self):
        for r in range(3):
            for c in range(3):
                if r == self.playerPosition[0] and c == self.playerPosition[1]:
                    self.maplist[r][c] = self.PEOPLE
                #self.maplist[r][c] != self.PEOPLE and self.maplist[r][c] != self.EXIT:
                elif r == self.exitPosition[0] and c == self.exitPosition[1]:
                    self.maplist[r][c] = self.EXIT
                else:
                    self.maplist[r][c] =  random.choice([self.TRAP,self.ROAD])

    

    def roomContent(self,content):
        if content == self.TRAP:
            return "X"
        elif content == self.PEOPLE:
            return "*"
        elif content == self.EXIT:
            return "@"
        else:
            return " "
        
    def drawMap(self):
        trapmap = "You are in trap room. If you want to go back, you need to move to EXIT.If you go into TRAP, you will die.\n"
        trapmap += "YOU--*  EXIT--@ TRAP--X\n"
        trapmap += "MOVE INPUT: up, down, left, right, wait.\n"
        trapmap += '-----------\n'
        trapmap +=' '+ self.roomContent(self.maplist[0][0]) + ' | ' + self.roomContent(self.maplist[0][1])+ ' | ' + self.roomContent(self.maplist[0][2])+"\n"
        trapmap += '-----------\n'
        trapmap +=' '+ self.roomContent(self.maplist[1][0]) + ' | ' + self.roomContent(self.maplist[1][1])+ ' | ' + self.roomContent(self.maplist[1][2])+"\n"
        trapmap += '-----------\n'
        trapmap +=' '+ self.roomContent(self.maplist[2][0]) + ' | ' + self.roomContent(self.maplist[2][1])+ ' | ' + self.roomContent(self.maplist[2][2])+"\n"
        trapmap += '-----------\n'
        return trapmap
    
    def isEscape(self):
        if self.playerPosition[0] == self.exitPosition[0] and self.playerPosition[1] == self.exitPosition[1]:
            self.playerStatus = self.ESCAPED
        elif self.maplist[self.playerPosition[0]][self.playerPosition[1]] == self.TRAP:
            self.playerStatus = self.DEAD
        else:
            pass
    def commandHandler(self,command):
        if command == "up":
            #print(command)
            nextY = self.playerPosition[0] -1
            if nextY >= 0 and nextY <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[0] = nextY
            else:
                self.output("Can't go that way")
                
        elif command == "down":
            #print(command)
            nextY = self.playerPosition[0] + 1
            if nextY >= 0 and nextY <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[0] = nextY

            else:
                self.output("Can't go that way")
                
        elif command == "left":
            #print(command)
            nextX = self.playerPosition[1] -1
            if nextX >= 0 and nextX <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[1] = nextX
            else:
                self.output("Can't go that way")
                
        elif command == "right":
            #print(command)
            nextX = self.playerPosition[1] +1
            if nextX >= 0 and nextX <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[1] = nextX
            else:
                self.output("Can't go that way")
                
        elif command == "wait":
            self.output("Waiting")
        else:
            self.output("what to do?")
        self.isEscape()
        self.changeMap()
        
    def output(self,string0):
        print(string0)

        
trap =Trap()
while True:
    if trap.playerStatus == trap.ESCAPED:
        print('escape')
        break
    elif trap.playerStatus == trap.DEAD:
        print("dead")
        break
    else:
        trap.output(trap.changeMap())
        command =input()
        trap.commandHandler(command)
        
