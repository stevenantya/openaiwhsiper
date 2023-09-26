const int microphonePin = A0;
const long SAMPLING_RATE =  4000; //in Hz
const long INTERVAL = 1000000L / SAMPLING_RATE; // Time in microseconds for 4kHz sample rate
long previousMicros = 0;

void setup() {
  Serial.begin(250000); // Begin the serial communication
}

void loop() {
  long currentMicros = micros();
  
  if (currentMicros - previousMicros >= INTERVAL) {
    previousMicros = currentMicros;
    
    int audioValue = analogRead(microphonePin);
    Serial.println(audioValue);
  }
}