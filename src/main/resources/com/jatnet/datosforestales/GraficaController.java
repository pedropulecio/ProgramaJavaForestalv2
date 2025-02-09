/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/javafx/FXMLController.java to edit this template
 */
package com.jatnet.datosforestales;
import java.io.IOException;
import java.net.URL;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.ResourceBundle;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.chart.CategoryAxis;

import javafx.scene.chart.LineChart;
import javafx.scene.chart.XYChart;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.ScrollPane;
import javafx.scene.layout.GridPane;
import javafx.stage.Stage;
/**
 * FXML Controller class
 *
 * @author Pedro
 */
public class GraficaController  {

    @FXML
    private ComboBox<String> comboBoxNodos;

    @FXML
    private DatePicker datePickerInicio;

    @FXML
    private ComboBox<String> comboBoxHoraInicio;

    @FXML
    private DatePicker datePickerFin;

    @FXML
    private ComboBox<String> comboBoxHoraFin;

    @FXML
    private LineChart<String, Number> lineChartTemperatura;

    @FXML
    private LineChart<String, Number> lineChartHumedad;

    @FXML
    private LineChart<String, Number> lineChartLuminosidad;

    @FXML
    private LineChart<String, Number> lineChartLluvia;

    private static final String DB_URL = "jdbc:mysql://localhost:3306/monitoreoforestal";
    private static final String DB_USER = "monitor";
    private static final String DB_PASSWORD = "admin";

    @FXML
    public void initialize() {
        cargarNodos();
        cargarHoras();

        // Desactivar animaciones para mejorar el rendimiento
        lineChartTemperatura.setAnimated(false);
        lineChartHumedad.setAnimated(false);
        lineChartLuminosidad.setAnimated(false);
        lineChartLluvia.setAnimated(false);
    }

