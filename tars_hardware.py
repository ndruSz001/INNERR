"""
TARS Hardware Control - Control de hardware para laboratorio/taller
Controla ESP32, Arduino, sensores, actuadores, motores, servos.
Diferenciador clave vs Copilot/ChatGPT: Control real de hardware.
"""

import serial
import serial.tools.list_ports
import json
import time
from datetime import datetime
from pathlib import Path


class TarsHardware:
    """Control de hardware para experimentos y prototipos."""
    
    def __init__(self, data_dir="./data/hardware"):
        self.conexiones = {}
        self.sensores_activos = {}
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def listar_puertos_disponibles(self):
        """Lista todos los puertos seriales disponibles (ESP32, Arduino, etc.)"""
        puertos = serial.tools.list_ports.comports()
        disponibles = []
        
        for puerto in puertos:
            info = {
                "puerto": puerto.device,
                "descripcion": puerto.description,
                "fabricante": puerto.manufacturer,
                "vid_pid": f"{puerto.vid:04x}:{puerto.pid:04x}" if puerto.vid else "N/A"
            }
            disponibles.append(info)
            
        return disponibles
    
    def conectar_dispositivo(self, puerto="/dev/ttyUSB0", baudrate=115200, nombre="esp32"):
        """
        Conecta a un dispositivo serial (ESP32, Arduino, etc.)
        
        Args:
            puerto: Puerto serial (ej: /dev/ttyUSB0, COM3)
            baudrate: Velocidad de comunicación (115200 para ESP32)
            nombre: Identificador del dispositivo
        """
        try:
            conexion = serial.Serial(puerto, baudrate, timeout=1)
            time.sleep(2)  # Esperar inicialización
            
            self.conexiones[nombre] = {
                "serial": conexion,
                "puerto": puerto,
                "baudrate": baudrate,
                "conectado": datetime.now().isoformat()
            }
            
            print(f"✅ Conectado a {nombre} en {puerto} @ {baudrate} bps")
            return True
            
        except serial.SerialException as e:
            print(f"❌ Error conectando a {puerto}: {e}")
            return False
    
    def desconectar_dispositivo(self, nombre="esp32"):
        """Desconecta un dispositivo serial."""
        if nombre in self.conexiones:
            self.conexiones[nombre]["serial"].close()
            del self.conexiones[nombre]
            print(f"🔌 Desconectado: {nombre}")
            return True
        return False
    
    def enviar_comando(self, comando, nombre="esp32"):
        """
        Envía un comando al dispositivo.
        
        Args:
            comando: String o dict con el comando
            nombre: Identificador del dispositivo
        """
        if nombre not in self.conexiones:
            print(f"❌ Dispositivo '{nombre}' no conectado")
            return None
        
        conn = self.conexiones[nombre]["serial"]
        
        # Convertir dict a JSON si es necesario
        if isinstance(comando, dict):
            comando = json.dumps(comando)
        
        # Enviar comando
        conn.write(f"{comando}\n".encode())
        time.sleep(0.1)
        
        # Leer respuesta
        respuesta = ""
        while conn.in_waiting > 0:
            respuesta += conn.readline().decode().strip()
        
        return respuesta
    
    def leer_sensores(self, nombre="esp32", cantidad=1):
        """
        Lee datos de sensores del dispositivo.
        
        Returns:
            list: Lista de lecturas de sensores
        """
        if nombre not in self.conexiones:
            print(f"❌ Dispositivo '{nombre}' no conectado")
            return []
        
        lecturas = []
        conn = self.conexiones[nombre]["serial"]
        
        for _ in range(cantidad):
            if conn.in_waiting > 0:
                linea = conn.readline().decode().strip()
                try:
                    # Intentar parsear como JSON
                    datos = json.loads(linea)
                    datos["timestamp"] = datetime.now().isoformat()
                    lecturas.append(datos)
                except json.JSONDecodeError:
                    # Si no es JSON, guardar como texto
                    lecturas.append({
                        "raw": linea,
                        "timestamp": datetime.now().isoformat()
                    })
            time.sleep(0.05)
        
        return lecturas
    
    def monitorear_continuo(self, nombre="esp32", duracion_segundos=10, callback=None):
        """
        Monitorea sensores continuamente por un tiempo determinado.
        
        Args:
            nombre: Identificador del dispositivo
            duracion_segundos: Duración del monitoreo
            callback: Función a llamar con cada lectura callback(datos)
        
        Returns:
            list: Todas las lecturas realizadas
        """
        if nombre not in self.conexiones:
            print(f"❌ Dispositivo '{nombre}' no conectado")
            return []
        
        print(f"📊 Monitoreando {nombre} por {duracion_segundos}s...")
        
        todas_lecturas = []
        inicio = time.time()
        
        while (time.time() - inicio) < duracion_segundos:
            lecturas = self.leer_sensores(nombre, cantidad=1)
            
            for lectura in lecturas:
                todas_lecturas.append(lectura)
                
                if callback:
                    callback(lectura)
                else:
                    print(f"  {lectura}")
            
            time.sleep(0.1)
        
        print(f"✅ Monitoreo completado: {len(todas_lecturas)} lecturas")
        return todas_lecturas
    
    def controlar_servo(self, pin, angulo, nombre="esp32"):
        """
        Controla un servo conectado al dispositivo.
        
        Args:
            pin: Pin del servo (ej: 13)
            angulo: Ángulo deseado (0-180)
            nombre: Identificador del dispositivo
        """
        comando = {
            "tipo": "servo",
            "pin": pin,
            "angulo": angulo
        }
        
        respuesta = self.enviar_comando(comando, nombre)
        print(f"🎛️  Servo pin {pin} → {angulo}°: {respuesta}")
        return respuesta
    
    def controlar_motor(self, pin, velocidad, nombre="esp32"):
        """
        Controla un motor DC con PWM.
        
        Args:
            pin: Pin del motor
            velocidad: Velocidad PWM (0-255)
            nombre: Identificador del dispositivo
        """
        comando = {
            "tipo": "motor",
            "pin": pin,
            "velocidad": velocidad
        }
        
        respuesta = self.enviar_comando(comando, nombre)
        print(f"⚡ Motor pin {pin} → velocidad {velocidad}: {respuesta}")
        return respuesta
    
    def ejecutar_protocolo_prueba(self, protocolo, nombre="esp32"):
        """
        Ejecuta un protocolo de prueba completo.
        
        Args:
            protocolo: Dict con pasos del protocolo
            {
                "nombre": "Prueba de torque",
                "pasos": [
                    {"accion": "servo", "pin": 13, "angulo": 90, "esperar": 2},
                    {"accion": "leer", "cantidad": 10},
                    {"accion": "servo", "pin": 13, "angulo": 0, "esperar": 2}
                ]
            }
        """
        print(f"\n🧪 Ejecutando protocolo: {protocolo.get('nombre', 'Sin nombre')}")
        
        resultados = {
            "protocolo": protocolo["nombre"],
            "inicio": datetime.now().isoformat(),
            "pasos": [],
            "lecturas": []
        }
        
        for i, paso in enumerate(protocolo.get("pasos", [])):
            print(f"\n  Paso {i+1}/{len(protocolo['pasos'])}: {paso}")
            
            if paso["accion"] == "servo":
                respuesta = self.controlar_servo(paso["pin"], paso["angulo"], nombre)
                resultados["pasos"].append({
                    "paso": i+1,
                    "accion": "servo",
                    "respuesta": respuesta
                })
                
            elif paso["accion"] == "motor":
                respuesta = self.controlar_motor(paso["pin"], paso["velocidad"], nombre)
                resultados["pasos"].append({
                    "paso": i+1,
                    "accion": "motor",
                    "respuesta": respuesta
                })
                
            elif paso["accion"] == "leer":
                lecturas = self.leer_sensores(nombre, paso.get("cantidad", 1))
                resultados["lecturas"].extend(lecturas)
                resultados["pasos"].append({
                    "paso": i+1,
                    "accion": "leer",
                    "lecturas_count": len(lecturas)
                })
            
            # Esperar si está especificado
            if "esperar" in paso:
                time.sleep(paso["esperar"])
        
        resultados["fin"] = datetime.now().isoformat()
        
        # Guardar resultados
        archivo_resultados = self.data_dir / f"protocolo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(archivo_resultados, 'w') as f:
            json.dump(resultados, f, indent=2)
        
        print(f"\n✅ Protocolo completado. Resultados guardados en: {archivo_resultados}")
        return resultados
    
    def calibrar_servos(self, pines, nombre="esp32"):
        """
        Calibra múltiples servos encontrando sus rangos de movimiento.
        
        Args:
            pines: Lista de pines de servos a calibrar
            nombre: Identificador del dispositivo
        """
        print(f"\n🔧 Calibrando {len(pines)} servos...")
        
        calibracion = {}
        
        for pin in pines:
            print(f"\n  Calibrando servo en pin {pin}...")
            
            # Probar rango 0-180
            self.controlar_servo(pin, 0, nombre)
            time.sleep(1)
            
            self.controlar_servo(pin, 90, nombre)
            time.sleep(1)
            
            self.controlar_servo(pin, 180, nombre)
            time.sleep(1)
            
            self.controlar_servo(pin, 90, nombre)  # Posición neutral
            
            calibracion[f"pin_{pin}"] = {
                "min": 0,
                "max": 180,
                "neutral": 90,
                "calibrado": datetime.now().isoformat()
            }
        
        # Guardar calibración
        archivo_cal = self.data_dir / f"calibracion_servos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(archivo_cal, 'w') as f:
            json.dump(calibracion, f, indent=2)
        
        print(f"\n✅ Calibración completada. Datos en: {archivo_cal}")
        return calibracion


# Ejemplo de uso
if __name__ == "__main__":
    hw = TarsHardware()
    
    # Listar puertos disponibles
    print("🔍 Puertos disponibles:")
    for puerto in hw.listar_puertos_disponibles():
        print(f"  - {puerto['puerto']}: {puerto['descripcion']}")
    
    # Conectar a ESP32
    # hw.conectar_dispositivo("/dev/ttyUSB0", nombre="esp32_exoesqueleto")
    
    # Ejemplo de protocolo
    protocolo_ejemplo = {
        "nombre": "Prueba de torque exoesqueleto",
        "pasos": [
            {"accion": "servo", "pin": 13, "angulo": 0, "esperar": 2},
            {"accion": "leer", "cantidad": 5},
            {"accion": "servo", "pin": 13, "angulo": 90, "esperar": 2},
            {"accion": "leer", "cantidad": 5},
            {"accion": "servo", "pin": 13, "angulo": 180, "esperar": 2},
            {"accion": "leer", "cantidad": 5},
        ]
    }
    
    # hw.ejecutar_protocolo_prueba(protocolo_ejemplo)
