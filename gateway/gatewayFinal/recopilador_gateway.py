import serial
from datetime import datetime
import os

# Configuración de puerto serial y carpeta de almacenamiento
PORT = '/dev/ttyAMA0'
BAUD_RATE = 9600
CARPETA = '/home/gateway/DatosForestales'

# Crear carpeta si no existe
if not os.path.exists(CARPETA):
    os.makedirs(CARPETA)

def guardar_datos(nodo, fecha, hora, datos):
    """
    Guarda los datos recibidos en el archivo de texto.
    """
    # Asegurarse de que la hora tenga el formato HH:MM
    if ":" not in hora and len(hora) == 4:  # Caso: "2125" -> "21:25"
        hora = hora[:2] + ":" + hora[2:]
        print(f"[INFO] Hora reconstruida: {hora}")
    elif ":" in hora and len(hora.split(":")) == 2:  # Caso: ya está en "HH:MM"
        pass
    else:
        print(f"[WARNING] Formato de hora no válido: {hora}. Se usará como está.")

    # Intentar validar y formatear
    try:
        hora_formateada = datetime.strptime(hora, "%H:%M").strftime("%H:%M")
    except ValueError:
        print(f"[ERROR] Formato de hora inválido, usando sin cambios: {hora}")
        hora_formateada = hora  # Usar la hora tal cual en caso de error

    # Guardar datos en archivo
    linea = f"Nodo: {nodo}, Fecha: {fecha}, Hora: {hora_formateada}, Datos: {', '.join(datos)}"
    archivo_path = f"{CARPETA}/datos_sensores.txt"
    with open(archivo_path, "a") as archivo:
        archivo.write(linea + "\n")
    print(f"[INFO] Datos guardados: {linea}")

def procesar_mensaje(mensaje):
    """
    Procesa el mensaje recibido y extrae los datos.
    """
    try:
        if not mensaje.startswith("INICIO:") or not mensaje.endswith(",FIN"):
            print(f"[WARNING] Mensaje mal formateado: {mensaje}")
            return

        # Extraer partes entre "INICIO:" y ",FIN"
        partes = mensaje[7:-4].split(",")
        nodo = None
        fecha = None
        hora = None
        datos = []

        # Leer los datos clave
        for parte in partes:
            if parte.startswith("NODO:"):
                nodo = parte.split(":")[1]
            elif parte.startswith("FECHA:"):
                fecha = parte.split(":")[1]
            elif parte.startswith("HORA:"):
                hora = parte[len("HORA:"):]  # Extrae todo después de "HORA:"
            elif parte.startswith("TEMP:") or parte.startswith("HUM:") or parte.startswith("LUM:") or parte.startswith("LLUVIA:"):
                datos.append(parte.split(":")[1])

        # Validar los datos mínimos
        if not nodo or not fecha or not hora or len(datos) < 4:
            print(f"[WARNING] Datos incompletos: {mensaje}")
            return

        # Guardar datos
        guardar_datos(nodo, fecha, hora, datos)

    except Exception as e:
        print(f"[ERROR] Error al procesar el mensaje: {e}, Mensaje: {mensaje}")

def enviar_hora(ser):
    """
    Envía la hora actual al maestro cuando lo solicita.
    """
    try:
        hora_actual = datetime.now().strftime("HORA:%Y-%m-%d %H:%M:%S")
        ser.write((hora_actual + "\n").encode('utf-8'))
        print(f"[INFO] Hora enviada al maestro: {hora_actual}")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar la hora: {e}")

def main():
    """
    Programa principal que maneja la comunicación con el maestro.
    """
    try:
        with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
            print(f"[INFO] Escuchando en {PORT} a {BAUD_RATE} baudios...")
            while True:
                if ser.in_waiting > 0:
                    mensaje = ser.readline().decode('utf-8').strip()
                    print(f"[DEBUG] Mensaje recibido bruto: {mensaje}")

                    # Procesar mensaje recibido
                    if mensaje.startswith("SOLICITAR_HORA"):
                        enviar_hora(ser)
                    else:
                        procesar_mensaje(mensaje)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
