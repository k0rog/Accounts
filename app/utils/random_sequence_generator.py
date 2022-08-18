import random


def generate_random_digit_sequence(length: int) -> str:
    return ''.join(["%s" % random.randint(0, 9) for _ in range(0, length)])
