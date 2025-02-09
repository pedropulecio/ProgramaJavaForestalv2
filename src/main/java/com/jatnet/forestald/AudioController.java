/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/javafx/FXMLController.java to edit this template
 */
package com.jatnet.forestald;

import com.jfoenix.controls.JFXButton;
import java.io.OutputStream;
import java.io.PrintStream;
import java.net.URL;
import java.util.ResourceBundle;
import javafx.concurrent.Task;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.TextArea;

/**
 * FXML Controller class
 *
 * @author Pedro
 */
public class AudioController  {

  @FXML
    private JFXButton runAudioServerButton;

    @FXML
    private JFXButton stopAudioServerButton;

    @FXML
    private TextArea consoleOutput;

    private Thread audioServerThread; // Hilo para ejecutar el servidor
    private AudioServer audioServer;  // Objeto del servidor
    private boolean isServerRunning = false; // Bandera para verificar el estado del servidor

    @FXML
    private void initialize() {
        // Redirigir System.out a la consola gráfica
        System.setOut(new PrintStream(new OutputStream() {
            @Override
            public void write(int b) {
                consoleOutput.appendText(String.valueOf((char) b));
            }
        }));

        // Configurar botón para ejecutar el servidor
        runAudioServerButton.setOnAction(event -> startAudioServer());

        // Configurar botón para detener el servidor
        stopAudioServerButton.setOnAction(event -> stopAudioServer());
    }

    private void startAudioServer() {
      if (isServerRunning) {
        consoleOutput.appendText("El servidor ya está en ejecución.\n");
        return;
    }

    try {
        // Intentar liberar el puerto antes de iniciar el servidor
        AudioServer.liberarPuerto(5000);

        // Crear una tarea para ejecutar el servidor en un hilo separado
        Task<Void> serverTask = new Task<>() {
            @Override
            protected Void call() throws Exception {
                try {
                    // Crear un nuevo objeto de AudioServer
                    audioServer = new AudioServer();
                    audioServer.main(null); // Iniciar el servidor
                    isServerRunning = true;
                } catch (Exception e) {
                    updateMessage("Error al iniciar el servidor: " + e.getMessage());
                }
                return null;
            }
        };

        // Actualizar la consola con los mensajes de la tarea
        serverTask.messageProperty().addListener((obs, oldMessage, newMessage) -> {
            if (newMessage != null && !newMessage.isEmpty()) {
                consoleOutput.appendText(newMessage + "\n");
            }
        });

        // Ejecutar la tarea en un nuevo hilo
        audioServerThread = new Thread(serverTask);
        audioServerThread.setDaemon(true); // Asegurar que el hilo se detenga al cerrar la aplicación
        audioServerThread.start();

        consoleOutput.appendText("AudioServer iniciado.\n");

    } catch (Exception e) {
        consoleOutput.appendText("Error al iniciar AudioServer: " + e.getMessage() + "\n");
        e.printStackTrace();
    }
    }

    private void stopAudioServer() {
        if (!isServerRunning) {
        consoleOutput.appendText("No hay un servidor en ejecución para detener.\n");
        return;
    }

    try {
        // Detener el servidor
        if (audioServer != null) {
            audioServer.shutdown(); // Llama al método para detener el servidor
        }
        if (audioServerThread != null && audioServerThread.isAlive()) {
            audioServerThread.interrupt(); // Interrumpir el hilo
        }

        isServerRunning = false; // Marcar como detenido
        consoleOutput.appendText("AudioServer detenido.\n");

    } catch (Exception e) {
        consoleOutput.appendText("Error al detener el servidor: " + e.getMessage() + "\n");
    }
    }
      
    
}
