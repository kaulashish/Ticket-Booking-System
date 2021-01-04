import models, sys, time
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy import create_engine
from getpass import getpass
import numpy as np
from tabulate import tabulate

engine = create_engine(
    "mysql+mysqldb://root:root@localhost:3306/ticketsystem", echo=False
)
session = sessionmaker(engine)()


def get_max_id(table, column):
    val = session.query(table).order_by(column.desc()).first()
    return val


def add_user(username):
    max_user_id = get_max_id(models.User, models.User.userid)
    if max_user_id == None:
        max_user_id = 1
    else:
        max_user_id = max_user_id.userid + 1
    password = getpass("Enter password: ")
    pass_len = len(password)
    while pass_len < 8:
        print("Password length should be greater or equal to 8, please enter again.")
        password = getpass("Enter password: ")
        pass_len = len(password)
    password_hash = models.User.create_password(password)

    while True:
        re_password = getpass("Re-enter password: ")
        if models.User.check_password_before_signup(re_password) == False:
            print("Passwords do not match.")
        else:
            break

    gender = str(input("Gender(M/F/O): "))
    age = int(input("Age: "))
    phone = input("Phone: ")

    while True:
        admin_status = input("Are you an admin? (y/n): ")
        if admin_status.lower() == "y":
            break
        elif admin_status.lower() == "n":
            break
        else:
            print("invalid input, please try again")
    if admin_status == "n":
        user_obj = models.User(
            userid=max_user_id,
            username=username,
            usertype=0,
            gender=gender.upper(),
            age=age,
            phone=phone,
            password_hash=password_hash,
        )
    elif admin_status == "y":
        user_obj = models.User(
            userid=max_user_id,
            username=username,
            gender=gender.upper(),
            age=age,
            phone=phone,
            usertype=1,
            password_hash=password_hash,
        )
    session.add(user_obj)
    session.commit()
    print("User created successfully!")
    time.sleep(0.5)


def search_user(username):
    return session.query(models.User).filter_by(username=username).all()


def password_checking(username, password):
    while True:
        usr = search_user(username)[0]
        status = session.execute(
            select([models.User.username, models.User.password_hash])
        )
        for row in status:
            if row[0] == username:
                result = models.User.check_password_after_signup(password, row[1])
        if result == False:
            print("Passwords do not match.")
            password = getpass("Re-enter password: ")
        else:
            print("Login Successful!")
            time.sleep(0.5)
            break


def welcome_message(username):
    while True:
        print("\n")
        print(f"Welcome, {username}".center(40, "-"))
        status = session.execute(select([models.User.username, models.User.usertype]))
        for row in status:
            if row[0] == username and row[1] == True:
                print("1. Init seats")
                print("2. Show seats")
                print("3. Add movies")
                print("4. Show statistics")
                print("0. Logout")

                prompt = int(input("Enter choice: "))
                if prompt == 1:
                    init_seats()
                if prompt == 2:
                    show_seats()
                    time.sleep(1)
                    input("\nPress enter to continue")

                if prompt == 3:
                    add_movies()
                if prompt == 4:
                    statistics()
                if prompt == 0:
                    print("Program will exit now.")
                    sys.exit()
                else:
                    print("")

            elif row[0] == username and row[1] == False:
                print("1. Show seats")
                print("2. Buy a ticket")
                print("3. Show booked tickets user info")
                print("0. Logout")

                prompt = int(input("Enter option: "))
                if prompt == 1:
                    show_seats()
                if prompt == 2:
                    buy_ticket()
                if prompt == 3:
                    booked_ticket_info()
                if prompt == 0:
                    print("Program will exit now.")
                    sys.exit()
                else:
                    print("\nInvalid input.")
                    time.sleep(1)


def init_seats():
    global seat_rows, seat_columns, seats
    seat_rows = int(input("Enter the number of rows: "))
    seat_columns = int(input("Enter the number of columns: "))
    seats = np.full((seat_rows, seat_columns), "S")
    print("Seats Initialized successfully!")
    prompt = str(input("Show seats? (y/n): "))
    if prompt.lower() == "y":
        show_seats()
        time.sleep(1)
        input("Press enter to continue")
    elif prompt.lower() == "n":
        pass


def show_seats():
    print("\nCinema: ")
    headers = [x for x in range(1, seat_columns + 1)]
    table = tabulate(seats, headers, showindex=True, tablefmt="pretty")
    print(table)


def add_movies():
    pass


def statistics():
    pass


def buy_ticket():
    pass


def booked_ticket_info():
    pass


# x = session.query(models.User).first()
# result = session.execute(select([models.User.password_hash]))
# print(result)
# for row in result:
#     print(row)

# init_seats()
# welcome_message("ashishadmin")
# password_checking("ashishadmin", "testing123")

session.close()


# add_user("testuser2")
# usr = search_user("ashishadmin")
# print(session.execute(select([usr.password_hash])))
# print(usr[0].password_hash)
# print(password_checking("testing123", "ashish01"))
