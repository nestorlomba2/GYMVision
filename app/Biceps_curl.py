from itertools import count
from .PoseModule import poseDetector



class biceps_curl:
    
    VISIBILITY_THRESHOLD = 0.6
    
    def __init__(self, num_rep=8, series = 3):

        self.E_Sig = 0        
        self.num_rep = num_rep
        self.data = {
            "errors": [],
            "errorsFrase": [],
            "count" : 0,
            "E_Actual" : 0,
            "Exercise_id": 4,
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

    def biceps_curl_function(self, landmarks):
        
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
                visibilityOK =  landmarks[0]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[12]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[14]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[16]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[24]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[26]['visibility']>self.VISIBILITY_THRESHOLD
                                
                if len(lmList) != 0 and visibilityOK:
                                              
                    hombroCodoMano = detector.findAngle(12, 14, 16)
                    hombroCaderaRodilla = detector.findAngle(12, 24, 26)
                    codoHombroCadera = detector.findAngle(14, 12, 24)
                    narizCodoHombro = detector.findAngle(0, 12, 24)

                    ########################################CORRECCIONES DE ERRORES########################################                  
                    
                    #control de la espalda
                    if hombroCaderaRodilla  <= 165 or hombroCaderaRodilla>= 180:
                        #self.repetitions[int(self.data['count'])]["error1"] = "espalda echada hacia atrás"
                        self.data['errors'].append(24)
                        self.data['errorsFrase'].append("Mantén la espalda recta 😉")

                    # control del "balanceo" del codo 
                    if codoHombroCadera >= 30:
                        #self.repetitions[int(self.data['count'])]["error2"] = "codo adelantado"
                        self.data['errors'].append(14)
                        self.data['errorsFrase'].append("No adelantes los codos 😗")

                    # control de la posición del cuello
                    
                    if narizCodoHombro <= 110:
                        #self.repetitions[int(self.data['count'])]["error3"] = "cuello adelantado"
                        self.data['errors'].append(0)
                        self.data['errorsFrase'].append("No adelantes el cuello 😯")

                    """
                    # control de la posición de las rodillas (actualmente no está en uso por ser poco preciso)

                    angle5 = detector.findAngle(img, 24, 26, 28, True)
                    if angle5 <= 175 or hombroCaderaRodilla >= 180:
                        cv2.putText(
                            img,
                            "flex. rodilla",
                            (lmList[26][1], lmList[26][2]),
                            cv2.FONT_HERSHEY_PLAIN,
                            4,
                            (0, 255, 0),
                            4,
                        )

                        self.repetitions[int(c)]["error4"] = "rodilla no flexionada"
                        cv2.circle(img, (lmList[26][1], lmList[26][2]), 6, (0, 255, 0), 6)
                    """
                    

                    #####################################MAQUINA DE ESTADOS##########################################
                    self.data['E_Actual']= self.E_Sig

                    
                    if  self.data['E_Actual'] == 0 and hombroCodoMano < 160:
                        self.E_Sig = 1
                    elif  self.data['E_Actual'] == 1 and hombroCodoMano < 50:
                        self.E_Sig = 2
                    elif  self.data['E_Actual'] == 2 and hombroCodoMano > 50:
                        self.E_Sig = 3
                        self.data['count'] += 1
                    elif  self.data['E_Actual'] == 3 and hombroCodoMano > 160:
                        self.E_Sig = 0

                    else:
                        self.E_Sig =  self.data['E_Actual']  # El estado se mantiene

                    if  self.data['E_Actual'] == 0:
                        E_text = "Abajo"
                    if  self.data['E_Actual'] == 1:
                        E_text = "Subiendo"
                    if  self.data['E_Actual'] == 2:
                        E_text = "Arriba"
                    if  self.data['E_Actual'] == 3:
                        E_text = "Bajando"

            else: 
                
                self.data['series'] -=  1 
                self.data['count'] = 0
        else:
            self.data['complete'] = True

                
