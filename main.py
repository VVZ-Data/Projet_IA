from games.jeux_1.main import main as a
from games.jeux_2.main import main as c


if __name__ == "__main__":
    choice = input("a = allumette c = cubee : ")
    if choice == 'a':
        a()
    else:
        c()