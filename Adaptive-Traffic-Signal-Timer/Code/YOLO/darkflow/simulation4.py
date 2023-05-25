# LAG
# NO. OF VEHICLES IN SIGNAL CLASS
# stops not used
# DISTRIBUTION
# BUS TOUCHING ON TURNS
# Distribution using python class

# *** IMAGE XY COOD IS TOP LEFT
import random
import math
import time
import threading
# from vehicle_detection import detection
import pygame
import sys
import os

# options={
#    'model':'./cfg/yolo.cfg',     #specifying the path of model
#    'load':'./bin/yolov2.weights',   #weights
#    'threshold':0.3     #minimum confidence factor to create a box, greater than 0.3 good
# }

# tfnet=TFNet(options)    #READ ABOUT TFNET
#
secondGreen = 0
# Default values of signal times
defaultRed = 150
defaultYellow = 5
defaultGreen = 30
defaultMinimum = 10
defaultMaximum = 60

signals = []
noOfSignals = 4
simTime = 200       # change this to change time of simulation
timeElapsed = 0

currentGreen = 0   # Indicates which signal is green
nextGreen = (currentGreen+1) % noOfSignals
currentYellow = 0   # Indicates whether yellow signal is on or off

# Average times for vehicles to pass the intersection
carTime = 2
bikeTime = 1
rickshawTime = 2.25
busTime = 2.5
truckTime = 2.5

# Count of cars at a traffic signal
noOfCars = 0
noOfBikes = 0
noOfBuses = 0
noOfTrucks = 0
noOfRickshaws = 0
noOfLanes = 2

# Red signal time at which cars will be detected at a signal
detectionTime = 5

speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8,
          'rickshaw': 2, 'bike': 2.5}  # average speeds of vehicles

# Coordinates of
x = {'right': [0, 0, 0], 'down': [792, 760, 727],
     'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [370, 402, 427], 'down': [0, 0, 0],
     'left': [530, 498, 466], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck',
                3: 'rickshaw', 4: 'bike', 5: 'ambulance'}

directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates of signal image, timer, and vehicle count
rsuCoods = (200, 15)
signalCoods = [(520, 230), (850, 230), (850, 570), (520, 570)]
signalTimerCoods = [(520, 210), (850, 210), (850, 550), (520, 550)]
vehicleCountCoods = [(480, 210), (880, 210), (880, 550), (480, 550)]
vehicleCountTexts = ["0", "0", "0", "0"]
# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 500}
defaultStop = {'right': 490, 'down': 320, 'left': 920, 'up': 600}
stops = {'right': [580, 580, 580], 'down': [320, 320, 320],
         'left': [810, 810, 810], 'up': [545, 545, 545]}

mid = {'right': {'x': 705, 'y': 445}, 'down': {'x': 695, 'y': 450},
       'left': {'x': 695, 'y': 425}, 'up': {'x': 695, 'y': 400}}
rotationAngle = 3

# Gap between vehicles
gap = 15    # stopping gap
gap2 = 15   # moving gap

pygame.init()
simulation = pygame.sprite.Group()
congestionIndexDefault = ["10", "20", "30", "40", "50", "60", "70", "80"]
congestionCoord = {'left': {0: (240, 300), 1: (240, 600)}, 'right': {0: (1000, 600),
                   1: (1000, 300)}, 'up': {0: (810, 100), 1: (530, 100)}, 'down': {0: (530, 700), 1: (810, 700)}}
congestionIndexText = {'left': {0: "10", 1: "20"}, 'right': {0: "30", 1: "40"}, 'up': {0: "50", 1: "60"},
                       'down': {0: "70", 1: "80"}}

