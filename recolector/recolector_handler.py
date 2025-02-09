import socket
import os

RECOLECTOR_IP = "0.0.0.0"
RECOLECTOR_PORT = 8080
DATOS_DIR = "/home/recolector/Documents/Datos"
ARCHIVO_DATOS = "datos_recibidos.txt"
AUDIO_DIR = "/home/recolector/Documents/AudioRecolectados"

def recibir_datos():
    os.makedirs(DATOS_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilización del puerto
        s.bind((RECOLECTOR_IP, RECOLECTOR_PORT))
        s.listen(1)
        print(f"Esperando conexión en {RECOLECTOR_IP}:{RECOLECTOR_PORT}...")

        while True:
            conn, addr = s.accept()
            print(f"Conexión establecida con {addr}")
            buffer = b""

            with conn:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    buffer += data

                    # Procesar datos de sensores
                    while b"<START>" in buffer and b"<END>" in buffer:
                        inicio = buffer.index(b"<START>") + len("<START>")
                        fin = buffer.index(b"<END>")
                        datos = buffer[inicio:fin].decode().strip()

                        if datos == "CERRAR_SERVIDOR":
                            print("Comando recibido para cerrar el servidor.")
                            return  # Salir de la función y cerrar el servidor

                        if datos:
                            with open(f"{DATOS_DIR}/{ARCHIVO_DATOS}", "a") as archivo:
                                archivo.write(datos + "\n")
                                print(f"Datos procesados y guardados: {datos}")

                        buffer = buffer[fin + len("<END>"):]
                        conn.sendall("OK\n".encode())

                    # Procesar archivos de audio
                    while b"<START_AUDIO>" in buffer and b"<END_AUDIO>" in buffer:
                        inicio = buffer.index(b"<START_AUDIO>") + len("<START_AUDIO>")
                        fin = buffer.index(b"<END_AUDIO>")
                        nombre_archivo = buffer[inicio:fin].decode().strip()
                        contenido_inicio = fin + len("<END_AUDIO>")
                        contenido = buffer[contenido_inicio:]

                        archivo_path = os.path.join(AUDIO_DIR, nombre_archivo)
                        with open(archivo_path, "wb") as audio_file:
                            audio_file.write(contenido)
                            print(f"Archivo de audio recibido y guardado: {archivo_path}")

                        buffer = b""
                        conn.sendall("OK_AUDIO\n".encode())

if __name__ == "__main__":
    try:
        recibir_datos()
    except KeyboardInterrupt:
        print("Interrupción manual. Cerrando el servidor...")
    finally:
        print("Servidor cerrado.")
