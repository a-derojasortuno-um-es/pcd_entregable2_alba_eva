from datetime import datetime
import time
from random import randint
from functools import reduce
import numpy as np
import statistics
from statistics import mean,stdev

#Clases de OBSERVER
#PUBLICADOR

class Publicador: 
    def __init__(self):
        self._suscriptor = Sistema.obtener_instancia() # el sistema siempre será el suscriptor.
     
    # No hará falta el método delete ni add suscriptor porque el sistema siempre estará suscrito a las notificiones del sensor.

    def notificar_sub(self, registro): 
        self._suscriptor.actualizar(registro)


class SensorTemp(Publicador): 
    def __init__(self):
        super().__init__() # se hereda al suscriptor.
    
    def fijar_temp(self, registro): 
        self.notificar_sub(registro)
    

#Clases CHAIN OF RESPONSIBILITY ---------
#SUSCRIPTOR Y MANEJADOR
class Sistema: 
    _unicaInstancia = None
    def __init__(self, sucesor = None):
        self.sucesor = sucesor
        self._datos_temp = []
    
    #Método por patrón Singleton
    @classmethod
    def obtener_instancia(cls):
        if not cls._unicaInstancia :
            cls._unicaInstancia = cls()
        return cls._unicaInstancia
    
    def calculo(self,orden,datos):
        pass

    def actualizar(self,registro): 
        try:
            print(f"El sistema ha recibido un valor de temperatura de {registro[1]}ºC en la fecha {registro[0]}")

            print("Se procede a realizar los cálculos...")

            self._datos_temp.append(registro)

            datos = self._datos_temp

   
            aumento = AumentoTemp()

            umbral = Umbral(aumento)

            calculos = CalculoEstadisticos()

            fin = False
            while fin == False:

                opcion = int(input("Seleccione el estadístico que desea obtener sobre la temperatura \n 1 - Media y desviación típica \n 2 - Cuantiles \n 3 - Temperatura máxima y mínima\n"))
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
        
            time.sleep(5)

            calculos.calculo(1,datos) # cálculos estadísticos.
            calculos.calculo(2,datos) # umbral.
            calculos.calculo(3,datos) # incremento.
        except TypeError:
            print("La temperatura recibida no es del tipo int o float. Vuelve a introducir una temperatura válida.")

    
#STRATEGY-----------
class CalculoEstadisticos(Sistema): 
    def __init__(self,sucesor=None):
        self.estrategia = None 
        self.sucesor = sucesor
    
    def set_estrategia(self,estrategia):
        self.estrategia = estrategia

    def calculo(self,orden,datos):
        self.estrategia.calculo(orden,datos)


class mediaDesviacion(Sistema): 
    def calculo(self,orden,datos):
        if orden == 1:
            if len(datos) < 12:
                print('Aún no se puede hacer el cálculo de la media y la desviación típica porque no se han recogido los suficientes datos.')
            else:
                T = datos[-12:]
                d = [i[1] for i in T] #lista sin fechas

                media = reduce(lambda x, y: x+y, d)/len(d)
                print('Temperatura media: ', round(media,2))

                desviacion = np.sqrt(sum(map(lambda x: (x-media)**2,d))/(len(d)-1))
                print('Desviación típica: ', round(desviacion,2) )

        elif self.sucesor:
            self.sucesor.calculo(orden,datos)

class cuantiles(Sistema):
    def calculo(self,orden,datos):
        if orden == 1:
            if len(datos) < 12:
                print('Aún no se puede hacer el cálculo de los cuantiles porque no se han recogido los suficientes datos.')
            else:
                T = datos[-12:]
                d = [i[1] for i in T]
                cuantiles = statistics.quantiles(d, n=4)
                print(f"El primer cuantil del 25% es {cuantiles[0]}, el que reúne el 50% de los datos es {cuantiles[1]} y el que divide los datos en un 75% es {cuantiles[2]}")

        elif self.sucesor:
            self.sucesor.calculo(orden,datos)

