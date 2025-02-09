import os
import requests
import pymysql

# Configuración de rutas y servidor
SOURCE_DIR = "/home/recolector/Documents/AudioRecolectados"
SERVER_URL = "http://10.3.141.54:5000/upload_audio"  # Cambiar si el puerto cambió
ruta_archivo_datos = "/home/recolector/Documents/Datos/datos_recibidos.txt"

# Verificar si el servidor está disponible
def verificar_servidor():
    try:
        response = requests.get(SERVER_URL, timeout=3)  # Prueba de conexión con un timeout de 3 segundos
        if response.status_code == 200 or response.status_code == 405:
            print("Servidor AudioServer disponible.")
            return True
    except requests.ConnectionError:
        print("Servidor AudioServer no está disponible.")
    except Exception as e:
        print(f"Error al verificar el servidor: {e}")
    return False

# Función para transferir los datos (transferirDatos.py)
def transferir_datos():
    if not os.path.exists(ruta_archivo_datos):
        print(f"El archivo no se encontró en la ruta: {ruta_archivo_datos}")
        return

    print(f"Procesando datos desde {ruta_archivo_datos}...")
    try:
        connection = pymysql.connect(
            host="10.3.141.54",
            user="monitor",
            password="admin",
            database="monitoreoforestal"
        )
        with connection.cursor() as cursor:
            with open(ruta_archivo_datos, "r") as file:
                for linea in file:
                    datos = limpiar_y_procesar(linea)
                    idNodoOriginal = int(datos[0])
                    nombreNodo = f"Nodo {idNodoOriginal}"
                    fecha = datos[1]
                    hora = datos[2]
                    temperatura, humedad, luminosidad, lluvia = map(float, datos[3:])

                    # Verificar o insertar nodo
                    idNodo = verificar_e_insertar_nodo(cursor, nombreNodo, connection)

                    # Insertar en la tabla registro
                    query = """
                    INSERT INTO registro (idNodo, fecha, hora, temperatura, humedad, luminosidad, lluvia)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (idNodo, fecha, hora, temperatura, humedad, int(luminosidad), int(lluvia)))
                    connection.commit()

            print("Datos procesados e insertados correctamente.")
            os.remove(ruta_archivo_datos)
            print(f"Archivo eliminado: {ruta_archivo_datos}")

    except pymysql.MySQLError as e:
        print(f"Error de MySQL: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close()

# Función para cliente_post.py
def enviar_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'rb') as f:
            files = {'file': (os.path.basename(ruta_archivo), f)}
            response = requests.post(SERVER_URL, files=files, timeout=10)

        if response.status_code == 200:
            print(f"Archivo enviado correctamente: {ruta_archivo}")
            return True
        else:
            print(f"Error al enviar archivo: {ruta_archivo}, Código: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("Servidor no disponible. Cerrando el programa.")
        return False
    except Exception as e:
        print(f"Error inesperado al conectar con el servidor: {e}")
        return False

def monitorear_y_enviar():
    """Monitorea la carpeta, envía los archivos y cierra el programa si no hay servidor."""
    if not verificar_servidor():
        print("Servidor no disponible. Cerrando el programa.")
        return

    if not os.path.exists(SOURCE_DIR):
        print(f"El directorio fuente no existe: {SOURCE_DIR}")
        return

    print(f"Monitoreando la carpeta: {SOURCE_DIR}")
    archivos = os.listdir(SOURCE_DIR)
    if not archivos:
        print("No hay archivos para transferir. Cerrando el programa...")
        return

    for archivo in archivos:
        ruta_archivo = os.path.join(SOURCE_DIR, archivo)
        if os.path.isfile(ruta_archivo):
            if enviar_archivo(ruta_archivo):
                os.remove(ruta_archivo)
                print(f"Archivo eliminado: {ruta_archivo}")
            else:
                print(f"No se pudo enviar el archivo: {ruta_archivo}")

# Función auxiliar de transferirDatos.py
def limpiar_y_procesar(linea):
    linea = linea.replace("Nodo: ", "").replace("Fecha: ", "").replace("Hora: ", "").replace("Datos: ", "")
    return linea.strip().split(", ")

def verificar_e_insertar_nodo(cursor, nombreNodo, connection, idUsuario=1):
    cursor.execute("SELECT idNodo FROM nodo WHERE nombreNodo = %s", (nombreNodo,))
    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]
    else:
        cursor.execute("INSERT INTO nodo (nombreNodo, idUsuario) VALUES (%s, %s)", (nombreNodo, idUsuario))
        connection.commit()
        cursor.execute("SELECT idNodo FROM nodo WHERE nombreNodo = %s", (nombreNodo,))
        return cursor.fetchone()[0]

if __name__ == "__main__":
    # Ejecutar transferirDatos.py
    print("Iniciando transferencia de datos...")
    transferir_datos()

    # Ejecutar cliente_post.py
    print("Iniciando transferencia de audios...")
    monitorear_y_enviar()
