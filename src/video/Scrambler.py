import random
import sys

moves = ["U", "D", "F", "B", "R", "L"]
dir = ["", "'", "2"]
slen = random.randint(25, 28)

class Scrambler():
    def __init__(self):
        self.scramble_mode = False
        self.expected_state = []
    
    def gen_scramble(self):
        # Make array of arrays that represent moves ex. U' = ['U', "'"]
        s = self.valid([[random.choice(moves), random.choice(dir)] for x in range(slen)])
        return self.scramble(s, slen)

        # Format scramble to a string with movecount
        # return ''.join(str(s[x][0]) + str(s[x][1]) + ' ' for x in range(len(s))) + "[" + str(slen) + "]"

    def valid(self, ar):
        # Check if Move behind or 2 behind is the same as the random move
        # this gets rid of 'R R2' or 'R L R2' or similar for all moves
        for x in range(1, len(ar)):
            while ar[x][0] == ar[x-1][0]:
                ar[x][0] = random.choice(moves)
        for x in range(2, len(ar)):
            while ar[x][0] == ar[x-2][0] or ar[x][0] == ar[x-1][0]:
                ar[x][0] = random.choice(moves)
        return ar
   
    def scramble(self, scr, len):
        cube = Cube()
        moves = ['U', 'L', 'F', 'R', 'B', 'D']
        for x in scr:
            cube.move(str(x[0])+str(x[1]), moves.index(x[0]))

        scr = ''.join(str(scr[x][0]) + str(scr[x][1]) + ' ' for x in range(len)) + "[" + str(len) + "]"
        # print(cube.cube)
        # print(scr)
        return (scr, cube)
    
    def resest_scramble_mode(self):
        self.expected_state = []


class Cube:
    def __init__(self):
        self.cube = [['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'], ['o', 'o', 'o', 'o', 'o', 'o', 'o', 'o'], ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g'], ['r', 'r', 'r', 'r', 'r', 'r', 'r', 'r'], ['b', 'b', 'b', 'b', 'b', 'b', 'b', 'b'], ['y', 'y', 'y', 'y', 'y', 'y', 'y', 'y']]

    def faceMove(self, x):
        self.cube[x][0], self.cube[x][6], self.cube[x][4], self.cube[x][2] = self.cube[x][6], self.cube[x][4], self.cube[x][2], self.cube[x][0]
        self.cube[x][1], self.cube[x][7], self.cube[x][5], self.cube[x][3] = self.cube[x][7], self.cube[x][5], self.cube[x][3], self.cube[x][1]
        return
    def faceMovePrime(self, x):
        self.cube[x][0], self.cube[x][2], self.cube[x][4], self.cube[x][6] = self.cube[x][2], self.cube[x][4], self.cube[x][6], self.cube[x][0]
        self.cube[x][1], self.cube[x][3], self.cube[x][5], self.cube[x][7] = self.cube[x][3], self.cube[x][5], self.cube[x][7], self.cube[x][1]
        return

    def swap(self, x1, x2, x3, x4, y1, y2, y3, y4):
        self.cube[x1][y1], self.cube[x2][y2], self.cube[x3][y3], self.cube[x4][y4] = self.cube[x2][y2], self.cube[x3][y3], self.cube[x4][y4], self.cube[x1][y1]



# print(cube.cube)

    def move(self, m, x):
        #Need to do 3 swaps based on the move
        if(m == 'U'):
            self.faceMove(x)
            self.swap(1,2,3,4,0,0,0,0)
            self.swap(1,2,3,4,1,1,1,1)
            self.swap(1,2,3,4,2,2,2,2)
        elif(m == "U'"):
            self.faceMovePrime(x)
            self.swap(1,4,3,2,0,0,0,0)
            self.swap(1,4,3,2,1,1,1,1)
            self.swap(1,4,3,2,2,2,2,2)
        elif(m == 'U2'):
            self.move('U', x)
            self.move('U', x)
        elif(m == 'D'):
            self.faceMove(x)
            self.swap(1,4,3,2,4,4,4,4)
            self.swap(1,4,3,2,5,5,5,5)
            self.swap(1,4,3,2,6,6,6,6)
        elif(m == "D'"):
            self.faceMovePrime(x)
            self.swap(1,2,3,4,4,4,4,4)
            self.swap(1,2,3,4,5,5,5,5)
            self.swap(1,2,3,4,6,6,6,6)
        elif(m == 'D2'):
            self.move('D', x)
            self.move('D', x)
        elif(m == 'R'):
            self.faceMove(x)
            self.swap(0,2,5,4,2,2,2,6)
            self.swap(0,2,5,4,3,3,3,7)
            self.swap(0,2,5,4,4,4,4,0)
        elif(m == "R'"):
            self.faceMovePrime(x)
            self.swap(0,4,5,2,2,6,2,2)
            self.swap(0,4,5,2,3,7,3,3)
            self.swap(0,4,5,2,4,0,4,4)
        elif(m == 'R2'):
            self.move('R', x)
            self.move('R', x)
        elif(m == 'L'):
            self.faceMove(x)
            self.swap(0,4,5,2,6,2,6,6)
            self.swap(0,4,5,2,7,3,7,7)
            self.swap(0,4,5,2,0,4,0,0)
        elif(m == "L'"):
            self.faceMovePrime(x)
            self.swap(0,2,5,4,6,6,6,2)
            self.swap(0,2,5,4,7,7,7,3)
            self.swap(0,2,5,4,0,0,0,4)
        elif(m == 'L2'):
            self.move('L', x)
            self.move('L', x)
        elif(m == 'F'):
            self.faceMove(x)
            self.swap(0,1,5,3,4,2,0,6)
            self.swap(0,1,5,3,5,3,1,7)
            self.swap(0,1,5,3,6,4,2,0)
        elif(m == "F'"):
            self.faceMovePrime(x)
            self.swap(0,3,5,1,4,6,0,2)
            self.swap(0,3,5,1,5,7,1,3)
            self.swap(0,3,5,1,6,0,2,4)
        elif(m == 'F2'):
            self.move('F', x)
            self.move('F', x)
        elif(m == 'B'):
            self.faceMove(x)
            self.swap(0,3,5,1,0,2,4,6)
            self.swap(0,3,5,1,1,3,5,7)
            self.swap(0,3,5,1,2,4,6,0)
        elif(m == "B'"):
            self.faceMovePrime(x)
            self.swap(0,1,5,3,0,6,4,2)
            self.swap(0,1,5,3,1,7,5,3)
            self.swap(0,1,5,3,2,0,6,4)
        elif(m == 'B2'):
            self.move('B', x)
            self.move('B', x)

    
