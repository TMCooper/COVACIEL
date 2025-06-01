const int pwmPin = 9;  // Pin de sortie du signal PWM
const unsigned long periode = 20000;  // Période de 50 ms en microsecondes
float vitesse = 0;  // Consigne de vitesse initiale
unsigned long deb = 0 ;
void setup() {
  pinMode(pwmPin, OUTPUT);
  Serial.begin(115200);  // Initialisation de la communication série
  Serial.println("Entrez une consigne de vitesse entre -1.0 et 1.0 :");
  deb = micros();
}

void loop() {
  // Vérification des entrées sur le port série
  // if(deb < 5000)
  //   vitesse = 0 ;
  // else{
  //     vitesse = sin(2 * PI * 0.2 * micros()) * 0.5;
  // }
  verifierConsigne();

  
  
  // Calcul du rapport cyclique et génération du signal PWM
  float rapportCyclique = calculerRapportCyclique(vitesse);
  genererSignalPWM(pwmPin, rapportCyclique);
}

void verifierConsigne() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // Lire la consigne jusqu'au saut de ligne
    input.trim();  // Supprimer les espaces ou les retours à la ligne

    float nouvelleVitesse = input.toFloat();  // Conversion de la chaîne en nombre

    if (nouvelleVitesse >= -1.0 && nouvelleVitesse <= 1.0) {
      vitesse = nouvelleVitesse;  // Mettre à jour la consigne de vitesse
      Serial.print("Consigne de vitesse mise à jour : ");
      Serial.println(vitesse);
    } else {
      Serial.println("Erreur : La consigne doit être entre -1.0 et 1.0.");
    }
  }
}

float calculerRapportCyclique(float vitesse) {
  // Conversion de la vitesse vers la durée d'état haut
  float dureeEtatHaut;
  if (vitesse == 0) {
    dureeEtatHaut = 1.5;
  } else if (vitesse > 0) {
    dureeEtatHaut = 1.5 + vitesse * (2.0 - 1.5);  // Interpolation vers 2 ms
  } else {
    dureeEtatHaut = 1.5 + vitesse * (1.3 - 1.5);  // Interpolation vers 1.3 ms
  }
  
  // Calcul du rapport cyclique correspondant
  //Serial.print("Rapport cyclique : ");
  //Serial.println((dureeEtatHaut / 20.0) * 100.0);
  return (dureeEtatHaut / 20.0) * 100.0;  // Convertir en %
}

void genererSignalPWM(int pin, float rapportCyclique) {
  static unsigned long debutCycle = micros();
  unsigned long dureeEtatHaut = (unsigned long)((rapportCyclique / 100.0) * periode);
  unsigned long actuel = micros();
  if (actuel - debutCycle < dureeEtatHaut) {
    digitalWrite(pin, HIGH);
  } else {
    digitalWrite(pin, LOW);
  }

  // Réinitialisation du cycle
  if (actuel - debutCycle >= periode) {
    debutCycle = actuel;
  }
}
