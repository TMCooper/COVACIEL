import lgpio
import time

GPIO_NUM = 19  # GPIO19

def main():
    print("Initialisation sans callback (lecture manuelle)...")

    try:
        h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(h, GPIO_NUM)

        last_state = lgpio.gpio_read(h, GPIO_NUM)
        print("État initial :", last_state)

        while True:
            state = lgpio.gpio_read(h, GPIO_NUM)
            if state != last_state:
                print("Changement détecté, état actuel :", state)
                last_state = state

    except KeyboardInterrupt:
        print("\nArrêt du programme par l'utilisateur.")
    finally:
        lgpio.gpiochip_close(h)
        print("Nettoyage GPIO terminé.")

if __name__ == '__main__':
    main()
