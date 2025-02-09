import os
import requests

# Ruta de la carpeta en la Raspberry Pi donde están los audios
SOURCE_DIR = "/home/recolector/Documents/AudioRecolectados"
SERVER_URL = "http://10.3.141.54:5000/upload_audio"  # Cambiar puerto si se modificó en el servidor

def enviar_archivo(ruta_archivo):
    """Envía un archivo al servidor HTTP."""
    try:
        with open(ruta_archivo, 'rb') as f:
            files = {'file': (os.path.basename(ruta_archivo), f)}
            response = requests.post(SERVER_URL, files=files, timeout=10)  # Timeout de 10 segundos

        if response.status_code == 200:
            print(f"Archivo enviado correctamente: {ruta_archivo}")
            return True
        else:
            print(f"Error al enviar archivo: {ruta_archivo}, Código: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("Servidor no disponible. Verifica que el servidor esté corriendo.")
        return False
    except requests.Timeout:
        print(f"Tiempo de espera agotado para el archivo: {ruta_archivo}")
        return False
    except Exception as e:
        print(f"Error inesperado al conectar con el servidor: {e}")
        return False

def monitorear_y_enviar():
    """Monitorea la carpeta, envía los archivos y cierra el programa al terminar."""
    if not os.path.exists(SOURCE_DIR):
        print(f"El directorio fuente no existe: {SOURCE_DIR}")
        return

    print(f"Monitoreando la carpeta: {SOURCE_DIR}")
    archivos_enviados = 0

    while True:
        try:
            archivos = os.listdir(SOURCE_DIR)
            if not archivos:
                if archivos_enviados == 0:
                    print("No hay archivos para transferir. Cerrando el programa...")
                else:
                    print(f"Transferencia completada. {archivos_enviados} archivos enviados.")
                break  # Salir del bucle al completar la transferencia

            for archivo in archivos:
                ruta_archivo = os.path.join(SOURCE_DIR, archivo)
                if os.path.isfile(ruta_archivo):
                    if enviar_archivo(ruta_archivo):
                        os.remove(ruta_archivo)  # Eliminar archivo si se envió correctamente
                        print(f"Archivo eliminado: {ruta_archivo}")
                        archivos_enviados += 1
                    else:
                        print(f"No se pudo enviar el archivo: {ruta_archivo}")
            # No es necesario esperar porque el programa se cerrará
        except KeyboardInterrupt:
            print("Programa interrumpido manualmente. Saliendo...")
            break
        except Exception as e:
            print(f"Error en el monitoreo: {e}")
            break

if __name__ == "__main__":
    monitorear_y_enviar()
