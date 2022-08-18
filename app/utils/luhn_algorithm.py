from functools import reduce


def calculate_checksum(code: str) -> int:
    # Pre-calculated results of multiplication by 2 with a deduction of 9 for large digits.
    # The index number is equal to the number on which the operation is performed
    LOOKUP = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)
    code = reduce(str.__add__, filter(str.isdigit, code))
    evens = sum(int(i) for i in code[1::2])
    odds = sum(LOOKUP[int(i)] for i in code[0::2])
    return (evens + odds) % 10


def calculate_luhn(code: str) -> int:
    checksum = calculate_checksum(code)

    return 0 if checksum == 0 else 10 - checksum
