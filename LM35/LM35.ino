void setup() {
  Serial.begin(9600); // Inicia comunicación serial
}

void loop() {
  int rawValue = analogRead(A0); // Lectura del sensor (0-1023)
  float temp = (rawValue * 5.0 / 1023.0) * 100; // Convertir a °C (LM35: 10mV/°C)
  
  Serial.println(temp); // Envía temperatura por serial
  delay(1000); // Espera 1 segundo
}