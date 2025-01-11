
def is_valid_trap(trap: str):
    if len(trap) != 2:
        return False
    if not trap[0].isalpha():
        return False
    if not trap[1].isdigit():
        return False
    return True