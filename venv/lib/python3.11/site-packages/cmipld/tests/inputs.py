import argparse


def run():
    parser = argparse.ArgumentParser(description="Test inputs")
    parser.add_argument("--flag", action="store_true", help="Flag to test")
    parser.add_argument("--option", help="Option to test")
    parser.add_argument("--updated", nargs="+", help="Inputs to test")

    args = parser.parse_args()
    print('Inputs test')
    print(args)
    return None
