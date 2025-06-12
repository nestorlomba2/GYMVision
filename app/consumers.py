from email import message
#from tkinter import E
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Repeticion

from app import Biceps_curl
from app.models import Room
from app import Elevaciones_frontales
from app import Elevaciones_laterales
from app import Extension_triceps
from app import Sentadillas
from app import Plancha
from app import Zancadas


class ChatConsumer(AsyncJsonWebsocketConsumer):

    @sync_to_async
    def delete_room(self,room_name):
        room = Room.objects.get(nombre=room_name)
        room.delete()
        print('Deleted room: ', room_name)
    
    async def connect(self):
        # cogemos el nombre del grupo por parámetros
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name  # nombre de la sala

        await self.channel_layer.group_add(  # añadimos el grupo
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if(len(self.channel_layer.groups.get(self.room_group_name,{}).items())==1):
            await self.delete_room(self.room_name)
            
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        print('Disconnected!')

    async def receive(self, text_data):  # receive from clients
        receive_dict = json.loads(text_data)
        message = receive_dict['message']
        action = receive_dict['action']

        if (action == 'new-offer') or (action == 'new-answer'):
            receiver_channel_name = receive_dict['message']['receiver_channel_name']
            receive_dict['message']['receiver_channel_name'] = self.channel_name
            await self.channel_layer.send(
                receiver_channel_name,   # se lo enviamos solo a uno
                {
                    'type': 'send.sdp',     # llamada al método send_sdp
                    'receive_dict': receive_dict
                }
            )
            return

        # handle WebRTC messages
        receive_dict['message']['receiver_channel_name'] = self.channel_name

        await self.channel_layer.group_send(    # estableces a quién envias el mensaje (broadcast al grupo)
            self.room_group_name,
            {
                'type': 'send.sdp',     # llamada al método send_sdp
                'receive_dict': receive_dict
            }
        )

    async def send_sdp(self, event):   # enviar un mensaje
        receive_dict = event['receive_dict']

        await self.send(text_data=json.dumps(receive_dict))



class CorreccionConsumer(AsyncJsonWebsocketConsumer):

    #inicializamos los objetos de todos los ejercicios con un valor por defecto de repeticiones y series 
    exerBicepsCurl = Biceps_curl.biceps_curl()
    exerElevacionesFrontales = Elevaciones_frontales.elevaciones_frontales()
    exerElevacionesLaterales = Elevaciones_laterales.elevaciones_laterales()
    exerExtensionTriceps = Extension_triceps.extension_triceps()
    exerPlancha = Plancha.plancha()
    exerZancadas = Zancadas.zancadas()
    exerSentadilla = Sentadillas.sentadillas()

    #inicializamos variables globales que nos servirán más adelante
    ejercicios = []
    contador = 0
    datos = []

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        print('Disconnected!')

    
    @sync_to_async
    def updateReps(self,exercise_id,user_id):
        repeticiones_ejercicio = Repeticion.objects.get(ejercicio=exercise_id, user=user_id)
        repeticiones_ejercicio.repeticiones = repeticiones_ejercicio.repeticiones + 1
        repeticiones_ejercicio.save()
    
        #print("guardadas las repeticiones")
    
    async def receive(self, text_data):  # receive from clients

        #recibimos datos de entrada (los landmarks y el tipo de socket) y declaramos variables como global para 
        #que no cree las variables de nuevo dentro de la funcion, si no que coja las de la clase 
        receive_dict = json.loads(text_data)
        control = receive_dict['control']
        global ejercicios
        global series
        global contador

        global reps
        global datos
        global contadorDevoluciones  

        if(control == 'info'):
            contadorDevoluciones = 0
            #recogemos info de entrada y segmentamos en variables
            datos = receive_dict['datos']
            ejercicios = datos['ejercicios']
            repeticiones = datos['repeticiones']
            series = datos['series']
            #por si hay dudas, contador se usa como iterador para saber el orden de los ejercicios en la rutina, de este modo
            # cuando se esté haciendo el primer ejercicio contador sera igual a 0 y cuando se esté haciendo el tercero, por ejemplo,
            # contador será igual a 2
            contador = 0 
            reps = 0       

            #bucle para, obtenidos los datos de la rutina, indicarle a nuestros objetos de ejercicios las repeticiones y las series, además de reinicializarlos
            #NOTA: La gestión de las repeticiones y series se hace dentro de las clases de cada ejercicio, en el __init__
            for i in ejercicios:
                if i == '1':
                    self.exerSentadilla.__init__(int(repeticiones[int(i)]), int(series))
                elif i == '2':
                    self.exerZancadas.__init__(int(repeticiones[int(i)]), int(series))
                elif i == '3':
                    self.exerPlancha.__init__(int(repeticiones[int(i)]), int(series))
                elif i == '4':
                    self.exerBicepsCurl.__init__(int(repeticiones[int(i)]), int(series))
                elif i == '5':
                    self.exerExtensionTriceps.__init__(int(repeticiones[int(i)]), int(series))
                elif i == '6':
                    self.exerElevacionesFrontales.__init__(int(repeticiones[int(i)]), int(series))
                elif i == '7':
                    self.exerElevacionesLaterales.__init__(int(repeticiones[int(i)]), int(series))

            print("Rutina recibida")

        elif(control == 'landmarks'):

            landmarks = receive_dict['landmarks']
            
            #"Bucle" para ir almacenando repeticiones de cada uno de los ejercicios y rellenando la rutina, cuando un las series
            # y repeticiones de un ejercicio se completan (esto se gestiona dentro de las funciones de ejercicios), se hace un contador ++
            # y se pasa al siguiente ejercicio
            # se sale del bucle cuando todas las series y repeticiones de la rutina terminan 

            if contador < len(ejercicios):

                if ejercicios[contador] == '1':                   
                    self.exerSentadilla.sentadillas_function(landmarks)
                    datos = self.exerSentadilla.data
                    if datos['count'] == 0:
                        reps = 0                   
                    if self.exerSentadilla.data['complete'] == True:
                        reps = 0     
                        contador += 1

                elif ejercicios[contador] == '2':
                    self.exerZancadas.zancadas_function(landmarks)                   
                    datos = self.exerZancadas.data
                    if datos['count'] == 0:
                        reps = 0
                    if self.exerZancadas.data['complete'] == True:
                        reps = 0     
                        contador += 1

                elif ejercicios[contador] == '3':
                    self.exerPlancha.plancha_function(landmarks)                    
                    datos = self.exerPlancha.data
                    if datos['count'] == 0:
                        reps = 0
                    if self.exerPlancha.data['complete'] == True:
                        reps = 0     
                        contador += 1

                elif ejercicios[contador] == '4':
                    self.exerBicepsCurl.biceps_curl_function(landmarks)
                    datos = self.exerBicepsCurl.data
                    if datos['count'] == 0:
                        reps = 0
                    if self.exerBicepsCurl.data['complete'] == True:
                        print("complete")
                        reps = 0     
                        contador += 1

                elif ejercicios[contador] == '5':
                    self.exerExtensionTriceps.extension_triceps_function(landmarks)
                    datos = self.exerExtensionTriceps.data
                    if datos['count'] == 0:
                        reps = 0
                    if self.exerExtensionTriceps.data['complete'] == True:
                        reps = 0     
                        contador += 1

                elif ejercicios[contador] == '6':
                    self.exerElevacionesFrontales.elevaciones_frontales_function(landmarks)                    
                    datos = self.exerElevacionesFrontales.data
                    if datos['count'] == 0:
                        reps = 0
                    if self.exerElevacionesFrontales.data['complete'] == True:
                        reps = 0     
                        contador += 1

                elif ejercicios[contador] == '7':
                    self.exerElevacionesLaterales.elevaciones_laterales_function(landmarks)                    
                    datos = self.exerElevacionesLaterales.data
                    if datos['count'] == 0:
                        reps = 0                    
                    if self.exerElevacionesLaterales.data['complete'] == True:
                        reps = 0     
                        contador += 1


          # ACTUALIZAR USER ID
          # ESTO HAY QUE PROBARLO, PERO GUARDARIA LAS REPETICIONES DE CADA EJERCICIO PARA ACTUALIZAR LOS RETOS

                if ((datos['count'] != 0) and (datos['count'] != reps)):
                    reps = reps +1
                    user_id = self.scope['url_route']['kwargs']['user_id']
                    exercise_id = ejercicios[contador]
                    await self.updateReps(exercise_id, user_id)

                
                if contadorDevoluciones == 10:
                    # print(contadorDevoluciones)
                    await self.channel_layer.send(    # estableces a quién envias el mensaje (al propio canal)
                        self.channel_name,
                        {
                            'type': 'send.result',     # llamada al método send_result
                            'receive_dict': datos
                        }
                    )
                    contadorDevoluciones = 0

                else:
                    contadorDevoluciones += 1
            
            else: 
                # print("rutina finalizada")
                
                rutinaAcabada= {
                    "errors": [],
                    "errorsFrase": [],
                    "count" : 0,
                    "E_Actual" : 0,
                    "Exercise_id": -1,
                    "complete": False,
                    "series": 0
                }
                await self.channel_layer.send(    # estableces a quién envias el mensaje (al propio canal)
                        self.channel_name,
                        {
                            'type': 'send.result',     # llamada al método send_result
                            'receive_dict': rutinaAcabada
                        }
                    )

    async def send_result(self, event):   # enviar un mensaje
        receive_dict = event['receive_dict']
        await self.send(text_data=json.dumps(receive_dict))
