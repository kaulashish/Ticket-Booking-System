import models
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from getpass import getpass

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
        if models.User.check_password(re_password) == False:
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


def search_user(username):
    return session.query(models.User).filter_by(username=username).all()


def password_checking(password, username):
    usr = search_user(username)[0]
    print(usr)
    while True:
        if usr.check_password(password) == False:
            print("Passwords do not match.")
        else:
            break


session.close()


# add_user("ashishadmin")
# usr = search_user("ashishadmin")
# print(usr[0].password_hash)
print(password_checking("testing123", "ashish01"))
