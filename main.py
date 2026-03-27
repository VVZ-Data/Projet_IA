from games.jeux_1.main import main as a
from games.jeux_2.main import main as c

from sqlalchemy import create_engine, Base


if __name__ == "__main__":

    choice = input("a = allumette c = cubee : ")
    if choice == 'a':
        a()
    else:
        c()


