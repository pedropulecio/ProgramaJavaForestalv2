/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/javafx/FXMLController.java to edit this template
 */
package com.jatnet.forestald;

import com.jfoenix.controls.JFXButton;
import java.io.IOException;
import java.net.URL;
import java.util.ResourceBundle;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.Scene;

import javafx.scene.layout.StackPane;
import javafx.stage.Stage;
/**
 * FXML Controller class
 *
 * @author Pedro
 */
public class LoginController implements Initializable {


    @FXML
    private StackPane root;
    
    @FXML
    private JFXButton btnPresentarLectura;
    @FXML
    private JFXButton btnTransferirAudios;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // TODO
    }    

   @FXML
private void presentarLectura(ActionEvent event) throws IOException {
    FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("grafica3.fxml"));
Parent root = fxmlLoader.load();
Stage stage = new Stage();
stage.setScene(new Scene(root));
stage.setMaximized(true); // Maximizar para probar
stage.show();
}


    @FXML
    private void transferirAudios(ActionEvent event) throws IOException {
        FXMLLoader loader = new FXMLLoader(getClass().getResource("audio.fxml"));
        Parent root = loader.load();
        Stage stage = new Stage();
        stage.setTitle("Lanzador de AudioServer");
        stage.setScene(new Scene(root));
        stage.show();

        System.out.println("transferirAudio");
    }
}
