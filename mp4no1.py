#Name: Group 6
#School: FEU-TECH
#Machine Problem number - 1

class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width

try:
    length_input = input("Enter Length value: ")
    if float(length_input) <= 0:
        print("The number is not a positive integer:")
    elif not float(length_input).is_integer():
        print("Input the correct data format")
    else:
        width_input = input("Enter the width of the rectangle: ")
        if float(width_input) <= 0:
            print("The number is not a positive integer:")
        elif not float(width_input).is_integer():
            print("Input the correct data format")
        else:
            rect = Rectangle(int(float(length_input)), int(float(width_input)))
            print(f"The Area of the Rectangle is:{rect.area()}")
except ValueError:
    print("Input the correct data format")