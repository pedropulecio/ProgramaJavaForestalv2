/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.jatnet.forestald;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.InetSocketAddress;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.util.concurrent.Executors;

/**
 *
 * @author Pedro
 */
public class AudioServer {
    private static final String UPLOAD_DIR = "C:/AudiosBase"; // Carpeta donde se guardarán los audios
    private static final String DB_URL = "jdbc:mysql://localhost:3306/monitoreoforestal"; // Ajusta según tu configuración
    private static final String DB_USER = "monitor";
    private static final String DB_PASSWORD = "admin";

    private static HttpServer server;

    public static void main(String[] args) {
        try {
            // Intentar liberar el puerto si está ocupado
            liberarPuerto(5000);

            // Crear directorio de subida si no existe
            File uploadDir = new File(UPLOAD_DIR);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
            }

            // Configurar servidor HTTP
            server = HttpServer.create(new InetSocketAddress(5000), 0);
            server.createContext("/upload_audio", new AudioUploadHandler());
            server.setExecutor(Executors.newFixedThreadPool(10)); // Manejo de concurrencia
            System.out.println("Servidor escuchando en el puerto 5000...");

            // Manejar cierre del servidor
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                System.out.println("Liberando recursos y apagando el servidor...");
                if (server != null) {
                    server.stop(0); // Detener el servidor y liberar el puerto
                }
                System.out.println("Servidor detenido y puerto liberado.");
            }));

            // Iniciar el servidor
            server.start();

        } catch (java.net.BindException e) {
            System.err.println("El puerto 5000 ya está en uso. Intenta liberar el puerto o usar uno diferente.");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // Clase que maneja las solicitudes de subida de audio
    static class AudioUploadHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) {
            if (!exchange.getRequestMethod().equalsIgnoreCase("POST")) {
                sendResponse(exchange, 405, "Método no permitido");
                return;
            }

            try {
                // Guardar el archivo
                String fileName = "audio_" + System.currentTimeMillis() + ".wav";
                File file = new File(UPLOAD_DIR, fileName);
                try (InputStream is = exchange.getRequestBody();
                     FileOutputStream fos = new FileOutputStream(file)) {
                    byte[] buffer = new byte[1024];
                    int bytesRead;
                    while ((bytesRead = is.read(buffer)) != -1) {
                        fos.write(buffer, 0, bytesRead);
                    }
                }

                // Registrar el archivo en la base de datos
                registrarArchivoEnBaseDeDatos(fileName, file.getAbsolutePath());

                // Responder al cliente
                sendResponse(exchange, 200, "Archivo recibido y registrado");
                System.out.println("Archivo recibido: " + fileName);
            } catch (Exception e) {
                e.printStackTrace();
                sendResponse(exchange, 500, "Error interno del servidor");
            }
        }

        // Método para registrar la ruta del archivo en la base de datos
        private void registrarArchivoEnBaseDeDatos(String fileName, String ruta) throws Exception {
            String query = "INSERT INTO audioforestal (idUsuario, rutaAudio) VALUES (?, ?)";
            try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, 1); // ID del usuario (ajustar según sea necesario)
                stmt.setString(2, ruta);
                stmt.executeUpdate();
                System.out.println("Archivo registrado en la base de datos: " + ruta);
            }
        }

        // Método para enviar una respuesta HTTP al cliente
        private void sendResponse(HttpExchange exchange, int statusCode, String message) {
            try {
                exchange.sendResponseHeaders(statusCode, message.getBytes().length);
                exchange.getResponseBody().write(message.getBytes());
                exchange.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    public void shutdown() {
    if (server != null) {
        server.stop(0); // Detener el servidor HTTP
        System.out.println("Servidor detenido y recursos liberados.");
    }
}

    // Método para liberar un puerto ocupado
    public static void liberarPuerto(int puerto) {
        try {
            String comando = String.format("cmd /c netstat -aon | findstr :%d", puerto);
            Process proceso = Runtime.getRuntime().exec(comando);
            BufferedReader reader = new BufferedReader(new InputStreamReader(proceso.getInputStream()));
            String linea;
            while ((linea = reader.readLine()) != null) {
                if (linea.contains("LISTENING")) {
                    String[] tokens = linea.split("\\s+");
                    int pid = Integer.parseInt(tokens[tokens.length - 1]);
                    Runtime.getRuntime().exec(String.format("taskkill /PID %d /F", pid));
                    System.out.println("Proceso en el puerto " + puerto + " detenido.");
                }
            }
        } catch (IOException e) {
            System.err.println("Error al liberar el puerto: " + e.getMessage());
        }
    }

}
