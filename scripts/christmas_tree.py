'''
The program should ask for your name and a number.
Then it should return a Christmas tree with as many levels as the number you entered, and below it, wishes using your name.

For example: for the number 6.
'''
def draw_christmas_tree(levels):
    # Draw the tree
    for i in range(levels):
        print(" " * (levels - i - 1) + "*" * (2 * i + 1))
    # Draw the trunk
    print(" " * (levels - 1) + "*")

def main():
    name = input("Podaj swoje imię: ")
    levels = int(input("Podaj liczbę pięter choinki: "))
    draw_christmas_tree(levels)
    print(f"Życzę Ci wesołych Świąt, {name}!")

if __name__ == "__main__":
    main()