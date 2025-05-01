
def cyferki():
    user_input = input("Wpisz cyfrę: ")

    if user_input.isdigit():
        cyfra = int(user_input)
        if 0 <= cyfra <= 9:
            print(f"Wpisana przez ciebie cyfra to {cyfra}")
        else:
            print(f"To nie jest cyfra!!!")
    else:
        print("Wpisz poprawny znak!")

cyferki()