    private void cargarNodos() {
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
            String query = "SELECT DISTINCT nombreNodo FROM nodo";
            PreparedStatement stmt = conn.prepareStatement(query);
            ResultSet rs = stmt.executeQuery();

            ObservableList<String> nodos = FXCollections.observableArrayList();
            while (rs.next()) {
                nodos.add(rs.getString("nombreNodo"));
            }

            comboBoxNodos.setItems(nodos);
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("Error al cargar los nodos: " + e.getMessage());
        }
    }

    private void cargarHoras() {
        ObservableList<String> horas = FXCollections.observableArrayList();
        for (int i = 0; i < 24; i++) {
            for (int j = 0; j < 60; j += 15) {
                horas.add(String.format("%02d:%02d:00", i, j));
            }
        }
        comboBoxHoraInicio.setItems(horas);
        comboBoxHoraFin.setItems(horas);
    }

    @FXML
    private void generarGrafica(ActionEvent event) {
        String nodoSeleccionado = comboBoxNodos.getValue();
        String fechaInicio = (datePickerInicio.getValue() != null) ? datePickerInicio.getValue().toString() : null;
        String horaInicio = comboBoxHoraInicio.getValue();
        String fechaFin = (datePickerFin.getValue() != null) ? datePickerFin.getValue().toString() : null;
        String horaFin = comboBoxHoraFin.getValue();

        if (nodoSeleccionado == null || fechaInicio == null || horaInicio == null || fechaFin == null || horaFin == null) {
            System.out.println("Por favor selecciona todos los filtros.");
            return;
        }

        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
            String query = "SELECT r.hora, r.temperatura, r.humedad, r.luminosidad, r.lluvia " +
                           "FROM registro r INNER JOIN nodo n ON r.idNodo = n.idNodo " +
                           "WHERE n.nombreNodo = ? AND r.fecha BETWEEN ? AND ? AND r.hora BETWEEN ? AND ? " +
                           "ORDER BY r.hora";

            PreparedStatement stmt = conn.prepareStatement(query);
            stmt.setString(1, nodoSeleccionado);
            stmt.setString(2, fechaInicio);
            stmt.setString(3, fechaFin);
            stmt.setString(4, horaInicio);
            stmt.setString(5, horaFin);

            ResultSet rs = stmt.executeQuery();

            List<String> horas = new ArrayList<>();
            List<Number> temperaturas = new ArrayList<>();
            List<Number> humedades = new ArrayList<>();
            List<Number> luminosidades = new ArrayList<>();
            List<Number> lluvias = new ArrayList<>();

            while (rs.next()) {
                horas.add(rs.getString("hora"));
                temperaturas.add(rs.getDouble("temperatura"));
                humedades.add(rs.getDouble("humedad"));
                luminosidades.add(rs.getDouble("luminosidad"));
                lluvias.add(rs.getDouble("lluvia"));
            }

            Platform.runLater(() -> mostrarGrafica(horas, temperaturas, humedades, luminosidades, lluvias));
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("Error al generar la gráfica: " + e.getMessage());
        }
    }

    private void mostrarGrafica(List<String> horas, List<Number> temperaturas, List<Number> humedades, List<Number> luminosidades, List<Number> lluvias) {
        // Limpiar gráficas anteriores
        lineChartTemperatura.getData().clear();
        lineChartHumedad.getData().clear();
        lineChartLuminosidad.getData().clear();
        lineChartLluvia.getData().clear();

        // Simplificar etiquetas de hora
        List<String> horasSimplificadas = new ArrayList<>();
        int intervalo = 2; // Mostrar solo cada 2 etiquetas
        for (int i = 0; i < horas.size(); i++) {
            if (i % intervalo == 0) {
                horasSimplificadas.add(horas.get(i).substring(0, 5)); // HH:mm
            } else {
                horasSimplificadas.add(""); // Espacio vacío
            }
        }

        // Serie para Temperatura
        XYChart.Series<String, Number> serieTemperatura = new XYChart.Series<>();
        for (int i = 0; i < horas.size(); i++) {
            serieTemperatura.getData().add(new XYChart.Data<>(horas.get(i).substring(0, 5), temperaturas.get(i)));
        }

        // Serie para Humedad
        XYChart.Series<String, Number> serieHumedad = new XYChart.Series<>();
        for (int i = 0; i < horas.size(); i++) {
            serieHumedad.getData().add(new XYChart.Data<>(horas.get(i).substring(0, 5), humedades.get(i)));
        }

        // Serie para Luminosidad
        XYChart.Series<String, Number> serieLuminosidad = new XYChart.Series<>();
        for (int i = 0; i < horas.size(); i++) {
            serieLuminosidad.getData().add(new XYChart.Data<>(horas.get(i).substring(0, 5), luminosidades.get(i)));
        }

        // Serie para Lluvia
        XYChart.Series<String, Number> serieLluvia = new XYChart.Series<>();
        for (int i = 0; i < horas.size(); i++) {
            serieLluvia.getData().add(new XYChart.Data<>(horas.get(i).substring(0, 5), lluvias.get(i)));
        }

        // Agregar las series
        lineChartTemperatura.getData().add(serieTemperatura);
        lineChartHumedad.getData().add(serieHumedad);
        lineChartLuminosidad.getData().add(serieLuminosidad);
        lineChartLluvia.getData().add(serieLluvia);

        // Configurar ejes X
        configurarEjeX(lineChartTemperatura, horasSimplificadas);
        configurarEjeX(lineChartHumedad, horasSimplificadas);
        configurarEjeX(lineChartLuminosidad, horasSimplificadas);
        configurarEjeX(lineChartLluvia, horasSimplificadas);
    }

  private void configurarEjeX(LineChart<String, Number> lineChart, List<String> horasSimplificadas) {
    CategoryAxis xAxis = (CategoryAxis) lineChart.getXAxis();

    // Crear una lista sin duplicados
    ObservableList<String> categoriasUnicas = FXCollections.observableArrayList(new ArrayList<>(new HashSet<>(horasSimplificadas)));

    xAxis.setAutoRanging(false); // Evitar que el eje ajuste automáticamente
    xAxis.setTickLabelRotation(45); // Rotar etiquetas 45 grados
    xAxis.setTickLabelGap(10); // Espaciado entre etiquetas
    xAxis.setCategories(categoriasUnicas); // Establecer las categorías únicas
}


    @FXML
    private void presentarLectura(ActionEvent event) {
        try {
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("grafica2.fxml"));
            Parent root = fxmlLoader.load();
            Scene scene = new Scene(root);
            Stage stage = (Stage) ((Node) event.getSource()).getScene().getWindow();

            // Manejar minimizar/restaurar
            stage.iconifiedProperty().addListener((observable, oldValue, isMinimized) -> {
                if (isMinimized) {
                    System.out.println("Ventana minimizada. Deteniendo actualizaciones...");
                } else {
                    System.out.println("Ventana restaurada.");
                }
            });

            stage.setScene(scene);
            stage.setTitle("Lectura de Datos y Gráficas");
            stage.setMaximized(true);
            stage.show();
        } catch (IOException e) {
            System.err.println("Error al cargar la ventana: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
