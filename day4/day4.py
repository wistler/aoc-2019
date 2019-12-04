
def is_valid(num, strictlyTwoDigitMatch=False):
    digits = [int(digit) for digit in str(num)]
    if len(digits) != 6:
        return False

    digits = [None] + digits + [None]  # padding

    twoAdjDigitsAreSame = False
    for w,x,y,z in [digits[i:i+4] for i in range(len(digits)-3)]:
        if x > y:
            return False
        if x == y:
            if not strictlyTwoDigitMatch or (w != x and y != z):
                twoAdjDigitsAreSame = True
    
    if not twoAdjDigitsAreSame:
        return False
    
    return True


if __name__ == '__main__':

    # test
    assert is_valid(111111) is True
    assert is_valid(223450) is False
    assert is_valid(123789) is False

    assert is_valid(223450, True) is False
    assert is_valid(111222, True) is False
    assert is_valid(112222, True) is True
    assert is_valid(111122, True) is True
    assert is_valid(123444, True) is False
    assert is_valid(112233, True) is True

    start = 172851
    stop = 675869

    firstCount = 0
    secondCount = 0
    for num in range(start, stop+1):
        # part 1
        if is_valid(num):
            firstCount += 1
        
        # part 2
        if is_valid(num, strictlyTwoDigitMatch=True):
            secondCount += 1
    
    print("Part 1 Count = {}\nPart 2 Count = {}".format(firstCount, secondCount))
