import os
import socket
import time

RECOLECTOR_IP = "10.3.141.1"  # Cambia a la IP de la Raspberry Pi Recolector
RECOLECTOR_PORT = 8080
DATOS_DIR = "/home/gateway/DatosForestales"
ARCHIVO_DATOS = "datos_sensores.txt"
AUDIO_DIR = "/home/gateway/AudioForestal"  # Carpeta con los audios


def enviar_datos():
    archivo_path = os.path.join(DATOS_DIR, ARCHIVO_DATOS)

    if not os.path.exists(archivo_path):
        print("No hay datos para enviar.")
        return

    while True:
        try:
            # Leer los datos línea por línea
            with open(archivo_path, "r") as archivo:
                lineas = archivo.readlines()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                print(f"Conectando al Recolector en {RECOLECTOR_IP}:{RECOLECTOR_PORT}...")
                s.connect((RECOLECTOR_IP, RECOLECTOR_PORT))
                print("Conexión establecida. Enviando datos...")

                for linea in lineas:
                    mensaje = f"<START>{linea.strip()}<END>\n"
                    s.sendall(mensaje.encode())
                    print(f"Bloque enviado: {mensaje.strip()}")

                    # Esperar confirmación del Recolector
                    s.settimeout(2)  # 2 segundos de espera
                    try:
                        respuesta = s.recv(1024).decode().strip()
                        if respuesta != "OK":
                            print(f"Error: Confirmación inválida del Recolector. Recibido: {respuesta}")
                            break
                        else:
                            print("Confirmación recibida del Recolector. Continuando con el siguiente bloque.")
                    except socket.timeout:
                        print("Error: No se recibió confirmación del Recolector.")
                        break

            # Eliminar archivo de datos después de enviar exitosamente
            os.remove(archivo_path)
            print(f"Archivo de datos {archivo_path} eliminado después de la transferencia exitosa.")
            break

        except Exception as e:
            print(f"Error en la transferencia de datos: {e}")
            print("Reintentando en 10 segundos...")
            time.sleep(10)


def enviar_audios():
    while True:
        try:
            archivos = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]
            if not archivos:
                print("No hay archivos de audio para enviar.")
                return

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((RECOLECTOR_IP, RECOLECTOR_PORT))
                print("Conexión establecida para envío de audios.")

                for archivo in archivos:
                    archivo_path = os.path.join(AUDIO_DIR, archivo)
                    with open(archivo_path, "rb") as f:
                        contenido = f.read()
                        mensaje = f"<START_AUDIO>{archivo}<END_AUDIO>".encode() + contenido
                        s.sendall(mensaje)
                        print(f"Audio enviado: {archivo}")

                        # Esperar confirmación
                        s.settimeout(5)
                        respuesta = s.recv(1024).decode().strip()
                        if respuesta != "OK_AUDIO":
                            print(f"Error: Confirmación inválida para el archivo {archivo}.")
                            break
                        else:
                            print(f"Confirmación recibida para el archivo {archivo}.")
                            os.remove(archivo_path)
                            print(f"Archivo de audio {archivo} eliminado después de la transferencia exitosa.")
            break

        except Exception as e:
            print(f"Error en la transferencia de audios: {e}")
            print("Reintentando en 10 segundos...")
            time.sleep(10)


if __name__ == "__main__":
    while True:
        enviar_datos()
        enviar_audios()
        print("Esperando nuevos datos o audios para enviar...")
        time.sleep(30)
