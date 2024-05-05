from datetime import datetime
import time
from abc import ABC, abstractmethod
from random import randint
import functools
import numpy as np
import statistics

class Controlador: # Como el controlador es el sistema, será la clase Observer del patrón Observer.
    _unicaInstancia = None
    def __init__(self):
        # solo hay un suscriptor, el sistema, así que no hará falta ningún susctiptor más.
        self.datos_temp = []
        self.sensor = None
    
    def asignar_sensor(self):
        self.sensor = SensorTemp()
    
    #Método por patrón singleton
    @classmethod
    def obtener_instancia(cls):
        if not cls._unicaInstancia :
            cls._unicaInstancia = cls()
        return cls._unicaInstancia
    
    def obtener_datos(self):
        return self.datos_temp
    
    def fijar_temp(self,registro):
        self.datos_temp.append(registro)
        self.sensor.set_registro(registro)
        time.sleep(5)
    
    def actualizar(self,registro): 
        print(f"El sistema ha recibido un valor de temperatura: {registro[1]} en la fecha {registro[0]}")
    

#Clases de OBSERVER
class Publicador: 
    def __init__(self):
        self._suscriptor = Controlador.obtener_instancia() # el sistema siempre será el suscriptor.
    
                        
    # No hará falta el método delete ni add suscriptor porque el sistema siempre estará suscrito a las notificiones del sensor.

    def notificar_sub(self, registro): 
        self._suscriptor.actualizar(registro)

#Clases de Chain of responsibility-------------
class SensorTemp(Publicador): #MANEJADOR y PUBLICADOR.
    def __init__(self, sucesor=None):
        super().__init__()
        self.sucesor = sucesor
    
    def calculo(self,orden,datos):
        pass
    
    def set_registro(self,registro): 
        self.notificar_sub(registro) # se notifica al sistema
        # se hacen las comprobaciones.

        datos_temp = self._suscriptor.obtener_datos()

        calculos = CalculoEstadisticos()

        primero = Orden(1)
        segundo = Orden(2)
        tercero = Orden(3)

        aumento = AumentoTemp()
        umbral = Umbral(aumento)

        fin = False
        while fin == False:
            opcion = int(input("Seleccione el estadístico que desea obtener de la temperatura durante los ultimos 60s \n 1 - Media y desviación típica \n 2 - Cuantiles \n 3 - Temperatura máxima y mínima\n"))
            if opcion == 1:
                estrategia = mediaDesviacion(umbral)
                calculos.set_estrategia(estrategia)
                fin = True
            elif opcion == 2:
                estrategia = cuantiles(umbral)
                calculos.set_estrategia(estrategia)
                fin = True
            elif opcion == 3:
                estrategia = ValoresMaxMin(umbral)
                calculos.set_estrategia(estrategia)
                fin = True
            else:
                print("Opción incorrecta. Vuelva a intentarlo.")

        
        calculos.calculo(primero,datos_temp) # cálculos estadísticos.
        calculos.calculo(segundo,datos_temp) # umbral.
        calculos.calculo(tercero,datos_temp) # incremento.
         


#STRATEGY-----------
class CalculoEstadisticos(SensorTemp): 
    def __init__(self,sucesor=None):
        self.estrategia = None 
        self.sucesor = sucesor
    
    def set_estrategia(self,estrategia):
        self.estrategia = estrategia

    def calculo(self,orden,datos):
        if len(datos) < 12: 
            print('Recogiendo datos...')
        else:
            self.estrategia.calculo(datos)

class mediaDesviacion(SensorTemp): 
    def calculo(self,orden,datos):
        if orden.nivel == 1:
            #nueva lista con los ultimos 12 datos (60s)
            T = datos[-12:]
            d = [i[1] for i in T] #lista sin fechas

            media = functools.reduce(lambda x, y: x+y, d)/len(d)
            print('Temperatura media: ', round(media,2))

            desviacion = np.sqrt(sum(map(lambda x: (x-media)**2,d))/(len(d)-1))
            print('Desviación típica: ', round(desviacion,2) )

        elif self.sucesor:
            self.sucesor.calculo(datos)

class cuantiles(SensorTemp):
    def calculo(self,orden,datos):
        if orden.nivel == 1:
            T = datos[-12:]
            d = [i[1] for i in T]
            cuantiles = statistics.quantiles(d, n=4)
            print(f"El primer cuantil del 25% es {cuantiles[0]}, el que reúne el 50% de los datos es {cuantiles[1]} y el que divide los datos en un 75% es {cuantiles[2]}")


        elif self.sucesor:
            self.sucesor.calculo(datos)

class ValoresMaxMin(SensorTemp):
    def calculo(self,orden,datos):
        if orden.nivel == 1:
            T = datos[-12:]
            d = [i[1] for i in T]
            print(f'Max:{max(d)}ºC\nMin:{min(d)}ºC')

        elif self.sucesor:
            self.sucesor.calculo(datos)

#FIN STRATEGY-----------------

class Umbral(SensorTemp):
    def calculo(self,orden,datos):
        if orden.nivel == 2:
            temp = datos[-1] # última temperatura registrada
            dato = [temp[1]] #nos quedamos solo con el valor de temp y en formato lista
            umbral = len(list(filter(lambda x: x >= 30.2,dato)))==1 
            if umbral:
                print(f"La temperatura actual de {temp[0]}ºC sobrepasa el umbral de temperatura.")

        elif self.sucesor:
            self.sucesor.calculo(datos)

class AumentoTemp(SensorTemp): #ultimos 30s (6 ultimos puestos de la lista)
    def calculo(self,orden,datos):
        if orden.nivel == 3:
            T = datos[-6:]
            d = [i[1] for i in T] # nos quedamos con las 6 últimas temperaturas solamente.
            # Se calculan todos los incrementos de la temperatura anterior con la siguiente.
            incrementoT = list(map(lambda x:abs(d[x+1]-d[x]),range(len(d)-1)))
            tempbruscas = list(filter(lambda x: x>10,incrementoT))
            if len(tempbruscas)>0:
                print('Aumento de la temperatura detectado.')

        elif self.sucesor:
            self.sucesor.calculo(datos)

class Orden:
    def __init__(self,nivel):
        self.nivel = nivel

#FIN CHAIN OF RESPONSABILITY-------------

#Función que crea el sensor con el orden de tareas indicado y pide la estrategia a aplicar
# def crear_sensor():
#     aumento = AumentoTemp()
#     umbral = Umbral(aumento)

#     opcion = int(input("Seleccione el estadístico que desea obtener de la temperatura durante los ultimos 60s \n 1 - Media y desviación típica \n 2 - Cuantiles \n 3 - Temperatura máxima y mínima"))
#     if opcion == 1:
#         estrategia = mediaDesviacion(umbral)
#     elif opcion == 2:
#         estrategia = cuantiles(umbral)
#     elif opcion == 3:
#         estrategia = ValoresMaxMin(umbral)
#     else:
#         print("Opción incorrecta. Vuelva a intentarlo.")

#     calculos = CalculoEstadisticos(umbral,estrategia)
#     sensor = SensorTemp(calculos)
#     return sensor

if __name__ == '__main__':
    controlador = Controlador.obtener_instancia()
    controlador.asignar_sensor()
    for i in range(500):
        fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        temp = randint(5,40)
        tupla_temp = (fecha,temp)
        controlador.fijar_temp(tupla_temp)










