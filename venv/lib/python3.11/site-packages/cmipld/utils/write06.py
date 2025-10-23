def errprint(*text):
    RED = "\033[91m"
    RESET = "\033[0m"
    print(RED, text, RESET)


def bprint(*text):
    other = "\033[94m"
    RESET = "\033[0m"
    print(other, text, RESET)


def get_datetime():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
