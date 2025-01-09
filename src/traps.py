
def is_valid_trap(trap: str):
    if len(trap) != 2:
        print(" bad len")
        return False
    if not trap[0].isalpha():
        print("not letter", trap[0])
        return False
    if not trap[1].isdigit():
        print ("not numb")
        return False
    return True