congestionIndexDirections = {'right': {'bikeSpeed': 0, 'bikeNo': 0, 'carSpeed': 0, 'carNo': 0, 'fourWheelerSpeed': 0, 'fourWheelerNo': 0},
                             'down': {'bikeSpeed': 0, 'bikeNo': 0, 'carSpeed': 0, 'carNo': 0, 'fourWheelerSpeed': 0, 'fourWheelerNo': 0},
                             'left': {'bikeSpeed': 0, 'bikeNo': 0, 'carSpeed': 0, 'carNo': 0, 'fourWheelerSpeed': 0, 'fourWheelerNo': 0},
                             'up': {'bikeSpeed': 0, 'bikeNo': 0, 'carSpeed': 0, 'carNo': 0, 'fourWheelerSpeed': 0, 'fourWheelerNo': 0}}

congestionVehicle = {0: {0: 'carSpeed', 1: 'carNo'}, 1: {0: 'fourWheelerSpeed', 1: 'fourWheelerNo'}, 2: {0: 'fourWheelerSpeed', 1: 'fourWheelerNo'},
                     3: {0: 'bikeSpeed', 1: 'bikeNo'}, 4: {0: 'bikeSpeed', 1: 'bikeNo'}, 5: 'ambulance'}
# passing the screen
# up- y = 10 left = x = 0 right = x = 1390 down = y = 780

exit_success = True
total_rounds = 0
total_ambulance = 0
# right - 495  left - 495 down - 315 up - 215
total_road_length = {'right': 500, 'left': 500, 'down': 370, 'up': 275}


class RoadSideUnit:
    def congestionIndex():
        print("congestion index calculation")


