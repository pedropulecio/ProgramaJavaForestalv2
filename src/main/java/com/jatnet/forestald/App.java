package com.jatnet.forestald;


import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

import java.io.IOException;
import java.sql.SQLException;
import javafx.scene.image.Image;


/**
 * JavaFX App
 */
public class App extends Application {

   public static String imagesPath="src/main/resources";
    private static Scene scene;
    
            
       
    @Override
    public void start(Stage stage) throws IOException {
        scene = new Scene(loadFXML("Login_1"), 640, 480);
        stage.setTitle("Jatnet");
    
try {
stage.getIcons().add(new Image(App.class.getResourceAsStream("/imagenes/productos.png")));
        System.out.println(imagesPath+"/imagenes/add_user.png");
} catch (NullPointerException e){ 
    System.err.println("No se pudo cargar");
}

        stage.setScene(scene);
       
        stage.show();
    }

    static void setRoot(String fxml) throws IOException {
        scene.setRoot(loadFXML(fxml));
    }

    private static Parent loadFXML(String fxml) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(App.class.getResource(fxml + ".fxml"));
        return fxmlLoader.load();
    }

    public static void main(String[] args) throws SQLException {
        //com.jatnet.basejatnet.model.Comercio.getInstance(new ComercioDAO().getComercio());
        launch();
    }
}