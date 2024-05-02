import io
from abc import ABC, abstractmethod
import time

class Controlador(type): # Patrón Singleton.
   
    _unicaInstancia = None

    def __init__(self,estrategia):
        self._estrategia = estrategia
        self._data = []

    
    def obtener_instancia(cls):
        if not cls._unicaInstancia:
            cls._unicaInstancia = cls()
        return cls._unicaInstancia
    
    def insertar_datos(self,temp):
        self._data.append(temp)
        # Para la notificación de cada elemento:
        self.notificacion().set_temperatura(temp)
        
        time.sleep(5) # Se reciben datos cada 5 segundos.

    
    def notificacion(self): # Patrón Observer -- se debe notificar al sistema cada 5 segundos con el nuevo valor de temperatura.
        # solo habrá un observador.
        class Observable: 
            def __init__(self):
                self._observer = None
            
            def register_observer(self,observer):
                self._observer = observer
            
            # No hará falta el método delete porque el sistema siempre estará suscrito a las notificiones del sensor.

            def notify_observer(self, data): 
                self._observer.update(data)

        class SensorTemperatura(Observable):
            def __init__(self, name):
                super().__init__()
                self.name = name
                self.temp = 0

            def set_temperatura(self, temp): 
                self.temp = temp
                self.notify_observer(self.temp)
        
        class Observer(ABC):
            @abstractmethod
            def update(self, data):
                pass

        class Sistema(Observer): 
            def update(self, temp): # Notificación individual.
                print(f"El sistema ha recibido un valor de temperatura: {temp}")
        
        sensor_temp = SensorTemperatura('Sensor de Temperatura')
        sistema = Sistema()
        sensor_temp.register_observer(sistema)

        return sensor_temp
    
    def estrategia(self):
        pass

    def comprobaciones(self): # Patrón de Chain of Responsibility.

        def estadísticos(self): # Cálculo de los estadísticos.
            # Patrón Strategy ---- se podrá ir variando de estrategia con respecto a lo que se tarde en ejecutar con el módulo IO.
            pass

        
        def umbral(self):
            pass

        def incremento(self):
            pass


if __name__ == "__main__":
    controlador = Controlador.obtener_instancia()





# El primer patrón de diseño es el Singleton.
# El segundo patrón puede que sea el Observer
# El R3 puede ser Chain of Responsibility pues es una cadena de responsabilidades con unos pasos a seguir.
# El R4 tal vez sea Strategy.


# Para hacer el patrón R3 se utilizarán los métodos funcionales.










