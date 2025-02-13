# -*- coding: utf-8 -*-
import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import time
import sys

# Configuración global (¡MODIFICA ESTO!)
PUERTO_ARDUINO = 'COM3'  # Windows: 'COM3', Linux/Mac: '/dev/ttyUSB0'
TIEMPO_MUESTREO = 300    # Segundos de adquisición (5 minutos)
TEMPERATURA_OBJETIVO = 1 # °C sobre la ambiente para calcular tiempo

def modelo_enfriamiento(t, k, T_amb):
    """Modelo de la ley de enfriamiento de Newton"""
    return T_amb + (T0 - T_amb) * np.exp(-k * t)

def main():
    global T0  # Temperatura inicial
    
    # ==================================================================
    # 1. Adquisición de datos desde Arduino
    # ==================================================================
    try:
        print(f"Conectando con Arduino en {PUERTO_ARDUINO}...")
        with serial.Serial(PUERTO_ARDUINO, 9600, timeout=1) as ser:
            ser.flushInput()
            datos = []
            start_time = time.time()
            
            print(f"Adquiriendo datos por {TIEMPO_MUESTREO} segundos...")
            print("Presiona Ctrl+C para detener anticipadamente")
            
            while (time.time() - start_time) < TIEMPO_MUESTREO:
                try:
                    linea = ser.readline().decode().strip()
                    temperatura = float(linea)
                    tiempo_actual = time.time() - start_time
                    datos.append([tiempo_actual, temperatura])
                    print(f"T: {tiempo_actual:5.1f}s | Temp: {temperatura:5.2f}°C")
                except (ValueError, UnicodeDecodeError):
                    continue
                except KeyboardInterrupt:
                    break
            
            datos = np.array(datos)
            np.savetxt('datos_enfriamiento.csv', datos, 
                       delimiter=',', 
                       header='Tiempo(s),Temperatura(C)',
                       fmt='%.4f')
            
    except serial.SerialException:
        print("\n¡Error de conexión! Usando datos de ejemplo...")
        # Generar datos sintéticos para demostración
        t = np.linspace(0, 300, 50)
        k_real = 0.015
        T_amb_real = 25.0
        T0 = 90.0
        datos = np.column_stack((t, modelo_enfriamiento(t, k_real, T_amb_real) + np.random.normal(0, 0.5, len(t))))
    
    # ==================================================================
    # 2. Procesamiento de datos
    # ==================================================================
    tiempos = datos[:, 0]
    temperaturas = datos[:, 1]
    T0 = temperaturas[0]  # Temperatura inicial
    
    # Ajuste de curva
    params, cov = curve_fit(modelo_enfriamiento, tiempos, temperaturas, p0=[0.01, 25])
    k, T_amb = params
    error_k = np.sqrt(cov[0,0])
    
    # Cálculo del tiempo de enfriamiento
    t_enfriamiento = -np.log(TEMPERATURA_OBJETIVO/(T0 - T_amb)) / k if (T0 - T_amb) > TEMPERATURA_OBJETIVO else np.inf
    
    # ==================================================================
    # 3. Visualización de resultados
    # ==================================================================
    plt.figure(figsize=(10, 6))
    
    # Datos experimentales
    plt.scatter(tiempos, temperaturas, color='crimson', s=20, 
                label='Datos reales' if 'real' in locals() else 'Datos sintéticos')
    
    # Curva ajustada
    t_ajuste = np.linspace(0, max(tiempos), 100)
    plt.plot(t_ajuste, modelo_enfriamiento(t_ajuste, k, T_amb), 
             'navy', linewidth=2, 
             label=f'Ajuste: $T(t) = {T_amb:.1f} + ({T0:.1f}-{T_amb:.1f})e^{{-{k:.4f}t}}$')
    
    # Líneas de referencia
    plt.axhline(T_amb, color='green', linestyle='--', alpha=0.7, label='Temperatura ambiente')
    plt.axhline(T_amb + TEMPERATURA_OBJETIVO, color='orange', linestyle=':', 
                label=f'Objetivo ({TEMPERATURA_OBJETIVO}°C sobre ambiente)')
    
    # Anotaciones
    plt.text(0.6*max(tiempos), 0.8*T0, 
             f'Tiempo característico (τ = 1/k): {1/k:.1f} s\n' +
             f'Tiempo para objetivo: {t_enfriamiento:.1f} s',
             bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round'))
    
    # Formato del gráfico
    plt.title('Ley de Enfriamiento de Newton - Resultados', fontsize=14)
    plt.xlabel('Tiempo (segundos)', fontsize=12)
    plt.ylabel('Temperatura (°C)', fontsize=12)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # Mostrar gráfico
    plt.show()

if __name__ == "__main__":
    main()
    sys.exit(0)