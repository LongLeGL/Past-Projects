import cv2
from numpy import True_
import mediapipe as mp

class handDetector:
    def __init__(self,mode = False, maxHands = 1, complexity = 1, detectCon = 0.5, trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.complexity = complexity
        self.detectCon = detectCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hand = self.mpHands.Hands(self.mode,self.maxHands,self.complexity,self.detectCon,self.trackCon)
        self.drawHand = mp.solutions.drawing_utils
    def findHand(self, frame, draw = False):
        self.foundHand = self.hand.process(frame)
        if self.foundHand.multi_hand_landmarks: #Hand(s) detected
            for aHand in self.foundHand.multi_hand_landmarks:
                if draw:
                    self.drawHand.draw_landmarks(frame,aHand, self.mpHands.HAND_CONNECTIONS)
        return frame
    def getPosition(self, frame, handNo=0):  #return list of positions for each landmark
        lmList = []
        if self.foundHand.multi_hand_landmarks:
            if len(self.foundHand.multi_hand_landmarks)>1:  #handNo = 0:left, =1:right when multiple hands are detected
                currentHand =  self.foundHand.multi_hand_landmarks[handNo]
            else: 
                currentHand =  self.foundHand.multi_hand_landmarks[0]
            for id, lm in enumerate(currentHand.landmark): #id is andmark[0-21] on a hand
                h, w, ch = frame.shape
                #Coordinate of each landmark in the frame:
                x = int(lm.x*w)
                y = int(lm.y*h)
                lmList.append([id,x,y])
        return lmList
#Function to solely run the module for testing:
def main():
    cap = cv2.VideoCapture(0)
    cap.set(3,960)
    cap.set(4,540)
    detector = handDetector()
    targetId = 8    #tip of index finger
    while True:
        isSucess, frame = cap.read()
        handFrame = detector.findHand(frame,True)
        posList = detector.getPosition(frame,1)
        if len(posList) != 0:
            cv2.circle(frame,(posList[targetId][1],posList[targetId][2]),10,(181,80,13),cv2.FILLED)
        cv2.imshow('Camera',handFrame)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            break

if __name__ == "__main__":
    main()