#Name: GROUP 6
#School: FEU-TECH
#Machine Problem number - 4

class RomanConverter:

    def __init__(self):
        self.roman_map = {
            'I': 1, 'V': 5, 'X': 10,
            'L': 50, 'C': 100, 'D': 500, 'M': 1000
        }

        self.int_to_roman_map = [
            (1000, "M"), (900, "CM"), (500, "D"),
            (400, "CD"), (100, "C"), (90, "XC"),
            (50, "L"), (40, "XL"), (10, "X"),
            (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
        ]

    def integer_to_roman(self, number):
        result = ""

        for value, symbol in self.int_to_roman_map:
            while number >= value:
                result += symbol
                number -= value

        return result

    def roman_to_integer(self, roman):
        roman = roman.upper()

        total = 0
        prev_value = 0

        for char in reversed(roman):
            value = self.roman_map[char]

            if value < prev_value:
                total -= value
            else:
                total += value

            prev_value = value

        return total

    def is_valid_roman(self, roman):
        roman = roman.upper()

        valid_chars = set(self.roman_map.keys())

        if len(roman) == 0:
            return False

        for char in roman:
            if char not in valid_chars:
                return False

        return True


class RomanNumeralApp:

    def __init__(self):
        self.converter = RomanConverter()

    def display_menu(self):
        print("\nGROUP 6 MENU - MP4")
        print("1. Convert an Integer to a Roman Numeral")
        print("2. Convert a Roman Numeral to an Integer")
        print("3. Exit")

    def run(self):
        while True:

            self.display_menu()

            opt = input("\nEnter your choice: ")

            if opt == "1":

                try:
                    number = int(input("\nEnter Integer - "))

                    if number <= 0:
                        print("Error: Please enter a positive whole number.")
                    elif number > 5000:
                        print("Error: MAX VALUE IS 5000.")
                    else:
                        roman = self.converter.integer_to_roman(number)
                        print("Output in Roman Numerals is:", roman)

                except ValueError:
                    print("Error: Only whole number values are accepted.")

            elif opt == "2":

                roman = input("\nEnter Roman Numeral - ").strip()

                if not self.converter.is_valid_roman(roman):
                    print("Error: Invalid Roman Numeral.")
                else:
                    integer_value = self.converter.roman_to_integer(roman)
                    print("Output in Integer is -", integer_value)

            elif opt == "3":
                print("\nProgram terminated.")
                break

            else:
                print("Error: Invalid menu opt.")

app = RomanNumeralApp()
app.run()
