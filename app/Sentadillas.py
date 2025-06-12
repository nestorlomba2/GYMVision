from .PoseModule import poseDetector

class sentadillas:
    
    VISIBILITY_THRESHOLD = 0.6

    def __init__(self, num_rep=8, series=3):

        self.E_Sig = 0        
        self.num_rep = num_rep
        self.data = {
            "errors": [],
            "errorsFrase": [],
            "count" : 0,
            "E_Actual" : 0,
            "Exercise_id": 1,
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

    def sentadillas_function(self, landmarks):

        #creo un objeto detector que tendrá las funciones para procesar los landmarks
        detector = poseDetector()
        #limpio el vector de errores
        self.data['errors'].clear()
        self.data['errorsFrase'].clear()
        ##########################################INITIAL LOOP#################################################
        if self.data['series'] != 0:                        #si quedan series por hacer
            if self.data['count'] < self.num_rep:          #si quedan repeticiones por hacer
                # el findPosition nos devuelve la posicion de los puntos en pixels
                lmList = detector.findPosition(480, 480 , landmarks)
                visibilityOK =  landmarks[12]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[24]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[26]['visibility']>self.VISIBILITY_THRESHOLD and \
                                landmarks[28]['visibility']>self.VISIBILITY_THRESHOLD
                                
                if len(lmList) != 0 and visibilityOK:
                    
                    caderaRodillaPieDer = detector.findAngle(24, 26, 28)
                    hombroCaderaRodilla = detector.findAngle(12, 24, 26)
                    
                    ########################################CORRECCIONES DE ERRORES########################################                  
                    
                    #control de la espalda
                    if landmarks[26]['x'] > landmarks[32]['x'] + 0.03:
                        self.data['errors'].append(26)
                        self.data['errorsFrase'].append("Las rodillas no deben superar las puntas de los pies 🦵")

                    #control de la espalda
                    if hombroCaderaRodilla <= 60:
                        
                        self.data['errors'].append(24)
                        self.data['errorsFrase'].append('Mantén la espalda recta 🤪')

                    ########################################CORRECCIONES DE ERRORES########################################

                    #####################################MAQUINA DE ESTADOS##########################################                 
                    self.data['E_Actual'] = self.E_Sig
                    # Elegir estado siguiente y salidas dependiendo del estado actual y entradas
                    if self.data['E_Actual'] == 0 and caderaRodillaPieDer < 160:
                        self.E_Sig = 1
                    elif self.data['E_Actual'] == 1 and caderaRodillaPieDer < 90:
                        self.E_Sig = 2
                        self.data["count"] += 1
                    elif self.data['E_Actual'] == 2 and caderaRodillaPieDer > 100:
                        self.E_Sig = 3
                    elif self.data['E_Actual'] == 3 and caderaRodillaPieDer > 170:
                        self.E_Sig = 0
                    else:
                        self.E_Sig = self.data['E_Actual']  # El estado se mantiene

                    if self.data['E_Actual'] == 0:
                        E_text = "Arriba"
                    if self.data['E_Actual'] == 1:
                        E_text = "Bajando"
                    if self.data['E_Actual'] == 2:
                        E_text = "Abajo"
                    if self.data['E_Actual'] == 3:
                        E_text = "Subiendo"
                    
                    ###############################################################################

            else:                
                self.data['series'] = self.data['series'] - 1 
                self.data['count'] = 0
        else: 
            self.data['complete'] = True