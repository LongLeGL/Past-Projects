import cv2
import autopy   #autopy basic mouse control is less costing then pyautogui
import pyautogui    #for scrolling
import time
import mediapipe as mp
import handDetectModule as hdm
import math
import numpy as np
import PySimpleGUI as sg
################# GUI ########################
layout =[
        [sg.Text("Options")],
        [sg.Checkbox("Enable clicking", default=True, enable_events=True), 
            sg.Checkbox("Enable scrolling", default = True, enable_events=True)],
        [sg.Text("Operation tracker:")],
        [sg.Output(size=(40,10))],
        [sg.Button("Stop program")]
        ]
gui = sg.Window('Control box', layout)
event, values = gui.read(0)
print("Starting...")
################# SETTINGS ###################
doClick = True
doScroll = True
drawHand = True
cap = cv2.VideoCapture(0)
sw, sh = autopy.screen.size()
camW = int(sw*2/3)
camH = int(sh*2/3)
cap.set(3, camW)  # Capture window's width
cap.set(4, camH)  # Cap window's height
targetId = 0  # mouse pointer = wrist
trackRegionW = int(camW*38/100)
trackRegionH = int(camH*38/100)
trackRegionX = camW-150-trackRegionW
trackRegionY = int(camH/2)-20
smoothen = 6
##############################################
detector = hdm.handDetector(False, 1, 1, 0.4, 0.3)
prevX, prevY = 0, 0
cTime, pTime = 0, 0
lclicked = False
rclicked = False
dclicked = False
holdTime = 0
clickInterval = 0;
held = False
scrolled = False
print("Program started !")
while True:
    isSucess, frame = cap.read()
    event, values = gui.read(0)

    #GUI's controls:
    if event == sg.WIN_CLOSED:
        break
    if event == "Stop program":
        print('Program terminated !')
        break
    doClick = values[0]
    doScroll = values[1]
    
    frame = cv2.flip(frame, 1)
    handFrame = detector.findHand(frame, drawHand)
    posList = detector.getPosition(frame, 0)
    cv2.rectangle(frame, (trackRegionX, trackRegionY), (trackRegionX +
                  trackRegionW, trackRegionY+trackRegionH), (255, 0, 0), 3)
    cv2.putText(frame, 'Relative cursor position', (trackRegionX, trackRegionY-10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 100), 2)
    ############
    clickInterval +=1
    if len(posList) != 0:
        cv2.circle(
            frame, (posList[targetId][1], posList[targetId][2]), 10, (181, 80, 13), cv2.FILLED)
        # Converting coordinate:
        mousePosx = np.interp(
            posList[targetId][1], (trackRegionX, trackRegionX+trackRegionW), (0, sw))
        mousePosy = np.interp(
            posList[targetId][2], (trackRegionY, trackRegionY+trackRegionH), (0, sh))
        # Smoothening coordinate value (create threshold to ignore slight shifts)
        currX = prevX + (mousePosx-prevX)/smoothen
        currY = prevY + (mousePosy-prevY)/smoothen
        # print(mousePosx,mousePosy)
        autopy.mouse.move(currX, currY)
        if doClick:
            # if y of index finger's tip is lower than its knucle => left click
            if posList[8][2] > posList[7][2]:
                if holdTime < 15:
                    if lclicked == False:
                        if clickInterval < 10:
                            autopy.mouse.click()
                            autopy.mouse.click()
                            print('double clicked')
                        else:
                            autopy.mouse.click()
                            print('left clicked')
                            lclicked = True
                            clickInterval = 0;
                    holdTime += 1

                else:
                    if held == False:
                        autopy.mouse.toggle(button = autopy.mouse.Button.LEFT, down = True)
                        print('mouse held')
                        held = True
            else:
                if lclicked == True or held == True:
                    autopy.mouse.toggle(button = autopy.mouse.Button.LEFT, down = False)
                    print('mouse released')
                    holdTime = 0
                    held = False
                    lclicked = False
            # if x of thumb tip is to the right of index mcp => right click
            if posList[12][2] > posList[11][2]:
                if rclicked == False:
                    autopy.mouse.click(autopy.mouse.Button.RIGHT)
                    rclicked = True
                    print('right clicked')
            else:
                if rclicked == True:
                    rclicked = False
                    #print('right click reset')
        if doScroll:
            if posList[4][1] < posList[5][1]:
                if scrolled == False:
                    pyautogui.scroll(-300)
                    scrolled = True
                    print('Scrolled down')
            else:
                if scrolled == True:
                    scrolled = False
                    #print('reset scroll')
        prevX, prevY = currX, currY
########
    # Displaying fps:
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(frame, str(int(fps)), (10, camH-50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow('Camera', frame)

cv2.destroyAllWindows()
time.sleep(1)
gui.close()

## Created by Le Hoang Long - 2022
# https://www.facebook.com/lehoanglong155046
# https://github.com/LongLeGL