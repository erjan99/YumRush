from random import randint

def generateOTP():
    code = randint(100000, 999999)
    return code

def verifyOTP(code, user_code):
    if code==user_code:
        return True
    else:
        return False
