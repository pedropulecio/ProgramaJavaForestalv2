module com.jatnet.forestald {
    requires javafx.controls;
    requires javafx.fxml;
    requires java.base;
    requires java.sql;
    requires com.jfoenix;
    requires org.kordamp.ikonli.core;
    requires jdk.httpserver; // Agrega este módulo

    opens com.jatnet.forestald to javafx.fxml;
    exports com.jatnet.forestald;
}
