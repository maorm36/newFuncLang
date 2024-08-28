from functools import reduce


# Solution 1: Fibonacci sequence generator
def fib(n):
    def fib_inner(x, a=0, b=1):
        return fib_inner(x-1, b, a+b) if x else a
    return list(map(fib_inner, range(n)))


# Solution 2: Concatenation of strings with spaces
def concat_with_space(lst):
    return reduce(lambda x, y: x + ' ' + y, lst)


# Solution 3: Cumulative sum of squares of even numbers in sublists
def cumulative_sum_of_squares(lst):
    return list(
        map(
            lambda sublist: reduce(
                lambda acc, x: (
                    (lambda y: (
                        (lambda z: (
                            (lambda w: w ** 2)(z) if z % 2 == 0 else 0
                        ))(y)
                    ))(x) + acc
                ),
                sublist,
                0
            ),
            lst
        )
    )


# Solution 4: Factorial and Exponentiation using higher-order functions
def cumulative_operation(op):
    return lambda seq: reduce(op, seq)


# Factorial function
factorial = cumulative_operation(lambda x, y: x * y)


# Exponentiation function
def exponentiation(seq):
    def exp(base, exponent):
        return base ** exponent

    return reduce(lambda acc, elem: exp(elem, acc), reversed(seq))


# Solution 5: One-line function using filter, map, and reduce
def one_line_sum_squares(lst):
    return reduce(lambda x, y: x + y, map(lambda x: x**2, filter(lambda num: num % 2 == 0, lst)))


# Solution 6: Counting palindromes in sublists
def count_palindromes_per_sublist(lst):
    return list(map(lambda sublist: reduce(lambda count, s: count + (s == s[::-1]), sublist, 0), lst))


#Solution 7: Explaining the term "lazy evaluation" in the context
#In this example, generate_values() is used directly in the list comprehension
#to compute the squares. Values are generated one by one as needed. Each value
#is passed to the square function to get its square. This is called lazy evaluation
#because values are computed and processed only when needed, without storing all
#values in memory beforehand.

#Lazy Evaluation: This means delaying the computation of values until they are
#actually needed. The generator produces values only on demand, which saves memory,
#especially with large data sets, and improves efficiency.


# Solution 8: Prime numbers sorted in descending order
def primes_sorted_desc(lst):
    return sorted([x for x in lst if x >= 1 and all(x % i != 0 for i in range(2, int(x**0.5) + 1))], reverse=True)


def main():
    while True:
        print("\nChoose a function to run:")
        print("1. Fibonacci sequence generator")
        print("2. Concatenation of strings with spaces")
        print("3. Cumulative sum of squares of even numbers in sublists")
        print("4. Factorial and Exponentiation functions")
        print("5. One-line sum of squares of even numbers")
        print("6. Counting palindromes in sublists")
        print("8. Prime numbers sorted in descending order")
        print("0. Exit")
        choice = input("Enter your choice (1-8): ")

        if choice == '1':
            n = int(input("Enter the number of Fibonacci numbers to generate: "))
            print(fib(n))

        elif choice == '2':
            input_lines = []
            print("Enter strings one by one. Press ENTER without typing to finish:")
            while True:
                line = input()
                if line == "":
                    break
                input_lines.append(line)
            result = concat_with_space(input_lines)
            print(result)

        elif choice == '3':
            input_lists = [
                [1, 2, 3, 4],
                [10, 15, 20, 25],
                [2, 4, 6, 8]
            ]
            print(cumulative_sum_of_squares(input_lists))

        elif choice == '4':
            factorial_input = range(1, 6)
            print(f"Factorial of 5: {factorial(factorial_input)}")  # Output: 120
            exponentiation_input = [2, 3, 4]
            print(f"Exponentiation 2^(3^4): {exponentiation(exponentiation_input)}")

        elif choice == '5':
            nums = [1, 2, 3, 4, 5, 6]
            print(one_line_sum_squares(nums))  # Output: 56

        elif choice == '6':
            list_of_lists = [['madam', 'racecar', 'hello'], ['noon', 'world'], ['level', 'python', 'rotor']]
            result = count_palindromes_per_sublist(list_of_lists)
            print(result)  # Output: [2, 1, 2]

        elif choice == '8':
            numbers = [10, 5, 15, 23, 29, 8, 1, 7, 13]
            result = primes_sorted_desc(numbers)
            print(result)  # Output: [29, 23, 13, 7, 5]

        elif choice == '0':
            print("Exiting.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
