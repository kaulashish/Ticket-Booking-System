import models, functions, sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from getpass import getpass

engine = create_engine(
    "mysql+mysqldb://root:root@localhost:3306/ticketsystem", echo=False
)
session = sessionmaker(engine)()

print("\n")
print("login".center(40, "*"))
username = input("username: ")
user_obj = functions.search_user(username)

if len(functions.search_user(username)) == 0:
    print("\n")
    print("\tUser not it database...")
    prompt = str(input("signup? (y/n): "))
    if prompt.lower() == "y":
        print("\n")
        print("signup".center(40, "*"))
        functions.add_user(username)
    elif prompt.lower() == "n":
        print("\nProgram will end now.")
        sys.exit()

else:
    password = getpass("Enter password: ")
    functions.password_checking(username, password)
    functions.welcome_message(username)

session.close()