#Name: Group 6
#School: FEU-TECH
#Machine Problem number - 2

class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius ** 2
    
    def perimeter(self):
        return 2 * 3.14 * self.radius
    
radius = input("Enter radius: ")

if (float(radius) < 0):
    print("Enter a positive number.")
elif "." in radius:
    print("Input a whole number value.")
else:
    radius = int(radius)
    c = Circle(radius)

    print(f"The answer is: {c.area()}")
    print(f"Here is the Answer: {c.perimeter()}")
