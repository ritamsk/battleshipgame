import sys
import os
from random import randint
import asyncio
import logging
import time
logger = logging.getLogger(__name__)


def coord_chek_api(coordinate):
    if str(coordinate[0]) not in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"] or coordinate[1:] not in  ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
        return False #("invalid Coordinate, try again")
    else:
        return True



def create_board():
    '''
    creates a board and fills it with water "~"
    '''
    grid = []
    for i in range(10):
        grid.append(["~", "~", "~", "~", "~", "~", "~", "~", "~", "~"])
    return grid

def char_convert(inputchar):
    '''
    converts the grid letters to numbers
    '''
    letterconversion = {"A": 1,
                        "B": 2,
                        "C": 3,
                        "D": 4,
                        "E": 5,
                        "F": 6,
                        "G": 7,
                        "H": 8,
                        "I": 9,
                        "J": 10}
    return letterconversion[inputchar.upper()]


def int_convert(inputint):
    '''
    converts the grid letters to numbers
    '''
    letterconversion = { 1: "A",
                         2 : "B",
                         3 : "C",
                        4 : "D",
                         5 : "E",
                        6 : "F",
                         7 : "G",
                         8 : "H",
                        9 : "I",
                        10 : "J"}
    return letterconversion[inputint]

def place_ship(lengthship, shipcharacter, origin, orientation, gridboard):
    '''
    places a ship onto the board with the starting letter of the ship.
    lengthship applies to the length of the ship, shipcharacter is the first character indicating the ship,
    origin is the starting point, orientation indicates either down(vertical) or to the right(horizontal)
    '''

    x = char_convert(origin[0])-1 # converts the x coordinate to the corresponding number from dictionary
    y = int(origin[1:])-1

    for i in range(lengthship):
        gridboard[y][x]=shipcharacter
        if orientation.lower()=="h":
            x+=1
        elif orientation.lower()=="v":
            y+=1
        else:
            raise ValueError('Orientation not recognised')


def shiplength(ship):
    ships = {"Battleship": 4,
             "Destroyer1": 3,
             "Destroyer2": 3,
             "Cruiser1": 2,
             "Cruiser2": 2,
             "Cruiser3": 2,
             "Torpedo Boat1": 1,
             "Torpedo Boat2": 1,
             "Torpedo Boat3": 1,
             "Torpedo Boat4": 1
             }
    return ships[ship]

def test_placement(lengthship, origin, orientation, gridboard):
    '''
    to check if the placement is actually valid
    '''
    x = char_convert(origin[0])-1
    y = int(origin[1:])-1

    if (x+lengthship>10) and (orientation == "h"):
        return False
    elif (y+lengthship>10) and (orientation == "v"): # this checks if ship is in given grid boundaries
        return False
    else:
        for i in range(lengthship):
            if gridboard[y][x] in ["B","D","C","T"]:
                return False
            elif orientation.lower()=="h":
                x+=1
            elif orientation.lower()=="v":
                y+=1
            else:
                raise ValueError('Orientation not recognised')
        return True

def random_board():
    '''
    creates a random board with random coordinates and direction
    '''
    randomboard=create_board()
    for boat in ["Battleship", "Destroyer1", "Destroyer2", "Cruiser1", "Cruiser2", "Cruiser3", "Torpedo Boat1", "Torpedo Boat2", "Torpedo Boat3", "Torpedo Boat4"]:
        l = shiplength(boat)
        coordinate = random_coord()
        direction = ["v","h"][randint(0,1)]
        #print(coordinate)
        while not test_placement(l, coordinate, direction, randomboard):
            coordinate = ["A","B","C","D","E","F","G","H","I","J"][randint(0,9)]+str(randint(1,10))
            direction = ["v","h"][randint(0,1)]
            #print(coordinate)
        place_ship(l, boat[0], coordinate, direction, randomboard)
    return randomboard


def random_board_api():
    '''
    creates a random board with random coordinates and direction
    '''
    answer = ''
    randomboard=create_board()
    for boat in ["Battleship", "Destroyer1", "Destroyer2", "Cruiser1", "Cruiser2", "Cruiser3", "Torpedo Boat1", "Torpedo Boat2", "Torpedo Boat3", "Torpedo Boat4"]:
        l = shiplength(boat)
        coordinate = random_coord()
        direction = ["v","h"][randint(0,1)]
        #print(coordinate)
        while not test_placement(l, coordinate, direction, randomboard):
            coordinate = ["A","B","C","D","E","F","G","H","I","J"][randint(0,9)]+str(randint(1,10))
            direction = ["v","h"][randint(0,1)]
            # print(coordinate)
        answer+=coordinate+direction+l.__str__()+'|'
        place_ship(l, boat[0], coordinate, direction, randomboard)
    return answer[:-1]



def random_coord():
    '''
    creates a random coordinate
    '''
    return ["A","B","C","D","E","F","G","H","I","J"][randint(0,9)]+str(randint(1,10))

def shoot(coordinate, opponentboard):
    '''
    shooting at the opponent board, takes in coordinate you want to shoot and which board is being shut
    '''
    x = char_convert(coordinate[0])-1
    y = int(coordinate[1:])-1

    if opponentboard[y][x] == "~": #symbol for water
        opponentboard[y][x] = "#" #symbol for a miss
        return True, "MISS"
    elif opponentboard[y][x] not in ["~", "#", "*"]:
        ship = opponentboard[y][x]
        opponentboard[y][x] = "*" #symbol for a hit
        return False, ship
    else:
        return False, 0 # for completeness


def create_board_api(board):
    new_board=[]
    for ship in board:
        print(ship)
        lenght = int(ship[len(ship)-1])
        new_board.append(ship[0]+ship[1:len(ship)-2])
        shipl =ship[0]
        shipi=int(ship[1:len(ship)-2])
        for i in range(1, lenght):
            if ship[2]=="v":
                shipi +=1
                new_board.append(ship[0]+str(shipi))
            else:
                shipl = int_convert(char_convert(shipl)+1)
                new_board.append( shipl + ship[1:len(ship)-2])
    print(new_board)
    return new_board



def shoot_api(coordinate, opponentboard):
    opponentboard = create_board_api(opponentboard)
    for ship in opponentboard:
        if coordinate == ship:
            return b'hit'
    return b'miss'




