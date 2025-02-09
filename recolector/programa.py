import RPi.GPIO as GPIO
import os
import time
import socket
import threading

# Pines GPIO
BUTTON_1_GPIO = 27  # Botón para recolector_handler
BUTTON_2_GPIO = 17  # Botón para transferirDatos
LED_GPIO = 6        # LED indicador
RECOLECTOR_PORT = 8080
DATOS_DIR = "/home/recolector/Documents/Datos"
ARCHIVO_DATOS = "datos_recibidos.txt"
AUDIO_DIR = "/home/recolector/Documents/AudioRecolectados"

# Estado del programa
current_mode = "idle"  # Puede ser 'recolector_handler', 'transferirDatos', o 'idle'
server_running = False

# Configuración de GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_1_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_2_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_GPIO, GPIO.OUT)
GPIO.output(LED_GPIO, GPIO.LOW)

# Función para el modo recolector_handler
def recolector_handler():
    global server_running
    server_running = True
    os.makedirs(DATOS_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", RECOLECTOR_PORT))
        s.listen(1)
        print(f"Servidor activo en el puerto {RECOLECTOR_PORT}.")

        while server_running:
            try:
                s.settimeout(1)
                conn, addr = s.accept()
                print(f"Conexión establecida con {addr}")
                buffer = b""

                with conn:
                    while server_running:
                        data = conn.recv(4096)
                        if not data:
                            break
                        buffer += data

                        while b"<START>" in buffer and b"<END>" in buffer:
                            inicio = buffer.index(b"<START>") + len("<START>")
                            fin = buffer.index(b"<END>")
                            datos = buffer[inicio:fin].decode().strip()

                            if datos:
                                with open(f"{DATOS_DIR}/{ARCHIVO_DATOS}", "a") as archivo:
                                    archivo.write(datos + "\n")
                                    print(f"Datos procesados y guardados: {datos}")

                            buffer = buffer[fin + len("<END>"):]
                            conn.sendall("OK\n".encode())

            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error en el servidor: {e}")

    print("Servidor detenido.")

# Función para el modo transferirDatos
def transferir_datos():
    try:
        print("Iniciando transferencia de datos...")
        exit_code = os.system("python3 /home/recolector/Documents/transferirDatos.py")
        if exit_code == 0:
            print("transferirDatos.py finalizó correctamente.")
        else:
            print(f"Error en transferirDatos.py: {exit_code}")
    except Exception as e:
        print(f"Error en transferirDatos: {e}")

# Función para manejar pulsadores
def manejar_pulsadores(channel):
    global current_mode, server_running
    if channel == BUTTON_1_GPIO:
        if current_mode != "recolector_handler":
            print("Cambiando a modo recolector_handler...")
            current_mode = "recolector_handler"
            GPIO.output(LED_GPIO, GPIO.HIGH)
            server_thread = threading.Thread(target=recolector_handler)
            server_thread.start()
        else:
            print("El servidor ya está en modo recolector_handler.")
    elif channel == BUTTON_2_GPIO:
        if current_mode != "transferirDatos":
            print("Cambiando a modo transferirDatos...")
            current_mode = "transferirDatos"
            server_running = False
            GPIO.output(LED_GPIO, GPIO.LOW)
            time.sleep(2)  # Esperar a que el servidor termine
            transferir_datos()
        else:
            print("Ya estás en modo transferirDatos.")

# Configurar eventos GPIO
GPIO.add_event_detect(BUTTON_1_GPIO, GPIO.FALLING, callback=manejar_pulsadores, bouncetime=200)
GPIO.add_event_detect(BUTTON_2_GPIO, GPIO.FALLING, callback=manejar_pulsadores, bouncetime=200)

print("Sistema listo. Usa los botones para cambiar entre modos.")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Saliendo del programa...")
    server_running = False
    GPIO.cleanup()
