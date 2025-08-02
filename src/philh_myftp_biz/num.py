from . import array


def digit(number:int, index:int):
    return int(str(number)[index])

def shuffle_range(min, max):
    range_ = range(min, max+1)
    range = array.generate(range_)
    return array.shuffle(range)

def is_prime(num):

    pre = {
        0: False,
        1: False,
        2: True
    }

    if num in pre:
        return pre[num]

    else:

        if digit(num, -1) in [0, 2, 4, 5, 6, 8]:
            return False
        
        else:
            for i in range(2, num):
                if (num % i) == 0:
                    return False

            return True
