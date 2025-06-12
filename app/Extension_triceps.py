from .PoseModule import poseDetector


class extension_triceps:
    
    VISIBILITY_THRESHOLD = 0.6
    
    def __init__(self, num_rep=8, series = 3):

           
        self.E_Sig = 0        
        self.num_rep = num_rep
        self.data = {
            "errors": [],
            "errorsFrase": [],
            "count" : 0,
            "E_Actual" : 0,
            "Exercise_id": 5,
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

    def extension_triceps_function(self, landmarks):
        
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
                visibilityOK =  landmarks[8]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[12]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[14]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[16]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[24]['visibility']>self.VISIBILITY_THRESHOLD
                                
                if len(lmList) != 0 and visibilityOK:
                    
                    hombroCodoMano = detector.findAngle(12, 14, 16)
                    caderaHombroOreja = detector.findAngle( 24, 12, 8)
                    hombroCodoCadera = detector.findAngle(12, 14, 24)

                    ########################################CORRECCIONES DE ERRORES########################################                  
                    
                    
                    if caderaHombroOreja <= 150 or caderaHombroOreja >= 190:                    
                        self.data['errorsFrase'].append('Mantén la cabeza recta 🧛‍♀️')
                        self.data['errors'].append(0)

                    # comprobación de la altura del codo                    
                    if hombroCodoCadera <= 110 or hombroCodoCadera >= 170:                    
                        self.data['errorsFrase'].append('El codo debe estar a la altura del cuerpo 👵')
                        self.data['errors'].append(14)

                    if hombroCodoMano <= 80:                    
                        self.data['errorsFrase'].append('No adelantes el brazo al bajar 😋')
                        self.data['errors'].append(16)


                    #####################################MAQUINA DE ESTADOS##########################################
                    self.data['E_Actual'] = self.E_Sig

                    if self.data['E_Actual'] == 0 and hombroCodoMano > 90:
                        self.E_Sig = 1
                    elif self.data['E_Actual'] == 1 and hombroCodoMano > 165:
                        self.E_Sig = 2
                    elif self.data['E_Actual'] == 2 and hombroCodoMano < 165:
                        self.E_Sig = 3
                    elif self.data['E_Actual'] == 3 and hombroCodoMano < 90:
                        self.data["count"] += 1
                        self.E_Sig = 0

                    else:
                        self.E_Sig = self.data['E_Actual']  # El estado se mantiene

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