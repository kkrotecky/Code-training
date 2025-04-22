import random

def rzut_kostka():
    return random.randint(1, 6)

def gra_kosci():
    print("Witaj, jak masz na imię?")
    imie = input("Podaj swoje imię: ")
    print(f"Witaj, {imie}!")
    print("Zasady gry są następujące: rzucasz 2 razy kostką. Za każde wyrzucone oczko po pierwszm rzucie dostajesz 1 punkt.\nZa każde wyrzucone oczko po drugim rzucie dostajesz mnożnik, przez ilość wyrzuconych oczek.")
    print("Przykładowo jeśli w pierwszym rzucie wyrzucisz 3 oczka, a w drugim 2 oczka, to pomnożymy 3*2=6.")
    print("Jeśli wyrzucisz 1 oczko w pierwszym rzucie, a 2 oczka w drugim rzucie, to dostaniesz 1*2=2 punkty i tak dalej.")
    print("Wygrywasz, jeżli zdobędziesz więcej punktów niż komputer.")
    print("Czy chcesz zagrać? (tak/nie)")
    odpowiedz = input("Podaj odpowiedź: ").lower()
    if odpowiedz == "tak":
        print("Super! Zaczynamy grę!")
    else:
        print("Dziękuję za grę! Do zobaczenia następnym razem!")
        return False
    return True

rzut1 = print(f"Rzut 1: {rzut_kostka()}")
rzut2 = print(f"Rzut 2: {rzut_kostka()}")
