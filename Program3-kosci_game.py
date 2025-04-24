import random

def rzut_kostka():
    return random.randint(1, 6)

def intro():
    print("Witam! Jak się nazywacie?")
    imie1 = input("Imię gracza nr 1: ")
    print("Witaj, " + imie1 + "! ")

    imie2 = input("Imię gracza nr 2: ")
    print("Witaj, " + imie2 + "! ")

    return imie1, imie2
    

def instrukcja():
    
    print("Zasady gry są następujące: każdy gracz rzuca 2 razy kostką. Za każde wyrzucone oczko po pierwszm rzucie dostaje 1 punkt.\nZa każde wyrzucone oczko po drugim rzucie otrzymuje mnożnik, przez ilość wyrzuconych oczek.")
    print("Przykładowo jeśli w pierwszym rzucie gracz wyrzuci 3 oczka, a w drugim 2 oczka, to pomnożymy 3*2=6.")
    print("Wygrywa gracz, który zdobędzie więcej punktów.")

def core():
    rzut1 = rzut_kostka()
    rzut2 = rzut_kostka()
    wynik = rzut1 * rzut2

    rzut3 = rzut_kostka()
    rzut4 = rzut_kostka()
    wynik2 = rzut3 * rzut4
    
    print(f"Rozpoczyna {imie1}")
    print("Kliknij Enter by rzucić kostką...")
    input()
    print(f"Pierwszy rzut: {rzut1}")
    print("Kliknij Enter oddać drugi rzut...")
    input()
    print(f"Drugi rzut: {rzut2}")

    print(f"Brawo! Twój wynik to: {wynik} punktów!")

    print(f"Kolej {imie2} ")

    print("Kliknij Enter by rzucić kostką...")
    input()
    print(f"Pierwszy rzut: {rzut3}")
    print("Kliknij Enter oddać drugi rzut...")
    input()
    print(f"Drugi rzut: {rzut4}")

    print(f"Brawo! Twój wynik to: {wynik2} punktów!")

    if wynik > wynik2:
        print(f"Wygrywa {imie1} z {wynik} punktami!")
    elif wynik2 > wynik:
        print(f"Wygrywa {imie2} z {wynik2} punktami!")
    else:
        print("Remis! Obaj gracze zdobyli tyle samo punktów.")

    print("Czy chcecie zagrać jeszcze raz? (tak/nie)")
    odpowiedz = input()
    if odpowiedz.lower() == "tak":
        core()
    else:
        print("Dzięki za grę! Do widzenia!")


imie1, imie2 = intro()
instrukcja()
core()
