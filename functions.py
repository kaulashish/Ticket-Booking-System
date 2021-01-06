import models, sys, time, math
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
                print("4. Remove movies")
                print("5. Show movies")
                print("6. Show statistics")
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
                    print("Movie added successfully!")
                if prompt == 4:
                    remove_movies()
                if prompt == 5:
                    show_movies()
                if prompt == 6:
                    statistics()
                if prompt == 0:
                    print("Program will exit now.")
                    sys.exit()

            elif row[0] == username and row[1] == False:
                print("1. Show seats")
                print("2. Show movies")
                print("3. Buy a ticket")
                print("4. Show booked tickets user info")
                print("0. Logout")

                prompt = int(input("Enter option: "))
                if prompt == 1:
                    show_seats()
                    time.sleep(1)
                    input("\nPress enter to continue")
                if prompt == 2:
                    show_movies()
                if prompt == 3:
                    buy_ticket()
                if prompt == 4:
                    booked_ticket_info()
                if prompt == 0:
                    print("Program will exit now.")
                    sys.exit()


def init_seats():
    if len(session.query(models.seats).all()) != 0:
        models.seats.__table__.drop(engine)
    seat_rows = int(input("Enter the number of rows: "))
    seat_columns = int(input("Enter the number of columns: "))
    seats = np.full((seat_rows, seat_columns), "S")
    # storing seat matrix into database
    for i in range(len(seats)):
        for j in range(len(seats[i])):
            max_seat_id = get_max_id(models.seats, models.seats.seatid)
            if max_seat_id == None:
                max_seat_id = 1
            else:
                max_seat_id = max_seat_id.seatid + 1
            seat, status = (i, j), seats[i][j]
            user_obj = models.seats(
                seatid=max_seat_id,
                seat_row=seat[0],
                seat_column=seat[1],
                status=status,
            )
            session.add(user_obj)

    print("Seats Initialized successfully!")
    prompt = str(input("Show seats? (y/n): "))
    while True:
        if prompt.lower() == "y":
            show_seats()
            time.sleep(1)
            input("Press enter to continue")
            break
        elif prompt.lower() == "n":
            break
        else:
            print("invalid entry")
            prompt = str(input("Show seats? (y/n): "))

    session.commit()


def show_seats():
    seat_rows = len(set(session.query(models.seats.seat_row)))
    seat_columns = len(set(session.query(models.seats.seat_column)))
    seats = np.full((seat_rows, seat_columns), "S")
    result = session.query(
        models.seats.seat_row, models.seats.seat_column, models.seats.status
    ).all()
    for item in result:
        seats[item[0]][item[1]] = item[2]
    print("\nCinema: ")
    headers = [x for x in range(0, seat_columns)]
    table = tabulate(seats, headers, showindex=True, tablefmt="pretty")
    print(table)


def add_movies():
    max_movie_id = get_max_id(models.movies, models.movies.movieid)
    if max_movie_id == None:
        max_movie_id = 1
    else:
        max_movie_id = max_movie_id.movieid + 1
    print("\n")
    print("Add movies".center(40, "-"))
    name = str(input("Enter movie name: "))
    director = str(input("Enter director name: "))
    user_obj = models.movies(movieid=max_movie_id, name=name, director=director)

    session.add(user_obj)
    session.commit()


def remove_movies():
    print("\n")
    print("Remove movies".center(40, "-"))
    result = session.query(models.movies).all()
    for index, movie in enumerate(result):
        print(f"{index + 1}. {movie}")
    choice = int(input("Enter choice: "))
    session.query(models.movies).filter_by(movieid=choice).delete()
    session.commit()
    print("Movie deleted successfully!")


def show_movies():
    print("\n")
    print("Movies".center(40, "*"))
    result = session.query(models.movies.name, models.movies.director).all()
    table = tabulate(result, ("Movie", "Director"), showindex=True, tablefmt="pretty")
    print(table)
    input("Press Enter to continue.")


def statistics():
    pass


def buy_ticket():
    pass


def booked_ticket_info():
    pass


# add_movies()
remove_movies()
session.close()
