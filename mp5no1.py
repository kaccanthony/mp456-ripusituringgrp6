print("GROUP 6 - MP5")
print("School: FEU-TECH")
print("Machine Problem number - 1")

numbers = [63, 52, 10, 42, 32, 17, 60, 45, 47, 39, 71, 55, 41, 95, 70, 48, 42, 32, 13, 35]

#a
print("(a) List:")
print(numbers)

#b
average = sum(numbers) / len(numbers)
print(f"\n(b) Average: {average}")

#c
print(f"\n(c) Largest value: {max(numbers)}")
print(f"    Smallest value: {min(numbers)}")

#d
unique = sorted(set(numbers))

print(f"\n(d) Second largest: {unique[-2]}")
print(f"    Second smallest: {unique[1]}")

#e
even_count = 0
for num in numbers:
    if num % 2 == 0:
        even_count += 1

print(f"\n(e) Number of even numbers: {even_count}")

#f
odd_count = 0
for num in numbers:
    if num % 2 != 0:
        odd_count += 1

print(f"\n(f) Number of odd numbers: {odd_count}")