def subtract_from_100(number):
    return 100 - number

if __name__ == "__main__":
    try:
        user_input = int(input("Enter an integer to subtract from 100: "))
        result = subtract_from_100(user_input)
        print(f"100 - {user_input} = {result}")
    except ValueError:
        print("Please enter a valid integer.")