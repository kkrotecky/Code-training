import random

def rzut_kostka():
    return random.randint(1, 6)

def intro():
    print("Witam! Jak masz na imię?")
    imie = input("Twoje imie: ")
    print("Witaj, " + imie + "! ")
    

def instrukcja():
    print("Zasady gry są następujące: rzucasz 2 razy kostką. Za każde wyrzucone oczko po pierwszm rzucie dostajesz 1 punkt.\nZa każde wyrzucone oczko po drugim rzucie dostajesz mnożnik, przez ilość wyrzuconych oczek.")
    print("Przykładowo jeśli w pierwszym rzucie wyrzucisz 3 oczka, a w drugim 2 oczka, to pomnożymy 3*2=6.")
    print("Jeśli wyrzucisz 1 oczko w pierwszym rzucie, a 2 oczka w drugim rzucie, to dostaniesz 1*2=2 punkty i tak dalej.")
    print("Wygrywasz, jeżli zdobędziesz więcej punktów niż komputer.")

def core():
    rzut1 = rzut_kostka()
    rzut2 = rzut_kostka()
    wynik = rzut1 * rzut2
    
    print("Kliknij Enter by zacząć...")
    input()
    print(f"Pierwszy rzut: {rzut1}")
    print("Kliknij Enter by zacząć...")
    input()
    print(f"Drugi rzut: {rzut2}")
    print(f"Zdobyłeś: {wynik} punktów!")

intro()
instrukcja()
core()
