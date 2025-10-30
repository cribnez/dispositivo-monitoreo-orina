
import tkinter as tk
from tkinter import Label, Button
import threading
import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt
import cv2

# -------------------------
# CONFIGURACIÓN DE PINES
# -------------------------
FLOW_SENSOR_PIN = 17
ULTRASONIC_TRIG = 22
ULTRASONIC_ECHO = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ULTRASONIC_TRIG, GPIO.OUT)
GPIO.setup(ULTRASONIC_ECHO, GPIO.IN)

# -------------------------
# VARIABLES GLOBALES
# -------------------------
pulse_count = 0
water_ml = 0.0
distances = []
volumes = []
is_measuring = False

# -------------------------
# FUNCIONES DE SENSOR
# -------------------------
def countPulse(channel):
    global pulse_count
    pulse_count += 1

GPIO.add_event_detect(FLOW_SENSOR_PIN, GPIO.FALLING, callback=countPulse)

def medir_distancia():
    GPIO.output(ULTRASONIC_TRIG, True)
    time.sleep(0.00001)
    GPIO.output(ULTRASONIC_TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ULTRASONIC_ECHO) == 0:
        start_time = time.time()
    while GPIO.input(ULTRASONIC_ECHO) == 1:
        stop_time = time.time()

    tiempo = stop_time - start_time
    distancia = (tiempo * 34300) / 2  # cm
    return distancia

# -------------------------
# FUNCIÓN PRINCIPAL DE MEDICIÓN
# -------------------------
def medir_flujo():
    global pulse_count, water_ml, distances, volumes, is_measuring
    pulse_count = 0
    water_ml = 0
    distances = []
    volumes = []
    is_measuring = True

    t_inicio = time.time()
    tiempo_total = 10  # segundos de medición

    while time.time() - t_inicio < tiempo_total and is_measuring:
        flow = pulse_count / 7.5  # conversión aproximada a ml/s
        water_ml += flow
        distancia = medir_distancia()
        distances.append(distancia)
        volumes.append(water_ml)
        label_resultado.config(text=f"Volumen total: {round(water_ml, 2)} mL")
        ventana.update_idletasks()
        time.sleep(1)
        pulse_count = 0

    # Captura de imagen
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        cv2.imwrite("/home/pi/ultima_captura.jpg", frame)
    cam.release()

    # Mostrar gráfica
    plt.plot(volumes, label="Volumen (mL)")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Volumen (mL)")
    plt.title("Uroflujometría - Flujo de Orina")
    plt.legend()
    plt.show()

    is_measuring = False

def iniciar_medicion():
    # Ejecuta la medición en un hilo separado
    hilo = threading.Thread(target=medir_flujo)
    hilo.start()

# -------------------------
# INTERFAZ GRÁFICA
# -------------------------
ventana = tk.Tk()
ventana.title("Medición de Flujo Urinario")
ventana.geometry("500x400")
ventana.configure(bg="#F0F4F8")

label_titulo = Label(ventana, text="Sistema de Uroflujometría", font=("Arial", 18, "bold"), bg="#F0F4F8")
label_titulo.pack(pady=10)

btn_inicio = Button(ventana, text="Iniciar Medición", font=("Arial", 14), bg="#4CAF50", fg="white", command=iniciar_medicion)
btn_inicio.pack(pady=20)

label_resultado = Label(ventana, text="Volumen total: 0 mL", font=("Arial", 14), bg="#F0F4F8")
label_resultado.pack(pady=10)

ventana.mainloop()
GPIO.cleanup()





