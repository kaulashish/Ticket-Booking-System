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
            password_hash=password_hash,
        )
    elif admin_status == "y":
        user_obj = models.User(
            userid=max_user_id,
            username=username,
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
                    buy_ticket(username)
                if prompt == 4:
                    booked_ticket_info(username)
                if prompt == 0:
                    print("Program will exit now.")
                    sys.exit()


def init_seats():
    models.customer.__table__.drop(engine)
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
    print("Movies".center(40, "-"))
    result = session.query(models.movies).all()
    for index, movie in enumerate(result):
        print(f"{index + 1}. {movie}")
    input("Press Enter to continue.")


def seat_price(seat_row, seat_column):
    while True:
        rows = session.query(models.seats.seat_row).all()
        columns = session.query(models.seats.seat_column).all()
        totalrows = sorted([x[0] for x in set(rows)])
        totalcolumns = sorted([x[0] for x in set(columns)])
        total_seats = get_max_id(models.seats, models.seats.seatid).seatid
        firsthalf_rows = [x for x in range(len(totalrows) // 2)]
        secondhalf_rows = [x for x in range(len(firsthalf_rows), len(totalrows))]
        if seat_row in totalrows and seat_column in totalcolumns:
            if total_seats <= 60:
                return 10
                break

            else:
                if seat_row in firsthalf_rows:
                    return 10
                    break
                elif seat_row in secondhalf_rows:
                    return 8
                    break
        else:
            print(
                "Seat given is invalid. Please provide a valid row and column number."
            )
            seat = (
                input("Select seat index separated by comma(row, column): ")
                .strip()
                .split(",")
            )
            seat_price(seat[0], seat[1])


def buy_ticket(username):
    print("\n")
    print("Buy Ticket".center(40, "-"))
    result = session.query(models.movies).all()
    print("Movies airing ->\n")
    # ? multiple screens to be implemented later
    for index, movie in enumerate(result):
        print(f"{index + 1}. {movie}")
    choice = int(input("Enter choice: "))
    if choice > len(session.query(models.movies).all()):
        print("Invalid entry")
    else:
        show_seats()
        seat_val = list(
            map(
                int,
                input("Select seat index separated by comma(row, column): ")
                .strip()
                .split(","),
            )
        )
        price = seat_price(seat_val[0], seat_val[1])
        seats = session.query(models.seats).filter_by(seat_column=seat_val[1]).all()
        for seat in seats:
            if seat.seat_row == seat_val[0] and seat.status == "B":
                print("Seat already booked, please select another seat.")
            elif seat.seat_row == seat_val[0]:
                prompt = str(input(f"Seat price is {price}$, confirm? (y/n): "))
                if prompt.lower() == "y":
                    max_customer_id = get_max_id(
                        models.customer, models.customer.userid
                    )
                    if max_customer_id == None:
                        max_customer_id = 0
                    else:
                        max_customer_id = max_customer_id.userid + 1
                    name = str(input("Full name: "))
                    gender = str(input("Gender(M/F/O): "))
                    age = int(input("Age: "))
                    phone = int(input("Phone: "))
                    # setting customer's total tickets bought, and money spent ->
                    total_tickets_bought = (
                        session.query(models.customer)
                        .filter_by(userid=max_customer_id)
                        .all()
                    )
                    if len(total_tickets_bought) == 0:
                        total_tickets_bought = 1
                    else:
                        total_tickets_bought = total_tickets_bought + 1
                    money_spent = (
                        session.query(models.customer)
                        .filter_by(userid=max_customer_id)
                        .all()
                    )
                    if len(money_spent) == 0:
                        money_spent = price
                    else:
                        money_spent = money_spent + price
                    # updating seat status:
                    seat.status = "B"
                    user_obj = models.customer(
                        userid=max_customer_id,
                        username=username,
                        name=name,
                        gender=gender.upper(),
                        age=age,
                        phone=phone,
                        tickets_bought=total_tickets_bought,
                        totalspent=money_spent,
                    )
                    session.add(user_obj)
                    session.commit()
                    print(f"Ticket bought for seat({seat_val[0]},{seat_val[1]})!")
                elif prompt.lower() == "n":
                    print("Seat selection cancelled.")


def booked_ticket_info(username):
    print("\n")
    print("User info".center(40, "-"))
    obj = session.query(models.customer).filter_by(username=username)
    count = 0
    moneyspent = 0
    totaltickets = 0
    for i in obj:
        if str(i.username) == username:
            count += 1
            name = i.name
            gender = i.gender
            age = i.age
            phone = i.phone
            moneyspent += i.totalspent
            totaltickets += i.tickets_bought
            print(f"Name: {name}")
            print(f"Gender: {gender}")
            print(f"Age: {age}")
            print("o".center(40, "-"))
    print(f"Tickets price: {moneyspent}")
    print(f"Total tickets bought: {totaltickets}")
    print("\n")
    input("Press Enter to continue...")


def statistics():
    print("\n")
    print("Statistics".center(40, "-"))

    # for percentage, total booked seats and current income
    booked_seats_obj = session.query(models.seats).filter_by(status="B")
    total_seats = get_max_id(models.seats, models.seats.seatid).seatid
    booked_seats = 0
    current_income = 0
    for seat in booked_seats_obj:
        booked_seats += 1
        current_income += seat_price(seat.seat_row, seat.seat_column)
    percentage = round((booked_seats / total_seats) * 100, 2)

    # for total price
    seat_row_obj = session.query(models.seats.seat_row)
    seat_column_obj = session.query(models.seats.seat_column)
    total_price = 0
    seat_row = []
    seat_column = []
    for i in seat_row_obj:
        seat_row.append(i[0])
    for j in seat_column_obj:
        seat_column.append(j[0])
    seats = list(map(lambda x, y: (x, y), seat_row, seat_column))
    total_price = 0
    for k in seats:
        total_price += seat_price(k[0], k[1])

    print(f"Number of purchased tickets: {booked_seats}")
    print(f"Percentage: {percentage}%")
    print(f"Current Income: {current_income}$")
    print(f"Total Income: {total_price}$")
    print("\n")
    input("Press enter to continue...")


session.close()
