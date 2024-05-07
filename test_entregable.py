from datetime import datetime
import time
from random import randint
from functools import reduce
import numpy as np
import statistics

#Clases de OBSERVER
#PUBLICADOR

class Publicador: 
    def __init__(self):
        self._suscriptor = Controlador.obtener_instancia() # el sistema siempre será el suscriptor.
    
                        
    # No hará falta el método delete ni add suscriptor porque el sistema siempre estará suscrito a las notificiones del sensor.

    def notificar_sub(self, registro): 
        self._suscriptor.actualizar(registro)


class SensorTemp(Publicador): 
    def __init__(self):
        super().__init__() # se hereda al suscriptor.
    
    def fijar_temp(self, registro): 
        self.notificar_sub(registro)
    

#Clases CHAIN OF RESPONSABILITY ---------
#SUSCRIPTOR Y MANEJADOR
class Controlador: 
    _unicaInstancia = None
    def __init__(self, sucesor = None):
        self.sucesor = sucesor
        self.datos_temp = []
    
    #Método por patrón singleton
    @classmethod
    def obtener_instancia(cls):
        if not cls._unicaInstancia :
            cls._unicaInstancia = cls()
        return cls._unicaInstancia
    
    def calculo(self,orden,datos):
        pass

    def actualizar(self,registro): 
        print(f"El sistema ha recibido un valor de temperatura de {registro[1]}ºC en la fecha {registro[0]}")

        print("Se procede a realizar los cálculos...")

        self.datos_temp.append(registro)
        datos_temp = self.datos_temp

        primero = Orden(1)
        segundo = Orden(2)
        tercero = Orden(3)

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

        calculos.calculo(primero,datos_temp) # cálculos estadísticos.
        calculos.calculo(segundo,datos_temp) # umbral.
        calculos.calculo(tercero,datos_temp) # incremento.
    

    
#STRATEGY-----------
class CalculoEstadisticos(Controlador): 
    def __init__(self,sucesor=None):
        self.estrategia = None 
        self.sucesor = sucesor
    
    def set_estrategia(self,estrategia):
        self.estrategia = estrategia

    def calculo(self,orden,datos):
        self.estrategia.calculo(orden,datos)


class mediaDesviacion(Controlador): 
    def calculo(self,orden,datos):
        if orden.nivel == 1:
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

class cuantiles(Controlador):
    def calculo(self,orden,datos):
        if orden.nivel == 1:
            if len(datos) < 12:
                print('Aún no se puede hacer el cálculo de los cuantiles porque no se han recogido los suficientes datos.')
            else:
                T = datos[-12:]
                d = [i[1] for i in T]
                cuantiles = statistics.quantiles(d, n=4)
                print(f"El primer cuantil del 25% es {cuantiles[0]}, el que reúne el 50% de los datos es {cuantiles[1]} y el que divide los datos en un 75% es {cuantiles[2]}")

        elif self.sucesor:
            self.sucesor.calculo(orden,datos)

class ValoresMaxMin(Controlador):
    def calculo(self,orden,datos):
        if orden.nivel == 1:
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

class Umbral(Controlador):
    def calculo(self,orden,datos):
        if orden.nivel == 2:
            temp = datos[-1] # última temperatura registrada
            dato = [temp[1]] #nos quedamos solo con el valor de temp y en formato lista
            umbral = len(list(filter(lambda x: x >= 30.2,dato)))==1 
            if umbral:
                print(f"La temperatura actual de {dato[0]}ºC sobrepasa el umbral de temperatura de 30.2ºC.")
            else:
                print(f"La temperatura actual de {dato[0]}ºC NO sobrepasa el umbral de temperatura de 30.2ºC.")

        elif self.sucesor:
            self.sucesor.calculo(orden,datos)

class AumentoTemp(Controlador): #ultimos 30s (6 ultimos puestos de la lista)
    def calculo(self,orden,datos):
        if len(datos) < 6: 
            print('Aún no se puede hacer el cálculo del incremento de temperatura porque no se han recogido los suficientes datos.\n')
        else:
            if orden.nivel == 3:
                T = datos[-6:]
                d = [i[1] for i in T] # nos quedamos con las 6 últimas temperaturas solamente.
                # Se calculan todos los incrementos de la temperatura anterior con la siguiente.
                incrementoT = list(map(lambda x:abs(d[x+1]-d[x]),range(len(d)-1)))
                tempbruscas = list(filter(lambda x: x>10,incrementoT))
                if len(tempbruscas)>0:
                    print('Aumento de la temperatura detectado.')

            elif self.sucesor:
                self.sucesor.calculo(orden,datos)

class Orden:
    def __init__(self,nivel):
        self.nivel = nivel

#FIN CHAIN OF RESPONSABILITY-------------

if __name__ == '__main__':
    sensor = SensorTemp()
    i = 0
    continuar = True
    while i < 500 and continuar:
        fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        temp = randint(5,40)
        tupla_temp = (fecha,temp)
        sensor.notificar_sub(tupla_temp)
        continuar = bool(int(input("¿Deseas continuar incluyendo datos?\n Si desea continuar pulse 1, si no, pulse 0.\n")))









