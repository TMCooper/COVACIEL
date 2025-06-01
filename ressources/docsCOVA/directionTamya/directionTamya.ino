#include <Servo.h>

Servo servoDirection;  // Création de l'objet Servo

const int pinServo = 10;  // Broche D10 pour le servo

void setup() {
  servoDirection.attach(pinServo);  // Attache du servo à D10
  Serial.begin(115200);
  Serial.println("Entrez une consigne de direction entre -1.0 et 1.0 :");
}

void loop() {
  verifierConsigneDirection();
}

void verifierConsigneDirection() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // Lire la consigne jusqu'au saut de ligne
    input.trim();  // Supprimer les espaces ou les retours à la ligne

    float consigneDirection = input.toFloat();  // Conversion de la chaîne en nombre

    if (consigneDirection >= -1.0 && consigneDirection <= 1.0) {
      piloterDirection(consigneDirection);
      Serial.print("Consigne de direction mise à jour : ");
      Serial.println(consigneDirection);
    } else {
      Serial.println("Erreur : La consigne doit être entre -1.0 et 1.0.");
    }
  }
}

void piloterDirection(float consigne) {
  // Conversion de la consigne entre -1.0 et 1.0 vers un angle entre 0° et 180°
  int angleServo = map(consigne * 100, -100, 100, 0, 180);
  servoDirection.write(angleServo);  // Déplacer le servo à l'angle correspondant
}
