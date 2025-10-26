from src.modules.commutative import generate_commutatives

def main():
    ids = input('Enter IDS: ')
    print(generate_commutatives(ids))