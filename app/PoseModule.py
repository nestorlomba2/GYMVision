import math
import time

import cv2
import mediapipe as mp
import numpy as np
from numpy.linalg import norm

"""
minimo código requerido para hacer funcionar esto
Aporta modularidad
"""

# creamos la clase poseDetector


class poseDetector:

    # definimos el método init (inicializa)
    def __init__(self):
        self.counter = 2

    

    def findPosition(self, width: 480, heigh: 480, landmarks):
        """
        Uso: Busca la posición de un punto mediapipe en el frame (su pos. x e y )
        Inputs:
            self: self
            img: frame de entrada 
            draw: dibuja el punto por encima
        Outputs:
            lmList: lista con tuplas [indice del punto, posicion x, posicion y]
        """
        self.lmList = []
        if landmarks:
            #for id, lm in enumerate(landmarks.landmark):
            for id, lm in enumerate(landmarks):
                
                cx, cy = int(lm['x'] * width), int(lm['y'] * heigh)
                self.lmList.append([id, cx, cy])
                
        return self.lmList

    def findPosition3D(self, img, draw=True):
        """
        Uso: Devuelve la posición de los puntos mediapipe en world-3D coordinates 
        Inputs:
            self: self
            img: frame de entrada 
            draw: imprime por pantalla la posición de los puntos
        Outputs:
            lmList3D: lista con tuplas [indice del punto, posicion x, posicion y, posicion z]
        """
        self.lmList3D = []
        if self.results.pose_world_landmarks:
            for id, lm in enumerate(self.results.pose_world_landmarks.landmark):

                # print(id, lm)
                cx, cy, cz = lm.x, lm.y, lm.z
                self.lmList3D.append([id, cx, cy, cz])
                if draw:
                    print("id: " + str(id) + ", pos: " + str(cx) + " " + str(cy) + " " + str(cz))

        return self.lmList3D

    def findAngle3D(self, img, p1, p2, p3, draw=True):
        """
        [WIP] Devuelve el ángulo teniendo en cuenta las 3DWorld coordinates
        Util para tomar medidas de ángulos desde diferentes posiciones
        """

        x1, y1, z1 = self.lmList3D[p1][1:]
        x2, y2, z2 = self.lmList3D[p2][1:]
        x3, y3, z3 = self.lmList3D[p3][1:]

        vect1 = (x3 - x2, y3 - y2, z3 - z2)
        vect2 = (x1 - x2, y1 - y2, z1 - z2)

        c = np.dot(vect1, vect2) / norm(vect1) / norm(vect2)
        angle3D = np.arccos(np.clip(c, -1, 1)) * 57.32484
        if draw:
            print(str(angle3D))

        return angle3D

    def findAngle(self, p1, p2, p3):
        """
        Uso: Devuelve el ángulo entre tres puntos mediapipe
        Inputs:
            self: self
            img: frame de entrada
            p1: punto mediapipe 1
            p2: punto mediapipe 2
            p3: punto mediapipe 3 
            draw: True si dibujar ángulo
        """
        # Get the landmarks
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        # Calculate the angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        # print(angle)
        
        if angle > 180:
            angle = 360 - angle

        if angle <= 0:
            angle = -angle
        
        return angle
        

def main():
    cap = cv2.VideoCapture("PoseVideos/Video.mp4")
    # para calcular los fps
    pTime = 0
    detector = poseDetector()
    while True:

        # img será nuestro frame, que por defecto viene en BGR, por lo que se cambia a RGB
        success, img = cap.read()
        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            print(lmList[14])
            cv2.circle(img, (lmList[14][1], lmList[14][2]), 15, (0, 0, 255), cv2.FILLED)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        # imprimimos fps por pantalla
        cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        # imshow muestra el frame, debe ir acompañado de WaitKey, que siempre es 1 para un ms, 0 para pulsar y sgte
        cv2.imshow("Image", img)
        cv2.waitKey(10)


# para hacerlo modular
if __name__ == "__main__":
    main()
