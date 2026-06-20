print("GROUP 6 - MP4")
print("School: FEU-TECH")
print("Machine Problem number - 5")

try:
    numbers = []

    print("\nEnter numbers one at a time.")

    while True:
        user_input = input("Enter a number (or 'done'): ")

        if user_input.lower() == "done":
            break

        try:
            numbers.append(int(user_input))
        except ValueError:
            print("Error: Please enter a valid integer.")
            continue

    if len(numbers) < 2:
        raise IndexError("At least 2 numbers are required.")

    print("\nOriginal list:", numbers)

    # (a) Replace second entry
    numbers[1] = 17
    print("(a)", numbers)

    # (b) Append 4, 5, 6
    numbers.extend([4, 5, 6])
    print("(b)", numbers)

    # (c) Pop first entry
    numbers.pop(0)
    print("(c)", numbers)

    # (d) Sort the list
    numbers.sort()
    print("(d)", numbers)

    # (e) Double the list
    numbers = numbers * 2
    print("(e)", numbers)

    # (f) Insert 25 at index 3
    numbers.insert(3, 25)
    print("(f)", numbers)

    print("\nFinal list:", numbers)

except IndexError as e:
    print("Error:", e)
except Exception as e:
    print("Unexpected error:", e)
