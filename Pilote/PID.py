from function.Pilote import Pilote

pid = Pilote(0.0, 0.0, 32, 33, 35)

# Liste de couples (input, output) prédéfinis
test_data = [
    (1.5, 1.7),
    (1.6, 1.5),
    (2.0, 1.9),
    (1.8, 2.0),
    (1.5, 1.7),
    (1.5, 2.0),
]

# Traitement et affichage des résultats
for i, (input_val, output_val) in enumerate(test_data):
    pid_output = pid.CalcPID(input=input_val, output=output_val)
    print(f"Test {i+1}: input={input_val}, output={output_val} → PID = {pid_output:.3f}")

# Arrêt explicite
pid.stop()