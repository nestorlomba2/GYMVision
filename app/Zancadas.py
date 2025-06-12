from .PoseModule import poseDetector

class zancadas:
    
    VISIBILITY_THRESHOLD = 0.4

    def __init__(self, num_rep=8, series=3):

        self.num_rep = num_rep
        self.E_Sig = 0
        self.data = {
            "errors": [],
            "errorsFrase": [],
            "count" : 0,
            "E_Actual" : 0,
            "Exercise_id": 2,
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

    def zancadas_function(self,landmarks):
        
        #creo un objeto detector que tendrá las funciones para procesar los landmarks
        detector = poseDetector()
        #limpio el vector de errores
        self.data['errors'].clear()
        self.data['errorsFrase'].clear()
        ##########################################INITIAL LOOP#################################################
        if self.data['series'] != 0:                        #si quedan series por hacer
            if self.data['count'] < self.num_rep:          #si quedan repeticiones por hacer          
                # el findPosition nos devuelve la posicion de los puntos en pixels
                lmList = detector.findPosition(480, 480, landmarks)
                visibilityOK =  landmarks[12]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[24]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[25]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[26]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[28]['visibility']>self.VISIBILITY_THRESHOLD

                                
                if len(lmList) != 0 and visibilityOK:

                    
                    caderaRodillaPieDer = detector.findAngle( 24, 26, 28)

                    # Angulo pierna derecha
                    caderaRodillaPieIzq = detector.findAngle(23, 25, 27)
                    hombroCaderaRodillaIzq = detector.findAngle(11,23,25)
                    hombroCaderaRodillaDer = detector.findAngle(12,24,26)

                    
                    ########################################CORRECCIONES DE ERRORES########################################

                    
                    if landmarks[26]['x'] > landmarks[32]['x'] + 0.03:
                        self.data['errors'].append(26)
                        self.data['errorsFrase'].append("Las rodillas no deben superar las puntas de los pies 🦵")

                    if landmarks[25]['x'] > landmarks[31]['x'] + 0.03:
                        self.data['errors'].append(25)
                        self.data['errorsFrase'].append("Las rodillas no deben superar las puntas de los pies 🦵")

                    if hombroCaderaRodillaIzq <= 90:
                        self.data['errorsFrase'].append("No flexiones el tronco, mantenlo recto 🤸‍♀️")
                        self.data['errors'].append(23)

                    if hombroCaderaRodillaDer <= 90:
                        self.data['errorsFrase'].append("No flexiones el tronco, mantenlo recto 🤸‍♂️")
                        self.data['errors'].append(24)
                        
                    """
                    

                    if angle4 <= 125:
                        self.repetitions[int(self.data['count'])]["error2"] = "Cuello hacia delante"
                        self.data['errors'].append(0)

                    # control del balanceo de la espalda
                    angle5 = detector.findAngle(12, 24, 26)
                    if angle5 >= 195:
                        self.repetitions[int(self.data['count'])]["error3"] = "Espalda echada hacia atrás"
                        self.data['errors'].append(24)
                    """

                    #####################################MAQUINA DE ESTADOS##########################################
                    self.data['E_Actual'] = self.E_Sig

                    # brazo derecho
                    if self.data['E_Actual'] == 0 and caderaRodillaPieDer < 160:
                        self.E_Sig = 1
                    elif self.data['E_Actual'] == 1 and caderaRodillaPieDer < 90:
                        self.E_Sig = 2
                    elif self.data['E_Actual'] == 2 and caderaRodillaPieDer > 90:
                        self.E_Sig = 3
                    elif self.data['E_Actual'] == 3 and caderaRodillaPieDer > 160:
                        self.E_Sig = 4
                    elif self.data['E_Actual'] == 4 and caderaRodillaPieIzq > 160:
                        self.E_Sig = 5
                    elif self.data['E_Actual'] == 5 and caderaRodillaPieIzq < 160:
                        self.E_Sig = 6
                    elif self.data['E_Actual'] == 6 and caderaRodillaPieIzq < 100:
                        self.E_Sig = 7
                    elif self.data['E_Actual'] == 7 and caderaRodillaPieIzq > 100:
                        self.E_Sig = 8
                        self.data['count'] += 1
                    elif self.data['E_Actual'] == 8 and caderaRodillaPieIzq > 160:
                        self.E_Sig = 0

                    else:
                        self.E_Sig = self.data['E_Actual']  # El estado se mantiene

                    if self.data['E_Actual'] == 0:
                        E_text = "Arriba izquierdo"
                    if self.data['E_Actual'] == 1:
                        E_text = "Bajando izquierdo"
                    if self.data['E_Actual'] == 2:
                        E_text = "Abajo  izquierdo"
                    if self.data['E_Actual'] == 3:
                        E_text = "Subiendo izquierdo"
                    if self.data['E_Actual'] == 4:
                        E_text = "Ahora con la pierna derecha"
                    if self.data['E_Actual'] == 5:
                        E_text = "Arriba derecho"
                    if self.data['E_Actual'] == 6:
                        E_text = "Bajando derecho"
                    if self.data['E_Actual'] == 7:
                        E_text = "Abajo derecho"
                    if self.data['E_Actual'] == 8:
                        E_text = "Subiendo derecho"
            
            else: 
                
                self.data['series'] = self.data['series'] - 1 
                self.data['count'] = 0
                    
        else: 
            self.data['complete'] = True