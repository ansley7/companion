int pingPin = 7;
int echoPin = 5;

void setup() {
  Serial.begin(115200);
  // put your setup code here, to run once:

}

void loop() {
  long duration, inches, cm;
  // put your main code here, to run repeatedly:
  pinMode(pingPin, OUTPUT);
  digitalWrite(pingPin, LOW);
  delayMicroseconds(2);
  digitalWrite(pingPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(pingPin, LOW);
  pinMode(echoPin, INPUT);
  duration = pulseIn(echoPin, HIGH);
  inches = microsecondsToInches(duration);
  Serial.print(inches);
  Serial.print("in, ");
  Serial.println();
  delay(30);
//  Serial.println("LF");


}
long microsecondsToInches(long microseconds) {
  return microseconds / 74 / 2;
}
