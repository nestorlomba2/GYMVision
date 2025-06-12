from .PoseModule import poseDetector


class elevaciones_frontales:
    
    VISIBILITY_THRESHOLD = 0.4
    
    def __init__(self, num_rep=8, series = 3):

        self.num_rep = num_rep
        self.E_Sig = 0
        self.data = {
            "errors": [],
            "errorsFrase": [],
            "count" : 0,
            "E_Actual" : 0,
            "Exercise_id": 6,
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

    def elevaciones_frontales_function(self,landmarks):
        
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
                visibilityOK =  landmarks[0]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[12]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[16]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[24]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[26]['visibility']>self.VISIBILITY_THRESHOLD
                                
                if len(lmList) != 0 and visibilityOK:

                    ######################################CONTADORES DE REPETICIONES#######################################
                    
                    manoHombroCaderaDer = detector.findAngle( 16, 12, 24)
                    manoHombroCaderaIzq = detector.findAngle(15, 11, 23)
                    narizHombroCadera = detector.findAngle(0, 12, 24)
                    hombroCaderaRodilla = detector.findAngle(12, 24, 26)
                    ########################################CORRECCIONES DE ERRORES########################################

                
                        
                    # control de la posición del cuello
                    if narizHombroCadera <= 125:
                        self.repetitions[int(self.data['count'])]["error2"] = "Cuello hacia delante"
                        self.data['errors'].append(0)
                        self.data['errorsFrase'].append("No adelantes el cuello 😎")

                    # control del balanceo de la espalda                    
                    if hombroCaderaRodilla  <= 165 or hombroCaderaRodilla >= 180:
                        self.repetitions[int(self.data['count'])]["error3"] = "Espalda echada hacia atrás 🙆‍♂️"
                        self.data['errors'].append(24)
                        self.data['errorsFrase'].append("Mantén la espalda recta")
                        
                    #####################################MAQUINA DE ESTADOS##########################################
                    self.data['E_Actual'] = self.E_Sig

                    # brazo derecho
                    if self.data['E_Actual'] == 0 and manoHombroCaderaDer > 20:
                        self.E_Sig = 1
                    elif self.data['E_Actual'] == 1 and manoHombroCaderaDer > 90:
                        self.E_Sig = 2
                    elif self.data['E_Actual'] == 2 and manoHombroCaderaDer < 90:
                        self.E_Sig = 3
                    elif self.data['E_Actual'] == 3 and manoHombroCaderaDer < 20:
                        self.E_Sig = 4
                    elif self.data['E_Actual'] == 4 and manoHombroCaderaIzq < 20:
                        self.E_Sig = 5
                    elif self.data['E_Actual'] == 5 and manoHombroCaderaIzq > 20:
                        self.E_Sig = 6
                    elif self.data['E_Actual'] == 6 and manoHombroCaderaIzq > 90:
                        self.E_Sig = 7
                    elif self.data['E_Actual'] == 7 and manoHombroCaderaIzq < 90:
                        self.E_Sig = 8
                        self.data['count'] += 1
                    elif self.data['E_Actual'] == 8 and manoHombroCaderaIzq < 20:
                        self.E_Sig = 0

                    else:
                        self.E_Sig = self.data['E_Actual']  # El estado se mantiene

                    if self.data['E_Actual'] == 0:
                        E_text = "Abajo izquierdo"
                    if self.data['E_Actual'] == 1:
                        E_text = "Subiendo izquierdo"
                    if self.data['E_Actual'] == 2:
                        E_text = "Arriba  izquierdo"
                    if self.data['E_Actual'] == 3:
                        E_text = "Bajando izquierdo"
                    if self.data['E_Actual'] == 4:
                        E_text = "Ahora con el brazo derecho"
                    if self.data['E_Actual'] == 5:
                        E_text = "Abajo derecho"
                    if self.data['E_Actual'] == 6:
                        E_text = "Subiendo derecho"
                    if self.data['E_Actual'] == 7:
                        E_text = "Arriba derecho"
                    if self.data['E_Actual'] == 8:
                        E_text = "Bajando derecho"
                
            else: 
                
                self.data['series'] = self.data['series'] - 1 
                self.data['count'] = 0 
        
        else: 
            self.data['complete'] = True