class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn, speedRandom, rando):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speedRandom
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        self.stopped = 0
        self.rando = rando
        vehicles[direction][lane].append(self)
        # self.stop = stops[direction][lane]
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.currentImage = pygame.image.load(path)
        self.exit = 0

        if(direction == 'right'):
            # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap
                self.stop = vehicles[direction][lane][self.index-1].stop - \
                    vehicles[direction][lane][self.index -
                                              1].currentImage.get_rect().width - gap
            else:
                self.stop = defaultStop[direction]
            # Set new starting and stopping coordinate
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction == 'left'):
            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop + \
                    vehicles[direction][lane][self.index -
                                              1].currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif(direction == 'down'):
            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop - \
                    vehicles[direction][lane][self.index -
                                              1].currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction == 'up'):
            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop + \
                    vehicles[direction][lane][self.index -
                                              1].currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    def move(self):
        global total_rounds, exit_success, total_ambulance
        # up- y = 10 left = x = 0 right = x = 1390 down = y = 780
        if(self.direction == 'right'):
            # if the image has crossed stop line now
            # if the image has crossed stop line now
            if(self.crossed == 0 and self.x+self.currentImage.get_rect().width > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1

            if(self.willTurn == 1):
                if(self.crossed == 0 or self.x+self.currentImage.get_rect().width < mid[self.direction]['x']):
                    if((self.x+self.currentImage.get_rect().width <= self.stop or (currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (self.index == 0 or self.x+self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - gap2) or vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.x += self.speed
                else:
                    if(self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(
                            self.originalImage, -self.rotateAngle)
                        self.x += 2
                        self.y += 1.8

                        if(self.rotateAngle == 90):
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.image = pygame.image.load(path)
                    else:
                        if(self.index == 0 or self.y+self.currentImage.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - gap2) or self.x+self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - gap2)):
                            self.y += self.speed
                            # up - y = 10 left = x = 0 right = x = 1390 down = y = 780
                            if(self.vehicleClass == 'ambulance' and self.crossed == 1 and (self.y <= 10 or self.y >= 780) and (self.exit == 0)):
                                exit_success = True
                                total_rounds += 1
                                total_ambulance = 0
                                self.exit = 1
                                print("crossed", self.y, self.direction)

            else:
                if((self.x+self.currentImage.get_rect().width <= self.stop or self.crossed == 1 or (currentGreen == 0 and currentYellow == 0)) and (self.index == 0 or self.x+self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - gap2) or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x += self.speed  # move the vehicle
                    # up - y = 10 left = x = 0 right = x = 1390 down = y = 780
                    if(self.vehicleClass == 'ambulance' and (self.crossed == 1) and (self.x <= 0 or self.x >= 1390) and (self.exit == 0)):
                        exit_success = True
                        total_rounds += 1
                        total_ambulance = 0
                        self.exit = 1
                        print("crossed", self.x, self.crossed,
                              self.exit, self.direction)

        elif(self.direction == 'down'):
            if(self.crossed == 0 and self.y+self.currentImage.get_rect().height > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1

            if(self.willTurn == 1):
                if(self.crossed == 0 or self.y+self.currentImage.get_rect().height < mid[self.direction]['y']):
                    if((self.y+self.currentImage.get_rect().height <= self.stop or (currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (self.index == 0 or self.y+self.currentImage.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - gap2) or vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.y += self.speed
                else:
                    if(self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(
                            self.originalImage, -self.rotateAngle)
                        self.x -= 2.5
                        self.y += 2

                        if(self.rotateAngle == 90):
                            self.turned = 1
                    else:
                        if(self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or self.y < (vehicles[self.direction][self.lane][self.index-1].y - gap2)):
                            self.x -= self.speed
                            # up - y = 10 left = x = 0 right = x = 1390 down = y = 780
                            if(self.vehicleClass == 'ambulance' and self.crossed == 1 and (self.x <= 0 or self.x >= 1390) and (self.exit == 0)):
                                exit_success = True
                                total_rounds += 1
                                total_ambulance = 0
                                self.exit = 1
                                print("crossed", self.x, self.direction)

            else:
                if((self.y+self.currentImage.get_rect().height <= self.stop or self.crossed == 1 or (currentGreen == 1 and currentYellow == 0)) and (self.index == 0 or self.y+self.currentImage.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - gap2) or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    self.y += self.speed
                    # up - y = 10 left = x = 0 right = x = 1390 down = y = 780
                    if(self.vehicleClass == 'ambulance' and self.crossed == 1 and (self.y <= 10 or self.y >= 780) and (self.exit == 0)):
                        exit_success = True
                        total_rounds += 1
                        total_ambulance = 0
                        self.exit = 1
                        print("crossed", self.y, self.direction)

        elif(self.direction == 'left'):
            if(self.crossed == 0 and self.x < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1

            if(self.willTurn == 1):
                if(self.crossed == 0 or self.x > mid[self.direction]['x']):
                    if((self.x >= self.stop or (currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.x -= self.speed
                        # up - y = 10 left = x = 0 right = x = 1390 down = y = 780

                else:
                    if(self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(
                            self.originalImage, -self.rotateAngle)
                        self.x -= 1.8
                        self.y -= 2.5

                        if(self.rotateAngle == 90):
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.currentImage = pygame.image.load(path)
                    else:
                        if(self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or self.x > (vehicles[self.direction][self.lane][self.index-1].x + gap2)):
                            self.y -= self.speed
                            # up - y = 10 left = x = 0 right = x = 1390 down = y = 780
                        if(self.vehicleClass == 'ambulance' and self.crossed == 1 and (self.y <= 10 or self.y >= 780) and (self.exit == 0)):
                            exit_success = True
                            total_rounds += 1
                            total_ambulance = 0
                            self.exit = 1
                            print("crossed", self.y, self.direction)
            else:
                if((self.x >= self.stop or self.crossed == 1 or (currentGreen == 2 and currentYellow == 0)) and (self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x -= self.speed  # move the vehicle
                    # up - y = 10 left = x = 0 right = x = 1390 down = y = 780
                    if(self.vehicleClass == 'ambulance' and self.crossed == 1 and (self.x <= 0 or self.x >= 1390) and (self.exit == 0)):
                        exit_success = True
                        total_rounds += 1
                        total_ambulance = 0
                        self.exit = 1
                        print("crossed", self.x, self.direction)
            # if((self.x>=self.stop or self.crossed == 1 or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2))):
            #     self.x -= self.speed
        elif(self.direction == 'up'):
            if(self.crossed == 0 and self.y < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1

            if(self.willTurn == 1):
                if(self.crossed == 0 or self.y > mid[self.direction]['y']):
                    if((self.y >= self.stop or (currentGreen == 3 and currentYellow == 0) or self.crossed == 1) and (self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.y -= self.speed
                else:
                    if(self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(
                            self.originalImage, -self.rotateAngle)
                        self.x += 1
                        self.y -= 1

                        if(self.rotateAngle == 90):
                            self.turned = 1
                    else:
                        if(self.index == 0 or self.x < (vehicles[self.direction][self.lane][self.index-1].x - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width - gap2) or self.y > (vehicles[self.direction][self.lane][self.index-1].y + gap2)):
                            self.x += self.speed
                            # up - y = 10 left = x = 0 right = x = 1390 down = y = 780
                        if(self.vehicleClass == 'ambulance' and self.crossed == 1 and (self.x <= 0 or self.x >= 1390) and (self.exit == 0)):
                            exit_success = True
                            total_rounds += 1
                            total_ambulance = 0
                            self.exit = 1
                            print("crossed", self.x, self.direction)
            else:
                if((self.y >= self.stop or self.crossed == 1 or (currentGreen == 3 and currentYellow == 0)) and (self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    self.y -= self.speed
                    # up - y = 10 left = x = 0 right = x = 1390 down = y = 780
                    if(self.vehicleClass == 'ambulance' and self.crossed == 1 and (self.y <= 10 or self.y >= 780) and (self.exit == 0)):
                        exit_success = True
                        total_rounds += 1
                        total_ambulance = 0
                        self.exit = 1
                        print("crossed", self.y, self.direction)

# Initialization of signals with default values


def initialize():
    rsu1 = RoadSideUnit()

    ts1 = TrafficSignal(0, defaultYellow, defaultGreen,
                        defaultMinimum, defaultMaximum)
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow,
                        defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow,
                        defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow,
                        defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts4)

    repeat()

# Set time according to formula


def setTime():
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfRickshaws, noOfLanes
    global carTime, busTime, truckTime, rickshawTime, bikeTime
    os.system("say detecting vehicles, " +
              directionNumbers[(currentGreen+1) % noOfSignals])
#    detection_result=detection(currentGreen,tfnet)
#    greenTime = math.ceil(((noOfCars*carTime) + (noOfRickshaws*rickshawTime) + (noOfBuses*busTime) + (noOfBikes*bikeTime))/(noOfLanes+1))
#    if(greenTime<defaultMinimum):
#       greenTime = defaultMinimum
#    elif(greenTime>defaultMaximum):
#       greenTime = defaultMaximum
    # greenTime = len(vehicles[currentGreen][0])+len(vehicles[currentGreen][1])+len(vehicles[currentGreen][2])
    # noOfVehicles = len(vehicles[directionNumbers[nextGreen]][1])+len(vehicles[directionNumbers[nextGreen]][2])-vehicles[directionNumbers[nextGreen]]['crossed']
    # print("no. of vehicles = ",noOfVehicles)
    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0
    for j in range(len(vehicles[directionNumbers[nextGreen]][0])):
        vehicle = vehicles[directionNumbers[nextGreen]][0][j]
        if(vehicle.crossed == 0):
            vclass = vehicle.vehicleClass
            # print(vclass)
            noOfBikes += 1
    for i in range(1, 3):
        for j in range(len(vehicles[directionNumbers[nextGreen]][i])):
            vehicle = vehicles[directionNumbers[nextGreen]][i][j]
            if(vehicle.crossed == 0):
                vclass = vehicle.vehicleClass
                # print(vclass)
                if(vclass == 'car'):
                    noOfCars += 1
                elif(vclass == 'bus'):
                    noOfBuses += 1
                elif(vclass == 'truck'):
                    noOfTrucks += 1
                elif(vclass == 'rickshaw'):
                    noOfRickshaws += 1
    # print(noOfCars)
    greenTime = math.ceil(((noOfCars*carTime) + (noOfRickshaws*rickshawTime) + (
        noOfBuses*busTime) + (noOfTrucks*truckTime) + (noOfBikes*bikeTime))/(noOfLanes+1))
    # greenTime = math.ceil((noOfVehicles)/noOfLanes)
   # print('Green Time: ', greenTime)
    if(greenTime < defaultMinimum):
        greenTime = defaultMinimum
    elif(greenTime > defaultMaximum):
        greenTime = defaultMaximum
    # greenTime = random.randint(15,50)
    signals[(currentGreen+1) % (noOfSignals)].green = greenTime


def repeat():
    global currentGreen, currentYellow, nextGreen, secondGreen
    # while the timer of current green signal is not zero

    while(signals[currentGreen].green > 0):
        printStatus()
        updateValues()
        time.sleep(1)

    currentYellow = 1   # set yellow signal on
    vehicleCountTexts[currentGreen] = "0"
    # reset stop coordinates of lanes and vehicles
    for i in range(0, 3):
        stops[directionNumbers[currentGreen]
              ][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    # while the timer of current yellow signal is not zero

    while(signals[currentGreen].yellow > 0):
        printStatus()
        updateValues()
        time.sleep(1)
    # set yellow signal off
    currentYellow = 0

    # reset all signal times of current signal to default times
    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    currentGreen = nextGreen  # set next signal as green signal
    nextGreen = (currentGreen+1) % noOfSignals    # set next green signal
    # set the red time of next to next signal as (yellow time + green time) of next signal
    signals[nextGreen].red = signals[currentGreen].yellow + \
        signals[currentGreen].green
    repeat()

# Print the signal timers on cmd


def printStatus():
    '''
    for i in range(0, noOfSignals):
        if(i == currentGreen):
            if(currentYellow == 0):
                print(" GREEN TS", i+1, "-> r:",
                      signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
            else:
                print("YELLOW TS", i+1, "-> r:",
                      signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
        else:
            print("   RED TS", i+1, "-> r:",
                  signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
    print()
    '''
# Update values of the signal timers after every second


def updateValues():
    for i in range(0, noOfSignals):
        if(i == currentGreen):
            if(currentYellow == 0):
                signals[i].green -= 1
                signals[i].totalGreenTime += 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

# Generating vehicles in the simulation


def generateVehicles():
    global exit_success, total_ambulance
    while(True):

        vehicle_type = random.randint(0, 4)
        if(vehicle_type == 4):
            lane_number = 0
        else:
            lane_number = random.randint(0, 1) + 1
        will_turn = 0
        if(lane_number == 2):
            temp = random.randint(0, 4)
            if(temp <= 2):
                will_turn = 1
            elif(temp > 2):
                will_turn = 0
        temp = random.randint(0, 999)
        speedRandom = random.randint(1, 2)
        speedRandom = speedRandom+random.random()
        rando = random.randint(5, 10)

       # print('random speed - ', speedRandom)
        direction_number = 0
        a = [900, 920, 950, 1000]
        if(temp < a[0]):
            direction_number = 0
        elif(temp < a[1]):
            direction_number = 1
        elif(temp < a[2]):
            direction_number = 2
        elif(temp < a[3]):
            direction_number = 3

        Vehicle(lane_number, vehicleTypes[vehicle_type],
                direction_number, directionNumbers[direction_number], will_turn, speedRandom, rando)

        time.sleep(0.35)


def simulationTime():
    global timeElapsed, simTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed == simTime):
            totalVehicles = 0
          #  print('Lane-wise Vehicle Counts')
            for i in range(noOfSignals):
                print('Lane', i+1, ':',
                      vehicles[directionNumbers[i]]['crossed'])
                totalVehicles += vehicles[directionNumbers[i]]['crossed']
            print('Total vehicles passed: ', totalVehicles)
            print('Total time passed: ', timeElapsed)
            print('No. of vehicles passed per unit time: ',
                  (float(totalVehicles)/float(timeElapsed)))
            os._exit(1)


def congestionIndexCalculation(direction):
    global gap, total_road_length
    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0
    carNo, bikeNo, fourWheelerNo = 0, 0, 0
    bikeAvg, carAvg, fourWheelerAvg = 0, 0, 0
    lane0, lane1, lane2 = 0, 0, 0
    bikeLength, carLength = 0, 0
    for j in range(len(vehicles[directionNumbers[direction]][0])):
        vehicle = vehicles[directionNumbers[direction]][0][j]
        if(vehicle.crossed == 0):
            bikeNo += 1
            bikeAvg += vehicle.speed*vehicle.rando
            bikeLength = max(vehicle.currentImage.get_rect(
            ).height, vehicle.currentImage.get_rect().width)
    lane0 = bikeNo*bikeLength
    lane0 += (bikeNo-1)*gap

    carNolane1, busNolane1, truckNolane1, rickshawNolane1 = 0, 0, 0, 0
    carNolane2, busNolane2, truckNolane2, rickshawNolane2 = 0, 0, 0, 0

    busLength, truckLength, rickshawLength = 0, 0, 0
    for i in range(1, 3):
        for j in range(len(vehicles[directionNumbers[direction]][i])):
            vehicle = vehicles[directionNumbers[direction]][i][j]
            if(vehicle.crossed == 0):
                vclass = vehicle.vehicleClass
                # print(vclass)
                if(vclass == 'car'):
                    if i == 1:
                        carNolane1 += 1
                    else:
                        carNolane2 += 1
                    carLength = 20

                elif(vclass == 'bus'):
                    if i == 1:
                        busNolane1 += 1
                    else:
                        busNolane2 += 1
                    busLength = max(vehicle.currentImage.get_rect(
                    ).height, vehicle.currentImage.get_rect().width)
                elif(vclass == 'truck'):
                    if i == 1:
                        truckNolane1 += 1
                    else:
                        truckNolane2 += 1
                    truckLength = max(vehicle.currentImage.get_rect(
                    ).height, vehicle.currentImage.get_rect().width)
                elif(vclass == 'rickshaw'):
                    if i == 1:
                        rickshawNolane1 += 1
                    else:
                        rickshawNolane2 += 1
                    rickshawLength = max(vehicle.currentImage.get_rect(
                    ).height, vehicle.currentImage.get_rect().width)

    total_vehicle_length = 0

    lane1 = (carNolane1*carLength) + (busNolane1*busLength) + \
        (truckNolane1*truckLength) + (rickshawNolane1*rickshawLength)
    lane2 = (carNolane2*carLength) + (busNolane2*busLength) + \
        (truckNolane2*truckLength) + (rickshawNolane2*rickshawLength)
    total_lane1 = carNolane1 + busNolane1 + truckNolane1 + rickshawNolane1
    total_lane2 = carNolane2 + busNolane2 + truckNolane2 + rickshawNolane2
    lane1 += (total_lane1-1)*gap
    lane2 += (total_lane2-1)*gap
    total_vehicle_length = lane0 + lane1 + lane2
    congestion_index = total_vehicle_length / \
        (total_road_length[directionNumbers[direction]]*3)
    print(congestion_index)

    #print("Averages - ", direction, bikeAvg, carAvg, fourWheelerAvg)
    if congestion_index >= 0.8:

        return "High"
    elif congestion_index >= 0.6:
        return "Medium"
    else:
        return "low"

    congestionStatus = ""
    if fourWheelerNo + carNo + bikeNo >= 16:
        congestionStatus = "High"
    else:
        congestionStatus = "Medium"

    return congestionStatus

    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0

    # cars congestion index
    carAvg = 0
    carno = congestionIndexDirections[directionNumbers[direction]]['carNo']
    bikeNo = congestionIndexDirections[directionNumbers[direction]]['bikeNo']
    fourWheelerNo = congestionIndexDirections[directionNumbers[direction]
                                              ]['fourWheelerNo']

    if congestionIndexDirections[directionNumbers[direction]]['carNo'] != 0:
        carAvg = congestionIndexDirections[directionNumbers[direction]]['carsSpeed'] / \
            congestionIndexDirections[directionNumbers[direction]]['carNo']

    if congestionIndexDirections[directionNumbers[direction]]['bikeNo'] != 0:
        bikeAvg = congestionIndexDirections[directionNumbers[direction]]['bikeSpeed'] / \
            congestionIndexDirections[directionNumbers[direction]]['bikeNo']

    if congestionIndexDirections[directionNumbers[direction]]['fourWheelerNo'] != 0:
        fourWheelerAvg = congestionIndexDirections[directionNumbers[direction]]['fourWheelerSpeed'] / \
            congestionIndexDirections[directionNumbers[direction]
                                      ]['fourWheelerNo']

    # print(noOfCars)
    congestionStatus = ""
    if fourWheelerNo + carno + bikeNo > 13:
        congestionStatus = "High"
    else:
        congestionStatus = "Medium"

    return congestionStatus

    greenTime = math.ceil(((noOfCars*carTime) + (noOfRickshaws*rickshawTime) + (
        noOfBuses*busTime) + (noOfTrucks*truckTime) + (noOfBikes*bikeTime))/(noOfLanes+1))
    # greenTime = math.ceil((noOfVehicles)/noOfLanes)
   # print('Green Time: ', greenTime)
    if(greenTime < defaultMinimum):
        greenTime = defaultMinimum
    elif(greenTime > defaultMaximum):
        greenTime = defaultMaximum
    # greenTime = random.randint(15,50)
    signals[(currentGreen+1) % (noOfSignals)].green = greenTime


class Main:
    thread4 = threading.Thread(
        name="simulationTime", target=simulationTime, args=())
    thread4.daemon = True
    thread4.start()

    thread2 = threading.Thread(
        name="initialization", target=initialize, args=())    # initialization
    thread2.daemon = True
    thread2.start()

    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/bg10.jpg')
    rsu = pygame.image.load('images/rsu.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread3 = threading.Thread(
        name="generateVehicles", target=generateVehicles, args=())    # Generating vehicles
    thread3.daemon = True
    thread3.start()

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background, (0, 0))   # display background in simulation
        # display signal and set timer according to current status: green, yello, or red
        screen.blit(rsu, (200, 15))
        t2 = font.render(
            str(1000), True, white, black)
        screen.blit(t2, (500, 770))
        for i in range(0, noOfSignals):
            if(i == currentGreen):
                if(currentYellow == 1):
                    if(signals[i].yellow == 0):
                        signals[i].signalText = "STOP"
                    else:
                        signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    if(signals[i].green == 0):
                        signals[i].signalText = "SLOW"
                    else:
                        signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if(signals[i].red <= 10):
                    if(signals[i].red == 0):
                        signals[i].signalText = "GO"
                    else:
                        signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["", "", "", ""]

        # display signal timer and vehicle count
        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(
                str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(
                str(displayText), True, black, white)
            screen.blit(vehicleCountTexts[i], vehicleCountCoods[i])

        timeElapsedText = font.render(
            ("Time Elapsed: "+str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText, (1100, 50))

        # display the vehicles
        for vehicle in simulation:
            screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
            # vehicle.render(screen)
            vehicle.move()
        pygame.display.update()


Main()
