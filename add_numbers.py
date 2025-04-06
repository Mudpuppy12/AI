#!/usr/bin/env python

def main():
    print("Program to add two numbers")
    
    # Get first number with validation
    while True:
        try:
            num1 = float(input("Enter the first number: "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    # Get second number with validation
    while True:
        try:
            num2 = float(input("Enter the second number: "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    # Calculate the sum
    result = num1 + num2
    
    # Display the result
    print(f"The sum of {num1} and {num2} is: {result}")

if __name__ == "__main__":
    main()