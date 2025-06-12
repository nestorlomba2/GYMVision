from itertools import count
from .PoseModule import poseDetector


class elevaciones_laterales:
    
    VISIBILITY_THRESHOLD = 0.6
    
    def __init__(self, num_rep=8, series = 3):

        self.E_Sig = 0       
        self.num_rep = num_rep
        self.data = {
            "errors": [],
            "errorsFrase": [],
            "count" : 0,
            "E_Actual" : 0,
            "Exercise_id": 7,
            "complete": False,
            "series": series
        }

        # creamos el vector de errores para la ia
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

    def elevaciones_laterales_function(self, landmarks):
            #creo un objeto detector que tendrá las funciones para procesar los landmarks
        detector = poseDetector()
        #limpio el vector de errores
        self.data['errors'].clear()
        self.data['errorsFrase'].clear()

        ##########################################INITIAL LOOP#################################################
        if self.data['series'] != 0:                            #si quedan series por hacer
            if self.data['count'] < self.num_rep:              #si quedan repeticiones por hacer                    
                # el findPosition nos devuelve la posicion de los puntos en pixels
                lmList = detector.findPosition(480, 480, landmarks)
                visibilityOK =  landmarks[11]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[12]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[13]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[15]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[16]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[23]['visibility']>self.VISIBILITY_THRESHOLD
                                
                if len(lmList) != 0 and visibilityOK:
                                              
                    angulo_hombro_izq = detector.findAngle(23, 11, 13)
                    angulo_codo_der = detector.findAngle(12, 14, 16)
                    angulo_codo_izq = detector.findAngle(11, 13, 15)


                    ####################################MAQUINA DE ESTADOS##########################################
                    self.data['E_Actual'] = self.E_Sig

                    if self.data['E_Actual'] == 0 and abs(angulo_hombro_izq) > 30 and abs(angulo_hombro_izq) < 60:
                        self.E_Sig = 1
                    elif self.data['E_Actual'] == 1 and abs(angulo_hombro_izq) > 100:
                        self.E_Sig = 2
                        self.data["count"] += 1
                    elif self.data['E_Actual'] == 2 and abs(angulo_hombro_izq) < 100 and abs(angulo_hombro_izq) > 30:
                        self.E_Sig = 3
                        
                    elif self.data['E_Actual'] == 3 and abs(angulo_hombro_izq) < 30:
                        self.E_Sig = 0
                    else:
                        self.E_Sig = self.data['E_Actual']

                    

                    if self.data['E_Actual'] == 0:
                        E_text = "Abajo"
                    if self.data['E_Actual'] == 1:
                        E_text = "Subiendo"
                    if self.data['E_Actual'] == 2:
                        E_text = "Arriba"
                    if self.data['E_Actual'] == 3:
                        E_text = "Bajando"

                    #############################################CORRECCIONES DE ERRORES#################################
                    
                    if abs(angulo_codo_izq) < 165 or abs(angulo_codo_izq) > 190:
                    
                        self.data['errors'].append(13)
                        self.data['errorsFrase'].append("Los codos deben mantenerse rectos 🏄‍♂️")

                    if abs(angulo_codo_der) < 165 or abs(angulo_codo_der) > 190:
                        self.data['errorsFrase'].append("Los codos deben mantenerse rectos 🏄‍♀️")
                        
                        self.data['errors'].append(14)



                    self.data['E_Actual'] = self.E_Sig

                    if self.data['E_Actual'] == 0 and abs(angulo_hombro_izq) > 30 and abs(angulo_hombro_izq) < 60:
                        self.E_Sig = 1
                    elif self.data['E_Actual'] == 1 and abs(angulo_hombro_izq) > 100:
                        self.E_Sig = 2
                        self.data["count"] += 1
                    elif self.data['E_Actual'] == 2 and abs(angulo_hombro_izq) < 100 and abs(angulo_hombro_izq) > 30:
                        self.E_Sig = 3
                        
                    elif self.data['E_Actual'] == 3 and abs(angulo_hombro_izq) < 30:
                        self.E_Sig = 0
                    else:
                        self.E_Sig = self.data['E_Actual']

                    

                    if self.data['E_Actual'] == 0:
                        E_text = "Abajo"
                    if self.data['E_Actual'] == 1:
                        E_text = "Subiendo"
                    if self.data['E_Actual'] == 2:
                        E_text = "Arriba"
                    if self.data['E_Actual'] == 3:
                        E_text = "Bajando"

                   
            else: 
                
                self.data['series'] = self.data['series'] - 1 
                self.data['count'] = 0
        else: 
            self.data['complete'] = True

