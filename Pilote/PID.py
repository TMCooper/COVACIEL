from function.Pilote import Pilote
import RPi.GPIO as gpio

pid = Pilote(0.0, 0.0, 32, 33, 35)

# Test avec 1.5 ms de consigne et 0.0 de sortie (donc erreur = 1.5)
pi_output = pid.CalcPID(input=1.5, output=1.7)
print(f"PID = {pi_output}")

pi_output = pid.CalcPID(input=1.6, output=1.5)
print(f"PID = {pi_output}")

pid.stop()