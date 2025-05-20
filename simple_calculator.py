def core():
    while True:
        print("What would you like to do?:")
        base = int(input("1. Add\n2. Substract\n3. Multiply\n4. Divide\n \nPlease write the number (1/2/3/4):"))
    
        if base == 1:
            addition()
            break
        elif base == 2:
                substraction()
                break
        elif base ==3:
                multiplication()
                break
        elif base ==4:
                division()
                break
        else: 
            print("\nWrite a write number 1, 2, 3 or 4!!!")
            input("\nTo continue press Enter:\n")



def addition():
    add = int(input("First number: "))
    add2 = int(input("Second number: "))
    solution = add + add2
    print(f"{add} + {add2} = {solution}")

def substraction():
     substract = int(input("First number: "))
     substract2 = int(input("Second number: "))
     solution = substract - substract2
     print(f"{substract} - {substract2} = {solution}")

def multiplication():
     multi = int(input("First number: "))
     multi2 = int(input("Second number: "))
     solution = multi * multi2
     print(f"{multi} x {multi2} = {solution}")

def division():
     divide = int(input("First number: "))
     divide2 = int(input("Second number: "))
     solution = divide / divide2
     print(f"{divide} / {divide2} = {solution}")

def main():
    while True:
        core()
        restart = input("Would you like to continue?: (Yes/No)").strip().lower()
        if restart != 'yes':
            break

main()