class ValoresMaxMin(Sistema):
    def calculo(self,orden,datos):
        if orden == 1:
            if len(datos) < 12:
                print('Aún no se puede hacer el cálculo de los valores máximos y mínimos porque no se han recogido los suficientes datos.')
            else:
                T = datos[-12:]
                d = [i[1] for i in T]
                maximo = reduce(lambda x,y:x if (x>y) else y,d)
                minimo = reduce(lambda x,y:x if (x<y) else y,d)
                print(f'Max:{maximo}ºC\nMin:{minimo}ºC')

                
        elif self.sucesor:
            self.sucesor.calculo(orden,datos)

#FIN STRATEGY-----------------

class Umbral(Sistema):
    def calculo(self,orden,datos):
        if orden == 2:
            temp = datos[-1] # última temperatura registrada
            dato = [temp[1]] #nos quedamos solo con el valor de temp y en formato lista
            umbral = len(list(filter(lambda x: x >= 30.2,dato)))==1 
            if umbral:
                print(f"La temperatura actual de {dato[0]}ºC sobrepasa el umbral de temperatura de 30.2ºC.")
            else:
                print(f"La temperatura actual de {dato[0]}ºC NO sobrepasa el umbral de temperatura de 30.2ºC.")

        elif self.sucesor:
            self.sucesor.calculo(orden,datos)

class AumentoTemp(Sistema): # últimos 30s (6 últimos puestos de la lista)
    def calculo(self,orden,datos):
        if len(datos) < 6: 
            print('Aún no se puede hacer el cálculo del incremento de temperatura porque no se han recogido los suficientes datos.\n')
        else:
            if orden == 3:
                T = datos[-6:]
                d = [i[1] for i in T] # nos quedamos con las 6 últimas temperaturas solamente.
                # Se calculan todos los incrementos de la temperatura anterior con la siguiente.
                incrementoT = list(map(lambda x:abs(d[x+1]-d[x]),range(len(d)-1)))
                tempbruscas = len(list(filter(lambda x: x>10,incrementoT)))>0
                if tempbruscas:
                    print('Aumento de la temperatura detectado.')

            elif self.sucesor:
                self.sucesor.calculo(orden,datos)

# -----FIN DEL CHAIN OF RESPONSIBILITY-----


# TEST UNITARIOS

L = [1.5,2.2,4,14.7,27.4,31.3,24.7,34.8,]

# Se comprueba si el cálculo de la media y la desviación es correcto.

def media_desviacion(L):
    media = reduce(lambda x, y: x+y, L)/len(L)
    desviacion = np.sqrt(sum(map(lambda x: (x-media)**2,L))/(len(L)-1))
    return media,desviacion
   
def test_media():
    media,desviacion = media_desviacion(L)
    assert media == mean(L)
    assert desviacion == stdev(L)

# El cálculos de los cuantiles como se ha hecho con la librería stadistics no hará falta comprobarlo.

def max_min(L):
    maximo = reduce(lambda x,y:x if (x>y) else y,L)
    minimo = reduce(lambda x,y:x if (x<y) else y,L)
    return maximo,minimo

def test_max_min():
    maximo,minimo = max_min(L)
    assert maximo == max(L)
    assert minimo == min(L)


def incremento(L):
    incrementoT = list(map(lambda x:abs(L[x+1]-L[x]),range(len(L)-1)))
    tempbruscas = len(list(filter(lambda x: x>10,incrementoT)))>0
    return tempbruscas


def test_incremento():
    assert incremento(L) == True # como sí hay incremento, la lista no debe estar vacía.


def umbral(L):
    umbral = len(list(filter(lambda x: x >= 30.2,L)))>0 # se modifica la función para que recoja todas las temperaturas que superan el umbral,
    # porque tiene como parámetro de entrada una lista en vez de una temperatura solo. 
    return umbral

def test_umbral():
    assert umbral(L) == True # como hay varias temperaturas que superan el umbral debería ser True.



if __name__ == '__main__':
    sensor = SensorTemp()
    i = 0
    continuar = True
    while i < 500 and continuar:
        fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        temp = randint(5,40)
        tupla_temp = (fecha,temp)
        sensor.fijar_temp(tupla_temp)
        continuar = bool(int(input("¿Deseas continuar incluyendo datos?\n Si desea continuar pulse 1, si no, pulse 0.\n")))














