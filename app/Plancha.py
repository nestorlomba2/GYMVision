from math import floor
from msilib.schema import SelfReg
from typing_extensions import Self
from .PoseModule import poseDetector
import time


class plancha:
    
    VISIBILITY_THRESHOLD = 0.6
    
    def __init__(self, num_rep=8, series = 3):
        self.E_Sig = 0        
        self.num_rep = num_rep
        self.data = {
            "errors": [],
            "errorsFrase": [],
            "count" : 0,
            "E_Actual" : 0,
            "Exercise_id": 3,
            "complete": False,
            "series": series,
        }   

        # creamos el vector de errores para la ia
        """
        self.repetitions = []
        for index in range(self.num_rep + 1):   
            repetition = {
                "error1": "",
                "error2": "",
                "error3": "",
                "error4": "",
                "error5": "",
                "error6": "",
                "error7": "",
                "error8": "",
                "error9": "",
            }
            self.repetitions.append(repetition)
        
        """

    def plancha_function(self, landmarks):
        
        #creo un objeto detector que tendrá las funciones para procesar los landmarks
        detector = poseDetector()
        #limpio el vector de errores
        self.data['errors'].clear()
        self.data['errorsFrase'].clear()
###########Variables de inicio de la maquina de estados##############3
        codo = 0
        cadera = 0
        rodilla = 0

        ##########################################INITIAL LOOP#################################################
        if self.data['series'] != 0:                            #si quedan series por hacer
            if self.data['count'] < self.num_rep:              #si quedan repeticiones por hacer        
                # el findPosition nos devuelve la posicion de los puntos en pixels
                lmList = detector.findPosition(480, 480, landmarks)   
                visibilityOK =  landmarks[11]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[13]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[15]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[23]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[25]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[27]['visibility']>self.VISIBILITY_THRESHOLD
                                
                if len(lmList) != 0 and visibilityOK:
                                              
                    hombroCaderaRodilla = detector.findAngle( 11, 23, 25)
                    hombroCodoMano = detector.findAngle( 11, 13, 15)
                    CaderaRodillaPie = detector.findAngle( 23, 25, 27)

                    ########################################CORRECCIONES DE ERRORES########################################                  
                    if abs(hombroCodoMano) > 105 or abs(hombroCodoMano) < 80:
                        self.data['errors'].append(13)# Error reflejado en codo 
                        self.data['errorsFrase'].append("Mantén los codos a 90º 😎")
                    else : codo = 1 #si no ha habido ningun error codo correcto

                    if abs(hombroCaderaRodilla) > 190 or abs(hombroCaderaRodilla) < 150:
                        self.data['errors'].append(23)
                        self.data['errorsFrase'].append("Mantén la cadera recta 😄")
                    else : cadera = 1 #si no ha habido ningun error cadera correcto

                    if abs(CaderaRodillaPie) > 190 or abs(CaderaRodillaPie) < 150:
                        self.data['errors'].append(23)
                        self.data['errorsFrase'].append("No descuides las rodillas 😜​")
                    else : rodilla = 1

                    if codo == 1 and cadera == 1 and rodilla ==1:
                        #####################################MAQUINA DE ESTADOS##########################################
                        self.data['E_Actual'] = 1
                        E_text = "Haciendo Plancha"

                        #inicio el contador 
                        if self.inicio==0:
                            self.inicio = time.time()-self.data['count']                             
                        
                        self.data['count'] = round(time.time()-self.inicio)

                    else: #Alguna de las tres variables de control es igual a 0
                        self.inicio = 0
                        self.data['E_Actual'] = 0
            else: 
                
                self.data['series'] -=  1 
                self.data['count'] = 0
                self.inicio = 0
        else:
            self.data['complete'] = True
