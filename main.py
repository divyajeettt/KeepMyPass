import matplotlib.pyplot as plt
import mysql.connector as con
import pickle
import os
import re

from tkinter.messagebox import *
from typing import Callable
from tkinter import *
from random import *
from string import *

from datetime import datetime as dt
from PIL import ImageTk, Image
from tkinter import ttk
from time import sleep


def connect() -> None:
    """establishes connection between Python & MySQL software"""
    global mydb, cursor

    try:
        mydb = con.connect(host="localhost", user="root", password="root")
        cursor = mydb.cursor()

    except con.InterfaceError:
        return no_window_message(showerror, "CANONOT CONTINUE PROGRAM", "UNABLE TO ESTABLISH CONNECTION WITH MySQL")

    else:
        try:
            cursor.execute("create database if not exists project")
        except:
            return no_window_message(showerror, "ERROR", "DATABASE CREATION UNSUCCESSFUL")
        else:
            cursor.execute("use project")
        finally:
            mydb.commit()

    if mydb.is_connected():
        # if connection is successful, create the Tables and start __main__ application
        create()
        loading()
    else:
        no_window_message(showerror, "ERROR", "SORRY! WE WERE UNABLE TO START THE APPLICATION")


def close() -> None:
    """closes the connection between Python & MySQL software"""

    try:
        cursor.close()
        mydb.close()
    except con.InternalError:
        no_window_message(showwarning, "WARNING", "UNABLE TO CLOSE CONNECTION TO MySQL")
    finally:
        no_window_message(showinfo, "THANK YOU", "Thank You for using KeepMyPass")


def create() -> None:
    """creates the required Tables ('passwords', 'contacts' and 'events') in the database"""

    nu, pk = "not null", "primary key"
    table, user = "create table if not exists", f"\nuser varchar(50) {nu}"

    passwords: str = f"""
        {table} passwords ({user}, username varchar(50), password varchar(256) {nu}, app_url varchar(100), notes text,
        {pk} (user, username)
    )"""

    contacts: str = f"""
        {table} contacts ({user}, fullname varchar(50) {nu}, contact_no varchar(15),
        alternate_no varchar(15), birthday date, city varchar(25) default "NEW DELHI",
        {pk} (user, contact_no)
    )"""

    events: str = f"""
        {table} events ({user}, evttitle varchar(30), evtdate date {nu},
        evttime time default "00:00:00", completed varchar(3) default "NO",
        {pk} (user, evttitle)
    )"""

    for query in passwords, contacts, events:
        try:
            cursor.execute(query)
        except:
            pass
        else:
            mydb.commit()


def pass_keys() -> None:
    """creates simple encryption and deceyption keys and sets them as global variables"""
    global ekey1, dkey1, ekey2, dkey2

    chrs1: list[str] = list(printable)[:-5]
    chrs2: list[str] = chrs1.copy()

    shuffle(chrs2)

    numbers: list[str] = []
    while len(numbers) != len(chrs1):
        num = str(int.from_bytes(os.urandom(2), "little"))
        if len(num) == 3 and num not in numbers:
            numbers.append(num)

    ekey1, dkey1 = dict(zip(chrs1, numbers)), dict(zip(numbers, chrs1))
    ekey2, dkey2 = dict(zip(numbers, chrs2)), dict(zip(chrs2, numbers))


def valid_username(uname: str) -> None:
    """displays an error if an entered username is invalid"""

    if not uname or uname.isspace():
        return showwarning("Required Field", "Username / Mail Address cannot be Empty", parent=UserVault)

    if "@" in uname:
        if uname.count("@") != 1 or "_" in uname or uname[0] == "@":
            return showerror("Error", "Invalid Mail - ID", parent=UserVault)

        match = re.search(r"[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*", uname)
        if match is None or match.span()[0] != 0:
            return showerror("Error", "Invalid Mail - ID", parent=UserVault)

    if len(uname) not in range(5, 51):
        return showerror("Error", "Username / Mail Address must be between 5 - 50 characters", parent=UserVault)

    if uname[0] not in (ascii_letters + "_"):
        return showerror("Error", "First letter of Username must be an underscore or alphabet", parent=UserVault)

    for char in uname:
        if char not in (ascii_letters + "_" + "." + digits):
            return showerror("Error", "Invalid character found in Username", parent=UserVault)


def valid_password(password: str) -> None:
    """displays an error if an entered password is invalid"""

    if not password or password.isspace():
        return showwarning("Required Field", "Password cannot be Empty", parent=UserVault)

    if len(password) not in range(8, 129):
        return showerror("Error", "Password must be between 8 - 128 characters", parent=UserVault)

    for char in password:
        if char not in printable[:-5]:
            return showerror("Error", "Invalid character found in Password", parent=UserVault)


def valid_contact(contact: str) -> None:
    """displays an error if an entered contact number is invalid"""

    if not contact.isdecimal() and not contact.startswith("+"):
        return showerror("Error", "Invalid character found in Contact Number", parent=UserVault)

    if len(contact) not in range(3, 16):
        return showerror("Error", "Contact Number must be between 3 - 15 digits", parent=UserVault)


def encrypt(string: str) -> str:
    """encrypts the given string and returns it"""

    string, copy = string[::-1].swapcase(), ""
    for char in string:
        copy += ekey1[char] + " "

    enc = [ekey2[num] for num in copy.split()]
    encrypted = ""
    for char in enc:
        encrypted += char + choice(punctuation)

    return encrypted


def decrypt(string: str) -> str:
    """decrypts the given string and returns it"""

    dec = [dkey2[char] for char in string[::2]]
    string, copy = "".join(dec), ""

    for i in range(0, len(string), 3):
        copy += dkey1[string[i:i+3]]

    decrypted = copy.swapcase()[::-1]
    return decrypted


def generate(length: int, specs: tuple[bool, 4]) -> str:
    """returns a random password generated with the given specifications
    :param:
    specs: tuple[bool, bool, bool, bool]: the entries in the tuple represent
    Uppercase, Lowercase, Digits, Special characters respectively"""

    if not any(specs):
        return showwarning("Required - Character Type", "Select atleast one type of character", parent=UserVault)

    char_type = {0: ascii_uppercase, 1: ascii_lowercase, 2: 3*digits, 3: punctuation}

    available = password = ""
    for i in range(4):
        available += char_type[i] if specs[i] else ""

    chars = list(available) * 20
    shuffle(chars)

    for _ in range(length):
        try:
            index = int.from_bytes(os.urandom(2), "big") // randint(10, 20)
            password += chars[index]
        except IndexError:
            password += choice(chars)

    for _ in range(randrange(1, 4)):
        sample1 = sample(chars, randint(25, len(available)))
        sample2 = sample(chars, len(sample1))
        table = str.maketrans(dict(zip(sample1, sample2)))
        password = password.translate(table)

    return password


def no_window_message(
    messagebox: Callable[[str, str, Tk], None],
    title: str, message: str
) -> None:
    """displays messageboxes without any parent window, if required"""

    temp_window = Tk()
    temp_window.withdraw()
    messagebox(title=title, message=message, parent=temp_window)
    temp_window.destroy()


def global_vars() -> None:
    """defines various variables required globally"""
    global root, style, color, IMAGES, ICONS, CURSORS, FILES, USER_COUNT, CREDENTIALS

    root: Tk = Tk()                 # initializes the main-window
    root.resizable(False, False)    # prevents resizing of the window
    USER_COUNT: int = 0             # count number of Users already present
    color: str = "#dff3ef"          # background color for Entry boxes and Text boxes
    style = ttk.Style()             # configure the stylizing of tabular data

    # initialize tuples containing all required icons and image objects through their location
    ICONS: tuple[str] = tuple(icon for icon in os.listdir(os.path.join(os.getcwd(), "Icons")))

    IMAGES: tuple[ImageTk] = tuple(
        ImageTk.PhotoImage(Image.open(image))
        for image in os.listdir(os.path.join(os.getcwd(), "Images"))
    )

    # initialize a tuple containing all required CURSORS types
    CURSORS: tuple[str] = ("hand2", "starting", "wait", "arrow", "question_arrow", "no", "xterm", "plus")

    # initialize binary filenames in a tuple
    FILES: tuple[str] = ("passwords.dat", "pkeys.dat")

    # initialize the Admin and the password to Admin Mode
    CREDENTIALS: tuple[str] = ("Divyajeet Singh", "Python KeepMyPass GUI Project")

    if not os.path.isfile(FILES[0]):
        return

    with open(file=FILES[0], mode="rb") as file:
        while True:
            try:
                record = pickle.load(file)
            except EOFError:
                break
            else:
                USER_COUNT += 1
    USER_COUNT //= 16


def empty_screen(screen: Tk, dont_destroy: Tk|None = None) -> None:
    """empties all widgets from the mentioned 'screen'"""

    for name, widget in tuple(screen.children.items()):
        if "toplevel" not in name and widget != dont_destroy:
            widget.destroy()
    try:
        window.destroy()
    except NameError:
        pass
    plt.close("all")


def back_button(screen: Tk, window: Callable[[], None]) -> None:
    """places a back-button on 'screen' which takes the control back to 'window'"""

    Button(screen, image=IMAGES[0], bd=3, command=window, cursor=CURSORS[0]).place(x=0, y=0)


def hideshow(
    button: Button, entrybox: Entry, show_img: ImageTk, hide_img: ImageTk
) -> None:
    """hides and shows the Passwords according to the User's choice"""

    if str(button.cget("image")) == str(hide_img):
        img, char = show_img, "\N{BULLET}"
    else:
        img, char = hide_img, ""

    button.config(image=img)
    entrybox.config(show=char)


def exit_app(parent: Tk) -> None:
    """displays the main exit-prompt on 'parent' window"""

    if askyesno("EXIT?", "Do you want to quit KeepMyPass?", parent=parent):
        plt.close("all")
        root.destroy()
        close()


def loading() -> None:
    """displays the loading screen and starts the application"""

    global_vars()
    root.geometry("548x210")
    root.title("Loading\N{HORIZONTAL ELLIPSIS}")
    root.iconbitmap(ICONS[0])

    screen = Label(cursor=CURSORS[1])
    screen.place(x=0, y=0)
    for _ in range(randint(5, 7)):
        for image in IMAGES[1:4]:
            screen.config(image=image)
            root.update()
            sleep(uniform(0.115, 0.225))

    screen.destroy()
    root.geometry("450x22")

    bar = ttk.Progressbar(mode="determinate", length=450, orient=HORIZONTAL, cursor=CURSORS[2])
    bar.place(x=0, y=0)
    while bar["value"] < 100:
        bar["value"] += uniform(0.01, 0.35)
        root.update()
        sleep(random() ** randrange(500, 1001, 50))

    root.config(cursor=CURSORS[3])
    bar.destroy()
    no_window_message(showinfo, "Successful!", "Welcome to the Application")

    intro_window()


def intro_window() -> None:
    """starts the intro-window for the application"""

    root.geometry("544x544")
    root.title("KeepMyPass - Password Manager")
    root.iconbitmap(ICONS[1])
    welcome = list(IMAGES[4:7])

    def next_window():
        """opens the next image in the intro-window"""

        try:
            del welcome[0]
            Button(image=welcome[0], command=next_window, cursor=CURSORS[0]).place(x=0, y=0)
        except IndexError:
            # when intro finishes, the main app is started
            main_window()

    Button(image=welcome[0], command=next_window, cursor=CURSORS[0]).place(x=0, y=0)
    root.mainloop()


def main_window() -> None:
    """starts the main-window/homepage for the application"""

    empty_screen(root)
    root.geometry("772x544")
    root.title("KeepMyPass")
    root.iconbitmap(ICONS[2])

    def info() -> None:
        """shows help on how the application is used"""

        messages = [
            "To use the Application, you must first Sign Up.",
            "Multiple Users can be created, but each will have access to one's own data only.",
            "You only need to remember one Password - your MasterPassword.",
            "Once Signed Up, you can Log in to your Secure Vault and store: {0} Passwords {0} Contacts {0} Events",
            "If you ever forget your MasterPassword, we may be able to help you to retrieve your lost account.",
            "A Password-Protected Admin Mode allows the developer to search for any data!"
        ]
        showinfo("User Guide & Manual", "\n".join(messages).format("\n\t\N{BULLET}"))

    Label(image=IMAGES[7]).place(x=0, y=0)
    Button(image=IMAGES[8], bd=3, command=info, cursor=CURSORS[4]).place(x=699.375, y=0)

    coms = [login_window, signup_window, admin_mode, (lambda: exit_app(root))]
    for i in range(4):
        st, cur = (DISABLED, CURSORS[5]) if not (i or USER_COUNT) else (NORMAL, CURSORS[0])
        Button(image=IMAGES[i+9], bd=0, command=coms[i], state=st, cursor=cur).place(x=480, y=75*i + 146.25)

    root.protocol("WM_DELETE_WINDOW", (lambda: exit_app(root)))


def signup_window() -> None:
    """starts the signup-window for the User"""

    empty_screen(root)
    root.title("Sign Up for KeepMyPass")
    root.iconbitmap(ICONS[3])
    Label(image=IMAGES[13]).place(x=0, y=0)

    user = Entry(width=27, font=("ariel", 19, "bold"), bd=2, relief=FLAT, cursor=CURSORS[6], bg=color)
    user.insert(0, "Enter your FullName")
    user.bind("<Return>", (lambda event: create_user(user)))
    user.place(x=9, y=177.5)

    st, cur = (NORMAL, CURSORS[4]) if USER_COUNT else (DISABLED, CURSORS[5])
    Button(image=IMAGES[14], bd=0, command=(lambda: create_user(user)), cursor=CURSORS[0]).place(x=22.5, y=236)
    Button(image=IMAGES[15], bd=0, command=login_window, state=st, cursor=cur).place(x=52.5, y=311)

    back_button(root, main_window)


def create_user(user: Entry) -> None:
    """checks the name input by the User and inputs the MasterPassword"""

    name = user.get().strip().title()

    if name.casefold() in {"enter your fullname", ""}:
        return showwarning("Required Field", "Name cannot be Empty")

    if check_name(name):
        showwarning("Matching User Found", "User Already Exists!")

        if askyesno("Log In", "Log in instead?"):
            return login_window()
        if askyesno("Help", "Forgot Password? Need Help?"):
            return forgot_pass()

        return user.delete(0, END)

    if len(name) not in range(5, 51):
        showerror("Error", "Name must be between 5 - 50 characters")
        return user.delete(0, END)

    for char in name:
        if char not in (ascii_letters + " " + "."):
            showerror("Invalid character found", "Name can only contain Letters")
            return user.delete(0, END)

    empty_screen(root)
    Label(image=IMAGES[16]).place(x=0, y=0)
    specs = dict(width=22, bd=2, font=("ariel", 19, "bold"), relief=FLAT, cursor=CURSORS[6], bg=color)

    mp1, mp2, show, hide = Entry(**specs), Entry(**specs), *IMAGES[17:19]
    mp1.place(x=18, y=206)
    mp2.place(x=18, y=257.5)
    mp1.insert(0, "Choose a MasterPass")
    mp2.insert(1, "Confirm MasterPass")

    hs1 = Button(image=hide, bd=2, command=(lambda: hideshow(hs1, mp1, show, hide)), cursor=CURSORS[0])
    hs2 = Button(image=hide, bd=2, command=(lambda: hideshow(hs2, mp2, show, hide)), cursor=CURSORS[0])
    hs1.place(x=333.75, y=200)
    hs2.place(x=333.75, y=252)

    values = (name, mp1, mp2, write_file, end_window)
    mp2.bind("<Return>", (lambda event: set_mpass(*values)))
    Button(image=IMAGES[19], bd=0, command=(lambda: set_mpass(*values)), cursor=CURSORS[0]).place(x=35.5, y=322.5)

    back_button(root, signup_window)


def check_name(name_user: str) -> bool:
    """returns True if User already exists, False otherwise"""
    global ekey1, dkey1, ekey2, dkey2

    if not USER_COUNT:
        return False

    with open(FILES[0], "rb") as file1, open(FILES[1], "rb") as file2:
        exists = False

        for i in range(1, 16*USER_COUNT + 1):
            pwd_dict = pickle.load(file1)
            if not (i % 16):
                ekey1, dkey1, ekey2, dkey2 = pickle.load(file2)
                name = tuple(pwd_dict.keys())[0]
                if name_user == decrypt(name):
                    exists = True
                    break

    return exists


def set_mpass(
    name_user: str, mpass1: Entry, mpass2: Entry,
    file_func: Callable[[str, str], None], next_window:: Callable[[], None]
) -> None:
    """checks the validity of the MasterPassword"""

    m1, m2, delete = mpass1.get(), mpass2.get(), False

    if any([not m1, not m2, m1.isspace(), m2.isspace()]):
        delete, title, message, box = True, "Required Field", "MasterPassword cannot be Empty", showwarning

    elif m1 != m2:
        delete, title, message, box = True, "Error", "The MasterPassword you re-entered does not match", showerror

    elif len(m1) not in range(8, 129):
        delete, title, message, box = True, "Error", "MasterPassword must be between 8 - 128 characters", showerror

    if delete:
        mpass1.delete(0, END)
        mpass2.delete(0, END)
        return box(title, message)

    if m1.isalpha() or m2.isdecimal():
        message = "A MasterPassword containing only {} is weak. Still continue?"
        if not askyesno("Weak Password", message.format("Letters" if m1.isalpha() else "Digits")):
            return

    file_func(name_user, m2)
    next_window(name_user)


def write_file(name: str, masterpwd: str) -> None:
    """writes fake details & User's details and keys in the Binary Files"""

    with open(FILES[0], "ab") as file1, open(FILES[1], "ab") as file2:
        chars, truth = printable[:-5]*20, [True, False]
        pass_keys()

        for i in range(15):
            new_name: str = "".join(sample(chars, randint(5, 50 )))
            new_pass: str = "".join(sample(chars, randint(8, 128)))

            if choice(truth):
                pwds = [new_pass]
            elif choice(truth):
                pwd1 = "".join(sample(chars, randint(8, 128)))
                pwds = [new_pass, pwd1]
            else:
                pwd1 = "".join(sample(chars, randint(8, 128)))
                pwd2 = "".join(sample(chars, randint(8, 128)))
                pwds = [new_pass, pwd1, pwd2]

            pickle.dump({new_name: pwds}, file1)

        pickle.dump({encrypt(name): [encrypt(masterpwd)]}, file1)
        pickle.dump((ekey1, dkey1, ekey2, dkey2), file2)


def end_window(name: str) -> None:
    """finishes the MasterPassword creation and increments the number of Users"""
    global USER_COUNT

    empty_screen(root)
    root.title("Successful!")
    root.iconbitmap(ICONS[4])
    Label(image=IMAGES[20]).place(x=0, y=0)
    Button(image=IMAGES[21], bd=0, command=(lambda: create_vault(name)), cursor=CURSORS[0]).place(x=412.5, y=247.5)
    Button(image=IMAGES[22], bd=0, command=main_window, cursor=CURSORS[0]).place(x=412.5, y=322.5)

    USER_COUNT += 1


def login_window() -> None:
    """starts the log-in window for the User"""

    empty_screen(root)
    root.title("Log In to KeepMyPass")
    root.iconbitmap(ICONS[5])

    Label(image=IMAGES[23]).place(x=0, y=0)
    specs = dict(width=22, bd=2, font=("ariel", 19, "bold"), relief=FLAT, cursor=CURSORS[6], bg=color)

    urname, passwd, show, hide = Entry(**specs), Entry(**specs), *IMAGES[17:19]
    urname.place(x=393.75, y=210)
    passwd.place(x=393.75, y=262.5)
    urname.insert(0, "Enter Name of User")
    passwd.insert(1, "Enter MasterPassword")
    passwd.bind("<Return>", (lambda event: check_login(urname, passwd)))

    hs = Button(image=hide, bd=2, command=(lambda: hideshow(hs, passwd, show, hide)), cursor=CURSORS[0])
    hs.place(x=709.5, y=256.5)
    Button(image=IMAGES[24], bd=0, command=forgot_pass, cursor=CURSORS[4]).place(x=422.55, y=311.25)
    Button(image=IMAGES[21], bd=0, command=(lambda: check_login(urname, passwd)), cursor=CURSORS[0]).place(x=390, y=367.5)

    back_button(root, main_window)


def check_login(name: Entry, pwd: Entry) -> None:
    """checks the name of User & MasterPassword associated with it"""
    global ekey1, dkey1, ekey2, dkey2

    name_user, passwd = name.get().strip().title(), pwd.get()

    if not (name_user and len(name_user) in range(5, 51)):
        return showwarning("Required Field", "Please enter FullName of User")

    if not check_name(name_user):
        name.delete(0, END)
        pwd.delete(0, END)
        return showerror("Invalid User", "User does not Exist")

    with open(FILES[0], "rb") as file1, open(FILES[1], "rb") as file2:
        matched = False

        for i in range(1, 16*USER_COUNT + 1):
            pwd_dict = pickle.load(file1)
            if i % 16:
                continue

            ekey1, dkey1, ekey2, dkey2 = pickle.load(file2)
            kname, pwds = tuple(pwd_dict.items())[0]
            if name_user == decrypt(kname):
                if passwd == decrypt(pwds[-1]):
                    showinfo("Successful", "Logged in Successfully!")
                    matched = True
                break

    if matched:
        return create_vault(name_user)

    pwd.delete(0, END)
    showerror("Invalid Password", "Name of User & MasterPassword do not match")


def forgot_pass() -> None:
    """helps in retrieving lost Account of a User"""

    empty_screen(root)
    root.title("Retrieve Lost Account")
    root.iconbitmap(ICONS[6])

    def info() -> None:
        """shows how the lost User Account is retrieved"""

        messages = [
            "To retrieve your lost account, your must enter any old MasterPassword that you may remember.",
            "It doesn't have to be the entire password, instead all you need is any 8 matching characters.",
            "Unfortunately, we can't guarantee to retrieve your account.",
            "Remember, this is not a case-sensitive checking.",
            "As a tip, you should choose the MasterPassword to be one you don't use elsewhere."
        ]
        showinfo("Forgot Password Help", " ".join(messages))

    Label(image=IMAGES[25]).place(x=0, y=0)
    specs = dict(width=22, bd=2, font=("ariel", 19, "bold"), relief=FLAT, cursor=CURSORS[6], bg=color)

    name_user, lastpass = Entry(**specs), Entry(**specs)
    name_user.place(x=416.25, y=240)
    lastpass.place(x=416.25, y=292.5)
    name_user.insert(0, "FullName of User")
    lastpass.insert(1, "Last Password")
    lastpass.bind("<Return>", (lambda event: retrieve_account(name_user, lastpass)))

    Button(image=IMAGES[8], bd=3, command=info, cursor=CURSORS[4]).place(x=699.375, y=0)
    Button(image=IMAGES[26], bd=0, command=(lambda: retrieve_account(name_user, lastpass)), cursor=CURSORS[0]).place(x=390, y=360)

    back_button(root, login_window)


def retrieve_account(uname: Entry, lastpass: Entry) -> None:
    """retrieves the lost account of a User and prompts to change the MasterPassword"""
    global ekey1, dkey1, ekey2, dkey2

    name, passwd = uname.get().strip().title(), lastpass.get().casefold()

    if not check_name(name):
        if not name:
            return showwarning("Required Field", "Please enter FullName of User")

        showerror("Invalid User", "User does not Exist")
        return uname.delete(0, END)

    if not passwd or passwd.isspace():
        return showwarning("Required Field", "Please enter the last password you remember")

    if len(passwd) not in range(8, 129):
        showwarning("Invalid Password", "Please enter 8 - 128 matching charaters of your old MasterPassword")
        return lastpass.delete(0, END)

    with open(FILES[0], "rb") as file1, open(FILES[1], "rb") as file2:
        retrieved = False

        for i in range(1, 16*USER_COUNT + 1):
            pwd_dict = pickle.load(file1)
            if i % 16:
                continue

            ekey1, dkey1, ekey2, dkey2 = pickle.load(file2)
            kname, pwds = tuple(pwd_dict.items())[0]
            if name != decrypt(kname):
                continue

            for pwd in pwds:
                if passwd in decrypt(pwd).casefold():
                    showinfo("Successful", "Account Retrieval Successful!")
                    retrieved = True
                    break

    if retrieved:
        return change_masterpass(name)

    showwarning("We're sorry!", "Cannot gain access to your account. Try again!")
    lastpass.delete(0, END)


def change_masterpass(name_user: str) -> None:
    """changes the MasterPassword of the User"""

    empty_screen(root)
    root.title("Change your MasterPassword")
    root.iconbitmap(ICONS[7])

    Label(image=IMAGES[27]).place(x=0, y=0)
    specs = dict(width=22, bd=2, font=("ariel", 19, "bold"), relief=FLAT, cursor=CURSORS[6], bg=color)

    mp1, mp2, show, hide = Entry(**specs), Entry(**specs), *IMAGES[17:19]
    mp1.place(x=39, y=220.5)
    mp2.place(x=39, y=273)
    mp1.insert(0, "Choose a MasterPass")
    mp2.insert(1, "Confirm MasterPass")

    hs1 = Button(image=hide, bd=2, command=(lambda: hideshow(hs1, mp1, show, hide)), cursor=CURSORS[0])
    hs2 = Button(image=hide, bd=2, command=(lambda: hideshow(hs2, mp2, show, hide)), cursor=CURSORS[0])
    hs1.place(x=354.75, y=214.5)
    hs2.place(x=354.75, y=267)

    values = (name_user, mp1, mp2, update_file, create_vault)
    mp2.bind("<Return>", (lambda event: set_mpass(*values)))
    Button(image=IMAGES[19], bd=0, command=(lambda: set_mpass(*values)), cursor=CURSORS[0]).place(x=58.125, y=337.5)


def update_file(uname: str, newpass: str) -> None:
    """updates the Binary Files pertaining to User's MasterPasswords"""
    global ekey1, dkey1, ekey2, dkey2

    with open(FILES[0], "rb") as file1, open(FILES[1], "rb") as file2, open("temp.dat", "wb") as file3:
        for i in range(1, 16*USER_COUNT + 1):
            pwd_dict = pickle.load(file1)

            if not (i % 16):
                ekey1, dkey1, ekey2, dkey2 = pickle.load(file2)
                kname = tuple(pwd_dict.keys())[0]
                if uname == decrypt(kname):
                    pwd_dict[kname].append(encrypt(newpass))

            pickle.dump(pwd_dict, file3)

    os.remove(FILES[0])
    os.rename("temp.dat", FILES[0])
    showinfo("Successful", "Your MasterPassword has been Updated successfully")


def delete_file(user: str) -> None:
    """deletes the User account from Binary Files"""
    global ekey1, dkey1, ekey2, dkey2

    with open(FILES[0], "rb") as file1, open(FILES[1], "rb") as file2, \
         open("temp_pass.dat", "wb") as file3, open("temp_keys.dat", "wb") as file4:

        del_recs = range(0)

        for i in range(1, 16*USER_COUNT + 1):
            pwd_dict = pickle.load(file1)

            if not (i % 16):
                ekey1, dkey1, ekey2, dkey2 = pickle.load(file2)
                kname = tuple(pwd_dict.keys())[0]
                if user == decrypt(kname):
                    del_recs = range(i, i+16)
                else:
                    pickle.dump((ekey1, dkey1, ekey2, dkey2), file4)

            if i not in del_recs:
                pickle.dump(pwd_dict, file3)

    for temp, name in ("temp_pass.dat", FILES[0]), ("temp_keys.dat", FILES[1]):
        os.remove(name)
        os.rename(temp, name)


def delete_user(name_user: str) -> None:
    """deletes the User data from the database and decrements the number of Users"""
    global USER_COUNT

    try:
        for table in "passwords", "contacts", "events":
            cursor.execute(f"delete from {table} where user = {name_user !r}")
    except:
        return showerror("Error", "Sorry, some error occured. We were unable to remove your account")
    else:
        mydb.commit()
        msg = "All data has been removed from your Vault. "

        if askyesno("Vault Emptied", f"{msg}Do you still wish to delete your account?"):
            delete_file(name_user)
            USER_COUNT -= 1
            return showinfo("Successful", "User Account deleted successfully.")

        showinfo("Successful", "Your Vault has been emptied sucessfully.")


def create_vault(user: str) -> None:
    """starts the vault-window for a specific User"""
    global UserVault

    try:
        UserVault.destroy()
    except NameError:
        pass
    finally:
        UserVault: Tk = Toplevel(root)
        UserVault.resizable(False, False)
        vault_window(user)
        main_window()


def vault_window(name: str) -> None:
    """places the widgets on the vault-window"""

    UserVault.geometry("772x544")
    UserVault.title(f"""{f"{name}'" if name.endswith("s") else f"{name}'s"} Secure Vault""")
    UserVault.iconbitmap(ICONS[8])
    Label(UserVault, image=IMAGES[28]).place(x=0, y=0)

    def view_all(b: str|None = "\n\t\N{BULLET} ") -> None:
        """displays what type of information can be viewed from the Application"""

        messages = [
            "You can view all the personal information in your Vault in an orderly fashion:",
            "{0}Tabular Format {0}Graphical Format \n",
            "Available Tables: {0}Passwords {0}Contacts {0}Events \n",
            "Available Graphs: {4}{0} {4}{1} {4}{2} {4}{3} \n".format(*graph_names, b),
            "You can edit (Update/Delete) your saved data by double-clicking or right-clicking it."
        ]
        showinfo("View Data", " ".join(messages).format(b), parent=UserVault)

    def view_data(tablename: str) -> None:
        """fetches all data of the User in the given Table ('passwords', 'contacts', or 'events')"""

        display_records(
            parent=UserVault, tablename=tablename,
            title=f"""{f"{name}'" if name.endswith("s") else f"{name}'s"} {tablename.capitalize()}""",
            query=f"select * from {tablename} where user = {name !r}",
            no_records=("Empty Vault", f"There are no {tablename.capitalize()} in your Vault!"),
        )

    def graph(variable: str) -> None:
        """selects and shows the Graph chosen by the User"""

        def graph1() -> None:
            """displays VERTICAL BAR GRAPH: number of passwords per app/url"""

            x_axis, y_axis = [row[0] if row[0] else "Unspecified" for row in data], [row[1] for row in data]
            plt.bar(x_axis, y_axis, color="b", width=0.35)

        def graph2() -> None:
            """displays HORIZONTAL BAR GRAPH: number of contacts per city"""

            x_axis, y_axis = [row[0] for row in data], [row[1] for row in data]
            plt.barh(x_axis, y_axis, color="b", height=0.35)

        def graph3() -> None:
            """displays PIE CHART: number of events per their status of completion"""

            labels, slices, colors = ["INCOMPLETE", "COMPLETED"], [row[1] for row in data], ["#d11718", "#25c5d4"]
            plt.pie(slices, labels=labels, colors=colors, autopct="%1.1f%%", explode=[0, 0.035], wedgeprops={"edgecolor": "black"})

        def graph4() -> None:
            """displays LINE PLOT: number of events per date"""

            x_axis, y_axis = [row[0].strftime("%a, %b %d, '%y") for row in data], [row[1] for row in data]
            plt.plot(x_axis, y_axis, marker="o", color="b", linewidth=1.35, linestyle="--")

        plt.close("all")
        graph_number = {graph_names[i]: i for i in range(4)}[variable]

        try:
            cursor.execute(
                {
                    0: "select app_url, count(*) from passwords where user = {} group by app_url",
                    1: "select city, count(*) from contacts where user = {} group by city",
                    2: "select completed, count(*) from events where user = {} group by completed",
                    3: "select evtdate, count(*) from events where user = {} group by evtdate",
                }[graph_number].format(repr(name))
            )
        except:
            return showerror("Error", "Sorry, we were unable to grab the information necessary for your Graph", parent=UserVault)
        else:
            data, count = sorted(cursor.fetchall(), key=(lambda row: row[0])), cursor.rowcount
            if count in range(2):
                return showinfo("Not Enough Data", "You haven't saved enough Data in your Vault to produce this Graph", parent=UserVault)

        window_heading, graph_heading = {
            0: ("Graph: Number of Passwords per App/URL", "Frequency of Passwords by App/URL"),
            1: ("Graph: Number of Contacts per City", "Frequency of Contacts by City"),
            2: ("Graph: Number of Events per status of completion", "Frequency of Events by their status of completion"),
            3: ("Graph: Number of Event per Date", "Frequency of Events by Date"),
        }[graph_number]

        labels = {
            0: ("Applications/URLs", "Number of Passwords"), 1: ("Number of Contacts", "Name of Cities"),
            3: ("Dates", "Number of Events"),
        }.get(graph_number, ("", ""))

        plt.style.use("seaborn-dark" if graph_number in range(2) else "grayscale")
        plt.figure(window_heading)
        plt.title(graph_heading)

        {i: (graph1, graph2, graph3, graph4)[i] for i in range(4)}[graph_number]()

        plt.get_current_fig_manager().window.wm_iconbitmap(ICONS[17])
        plt.xlabel(labels[0])
        plt.ylabel(labels[1])
        plt.grid(True)
        plt.show()

    imgs, buttons, n = IMAGES[34:40], [], "Number of"
    coms = [view_all, (lambda: view_data("passwords")), (lambda: view_data("contacts")), (lambda: view_data("events"))]

    for i in range(4):
        buttons.append(Button(UserVault, bd=0, image=IMAGES[i+29], command=coms[i], cursor=CURSORS[4] if not i else CURSORS[0]))
        buttons[i].place(x=397.5, y=75*i + 131.25)

    op1 = Button(UserVault, image=imgs[0], bd=3, cursor=CURSORS[0], command=(lambda: vault_ops(name, op1, imgs[0], imgs[1])))
    op2 = Button(UserVault, image=imgs[2], bd=3, cursor=CURSORS[0], command=(lambda: pwd_generator(name, op2, imgs[2], imgs[3])))
    btn = Button(UserVault, image=imgs[4], bd=0, cursor=CURSORS[0], command=(lambda: add_info(name, buttons, btn, imgs[4], imgs[5])))

    graph_names = [
        f"{n} Passwords per App/URL", f"{n} Contacts per City", f"{n} Events Completed/Incomplete", f"{n} Events per Date"
    ]

    menu = ttk.OptionMenu(UserVault, StringVar(), "", *graph_names, command=graph)
    logout = (lambda: askyesno("Log Out?", "Log Out of Secure Vault? You will have to Log In again!", parent=UserVault))
    menu.config(image=IMAGES[33], cursor=CURSORS[0])

    menu.place(x=0, y=474.25)
    op1.place(x=0, y=0)
    op2.place(x=699.375, y=0)
    btn.place(x=676.875, y=448.125)

    UserVault.protocol("WM_DELETE_WINDOW", (lambda: (plt.close("all"), UserVault.destroy()) if logout() else None))


def vault_ops(
    name: str, button: Button, img1: ImageTk, img2: ImageTk
) -> None:
    """displays additional options in the Vault"""

    empty_screen(UserVault, dont_destroy=button)

    if str(button.cget("image")) == str(img1):
        Label(UserVault, image=IMAGES[40]).place(x=0, y=0)
        UserVault.iconbitmap(ICONS[9])
        button = Button(UserVault, image=img2, bd=3, cursor=CURSORS[0], command=(lambda: vault_ops(name, button, img1, img2)))
        button.place(x=0, y=0)

        def user_logout() -> None:
            """prompts a User to log out of the Secure Vault"""

            if askokcancel("Log Out?", "Log Out of Secure Vault? You will have to Log In again!", parent=UserVault):
                UserVault.destroy()

        def user_change() -> None:
            """prompts a User to change their MasterPassword"""

            if askokcancel("Change MasterPassword", "You will be temporarily Logged Out. Still continue?", parent=UserVault):
                UserVault.destroy()
                change_masterpass(name)

        def user_delete() -> None:
            """prompts a User to delete their account"""

            if askokcancel("Confirm?", "Are you sure you want to delete your account? All data will be lost.", parent=UserVault):
                UserVault.destroy()
                delete_user(name)

        coms = [user_change, user_logout, (lambda: exit_app(UserVault))]

        for i in range(3):
            Button(UserVault, image=IMAGES[i+41], bd=0, command=coms[i], cursor=CURSORS[0]).place(x=43, y=75*i + 176.25)
        Button(UserVault, image=IMAGES[44], bd=3, command=user_delete, cursor=CURSORS[0]).place(x=699.375, y=0)

    else:
        vault_window(name)


def pwd_generator(
    name: str, button: Button, img1: ImageTk, img2: ImageTk
) -> None:
    """displays the password generator"""

    empty_screen(UserVault, dont_destroy=button)

    if str(button.cget("image")) == str(img1):
        UserVault.title("Secure Password Generator")
        UserVault.iconbitmap(ICONS[10])
        Label(UserVault, image=IMAGES[45]).place(x=0, y=0)
        button = Button(UserVault, image=img2, bd=3, cursor=CURSORS[0], command=(lambda: pwd_generator(name, button, img1, img2)))
        button.place(x=699.375, y=0)

        def security() -> None:
            """displays the password-security information"""

            messages = [
                "Our Passwords are generared using Top - Class encryption techniques.",
                "These are purely random & secured using intense character mapping & combination.",
                "Our Generators ensure that a unique password is returned each time.",
                "For queries or safety issues, contact developers."
            ]
            showinfo("Security Policy & Information", " ".join(messages), parent=UserVault)

        def copy_clipboard() -> None:
            """copies the current password to the system's clipboard"""

            if not box.get():
                return showinfo("No Password Found", "Please generate a Password first", parent=UserVault)
            else:
                root.clipboard_clear()
                root.clipboard_append(box.get())
                showinfo("Password Copied", "The current Password has been copied to the ClipBoard", parent=UserVault)

        Button(UserVault, image=IMAGES[46], bd=3, command=security, cursor=CURSORS[4]).place(x=0, y=0)
        Button(UserVault, image=IMAGES[47], bd=2, cursor=CURSORS[0], command=copy_clipboard).place(x=708.75, y=102.75)
        box = Entry(UserVault, width=49, bd=2, font=("ariel", 19, "bold"), relief=FLAT, cursor=CURSORS[6], state="readonly")
        box.place(x=15, y=108.75)

        specs = dict(from_=8, to=128, length=375, width=11.25, bg="white", sliderrelief=FLAT, orient=HORIZONTAL)
        slider = Scale(UserVault, cursor=CURSORS[0], **specs)
        slider.place(x=375, y=161.25)

        variables, checks = [IntVar() for _ in range(4)], []
        for i in range(4):
            checks.append(Checkbutton(UserVault, bd=17, bg="white", variable=variables[i], cursor=CURSORS[0]))
            checks[i].place(x=375, y=(235 + (i * 57.5)))
        variables[0].set(1)

        btn = Button(UserVault, image=IMAGES[48], cursor=CURSORS[0], bd=0, command=(lambda: gen_pass(slider, variables, box)))
        btn.place(x=337.5, y=468.75)

    else:
        vault_window(name)


def gen_pass(
    scale: Scale, variables: list[int, 4], entrybox: Entry
) -> None:
    """accesses the User's choices to generate a password"""

    p_len, values = scale.get(), tuple(var.get() for var in variables)
    password, st = generate(p_len, values), entrybox.cget("state")
    if password != "ok":
        entrybox.config(state=NORMAL)
        entrybox.delete(0, END)
        entrybox.insert(0, password)
        entrybox.config(state=st)


def add_info(
    name: str, buttons: list[Button, 4], button: Button, add: ImageTk, cross: ImageTk
) -> None:
    """chooses which information the User wants to save"""

    if str(button.cget("image")) == str(add):
        UserVault.iconbitmap(ICONS[11])

        def add_data() -> None:
            """displays what type of information can be stored in the application"""

            messages = [
                "The Secure Vault is the storage house of your: {0}Passwords {0}Contacts {0}Events \n",
                "Your personal data is stored in the database in encrypted formats - not even we can access them!"
            ]
            showinfo("Store Data", "".join(messages).format("\n\t\N{BULLET} "), parent=UserVault)

        coms = [add_data, (lambda: add_passwords(name)), (lambda: add_contacts(name)), (lambda: add_events(name))]
        for i in range(4):
            buttons[i].config(image=IMAGES[i+49], command=coms[i])
        button.config(image=cross)

    else:
        vault_window(name)


def confirm(
    save_data: Callable[[str, list[Entry], str], None], user: str, entryboxes: list[Entry],
    msg: bool|None = True, query: str|None = None
) -> bool:
    """confirms if the User wants to save the entered data"""

    if msg:
        if askokcancel("Confirm?", "Do you want to save the data?", parent=UserVault):
            save_data(user, entryboxes, query)
        else:
            return False
    else:
        save_data(user, entryboxes, query)
    return True


def add_passwords(user: str) -> None:
    """creates the add-passwords window"""

    empty_screen(UserVault)
    UserVault.title("Add New Passwords")
    UserVault.iconbitmap(ICONS[12])
    Label(UserVault, image=IMAGES[53]).place(x=0, y=0)

    specs = dict(master=UserVault, width=21, bd=2, font=("ariel", 19, "bold"), relief=FLAT, cursor=CURSORS[6], bg=color)
    entries = [Entry(**specs) for _ in range(3)] + [Text(height=3.4, **specs)]

    for i in range(4):
        entries[i].place(x=180, y=74.25*i + 112.5)
    entries[2].insert(0, "(Optional)")
    entries[3].insert(0.0, "(Optional)")

    hs = Button(UserVault, image=hide, bd=2, cursor=CURSORS[0], command=(lambda: hideshow(hs, entries[1], *IMAGES[17:19])))
    hs.place(x=495, y=180.75)

    specs = dict(from_=8, to=128, length=202, width=10, bg="white", sliderrelief=FLAT, orient=HORIZONTAL)
    slider = Scale(UserVault, cursor=CURSORS[0], **specs)
    slider.place(x=551.25, y=186.75)

    variables, checks = [IntVar() for _ in range(4)], []
    for i in range(4):
        checks.append(Checkbutton(UserVault, bd=10, bg="white", variable=variables[i], cursor=CURSORS[0]))
        checks[i].place(x=498.85, y=69.85*i + 250.5)
    variables[0].set(1)

    btn1 = Button(UserVault, image=IMAGES[54], bd=0, cursor=CURSORS[0], command=(lambda: gen_pass(slider, variables, entries[1])))
    btn2 = Button(UserVault, image=IMAGES[55], bd=0, cursor=CURSORS[0], command=(lambda: confirm(save_pass, user, entries)))
    btn1.place(x=495, y=105)
    btn2.place(x=15, y=463.125)

    back_button(UserVault, (lambda: vault_window(user)))


def save_pass(name_user: str, values: list[Entry], query: str|None = None) -> None:
    """adds a new/updates an existing record in Table 'passwords' in database"""

    v0, v1, v2, v3 = *[v.get().strip() for v in values[:3]], values[3].get(0.0, END).strip()

    v1 = values[1].get()
    v2 = "" if v2.casefold() == "(optional)" else v2.upper()
    v3 = "" if v3.casefold() == "(optional)" else v3.upper()

    if valid_username(v0):
        return values[0].delete(0, END)

    if valid_password(v1):
        return values[1].delete(0, END)

    if len(v2) not in range(101):
        showerror("Error", "URL must be less than 100 characters", parent=UserVault)
        return values[2].delete(0, END)

    if len(v3) not in range(201):
        showerror("Error", "Notes must be less than 200 characters", parent=UserVault)
        return values[3].delete(0.0, END)

    check_name(name_user)        # updates encryption keys
    sv_up = "save" if query is None else "update"

    try:
        cursor.execute(
            f"insert into passwords values {(name_user.upper(), v0.upper(), encrypt(v1), v2, v3)}"
            if query is None else query.format(repr(v0.upper()), repr(encrypt(v1)), repr(v2), repr(v3))
        )
    except con.errors.IntegrityError:
        return showerror("Error", f"Data with Username {v0 !r} already exists", parent=UserVault)
    except:
        return showerror("Error", f"Sorry, we were unable to {sv_up} your Data!", parent=UserVault)
    else:
        mydb.commit()
        showinfo("Successful", f"Your Data has been {sv_up + 'd'}!", parent=UserVault)
    finally:
        {v.delete(0, END) for v in values[:-1]}
        values[3].delete(0.0, END)
        values[2].insert(0, "(Optional)")
        values[3].insert(0.0, "(Optional)")


def add_contacts(user: str) -> None:
    """creates the add-contacts window"""

    empty_screen(UserVault)
    UserVault.title("Add New Contacts")
    UserVault.iconbitmap(ICONS[13])
    Label(UserVault, image=IMAGES[56]).place(x=0, y=0)

    specs = dict(width=31, bd=2, font=("ariel", 19, "bold"), relief=FLAT, cursor=CURSORS[6], bg=color)
    entries = [Entry(UserVault, **specs) for _ in range(5)]
    for i in range(5):
        entries[i].place(x=315, y=67.5*i + 120.5)
    entries[2].insert(0, "(Optional)")
    entries[3].insert(0, "(Optional)")
    entries[4].insert(0, "(Optional - Default NEW DELHI)")

    button = Button(UserVault, image=IMAGES[55], bd=0, cursor=CURSORS[0], command=(lambda: confirm(save_cont, user, entries)))
    button.place(x=15, y=463.125)

    back_button(UserVault, (lambda: vault_window(user)))


def save_cont(name_user: str, values: list[Entry], query: str|None = None) -> None:
    """adds a new/updates an existing record in Table 'contacts' in database"""

    v0, v1, v2, v3, v4 = [v.get().strip() for v in values]

    v2 = "" if v2.casefold() == "(optional)" else v2
    v3 = "01-01-0001" if v3.casefold() in {"(optional)", ""} else v3
    v4 = "NEW DELHI" if v4.casefold() in {"(optional - default new delhi)", ""} else v4.upper()

    if len(v0) not in range(3, 51):
        if not v0:
            return showwarning("Required Field", "Contact Name cannot be empty", parent=UserVault)
        showerror("Error", "Contact Name must be between 3 - 50 characters", parent=UserVault)
        return values[0].delete(0, END)

    if not v1:
        return showwarning("Required Field", "Contact Number cannot be empty", parent=UserVault)
    if valid_contact(v1):
        return values[1].delete(0, END)
    if v2:
        if valid_contact(v2):
            return values[2].delete(0, END)

    try:
        v3 = dt.strptime(v3, "%d-%m-%Y").date()
    except ValueError:
        try:
            v3 = dt.strptime(v3, "%d/%m/%Y").date()
        except ValueError:
            showerror("Error", "Invalid Date format used", parent=UserVault)
            return values[3].delete(0, END)

    sv_up = "save" if query is None else "update"

    try:
        cursor.execute(
            f"insert into contacts values {(name_user.upper(), v0.upper(), v1, v2, str(v3), v4)}"
            if query is None else query.format(repr(v0.upper()), repr(v1), repr(v2), repr(str(v3)), repr(v4))
        )
    except con.errors.IntegrityError:
        return showerror("Error", f"Data with Contact Number {v1 !r} already exists", parent=UserVault)
    except:
        return showerror("Error", f"Sorry, we were unable to {sv_up} your Data!", parent=UserVault)
    else:
        mydb.commit()
        showinfo("Successful", f"Your Data has been {sv_up + 'd'}!", parent=UserVault)
    finally:
        {v.delete(0, END) for v in values}
        values[2].insert(0, "(Optional)")
        values[3].insert(0, "(Optional)")
        values[4].insert(0, "(Optional - Default NEW DELHI)")


def add_events(user: str) -> None:
    """creates the add-events window"""

    empty_screen(UserVault)
    UserVault.title("Add New Events")
    UserVault.iconbitmap(ICONS[14])
    Label(UserVault, image=IMAGES[57]).place(x=0, y=0)

    specs   = dict(width=31, bd=2, font=("ariel", 19, "bold"), relief=FLAT, cursor=CURSORS[6], bg=color)
    entries = [Entry(UserVault, **specs) for _ in range(4)]
    for i in range(4):
        entries[i].place(x=315, y=69*i + 112.5)
    entries[2].insert(0, "(Optional - Default 00:00:00)")
    entries[3].insert(0, "YES/NO (Default NO)")

    button = Button(UserVault, image=IMAGES[55], bd=0, cursor=CURSORS[0], command=(lambda: confirm(save_evnt, user, entries)))
    button.place(x=15, y=463.125)

    back_button(UserVault, (lambda: vault_window(user)))


def save_evnt(name_user: str, values: list[Entry], query: str|None = None) -> None:
    """adds a new/updates an existing record in Table 'events' in database"""

    v0, v1, v2, v3 = [v.get().strip() for v in values]

    v2 = "00:00:00" if v2.casefold() in {"(optional - default 00:00:00)", ""} else v2
    v3 = "NO" if v3.casefold() in {"yes / no (default no)", ""} else v3.upper()

    if len(v0) not in range(3, 31):
        if not v0:
            return showwarning("Required Field", "Title of Event cannot be empty", parent=UserVault)
        showerror("Error", "Title of Event must be between 3 - 31 characters", parent=UserVault)
        return values[0].delete(0, END)

    if not v1:
        showwarning("Required Field", "Date of Event cannot be empty", parent=UserVault)
        return values[1].delete(0, END)

    try:
        v1 = dt.strptime(v1, "%d-%m-%Y").date()
    except ValueError:
        try:
            v1 = dt.strptime(v1, "%d/%m/%Y").date()
        except ValueError:
            showerror("Error", "Invalid Date format used", parent=UserVault)
            return values[1].delete(0, END)

    if v2.count(":") == 1 and " " not in v2:
        v2 = f"{v2[:-2]} {v2[-2:]}"
    try:
        v2 = dt.strptime(v2, "%I:%M %p").time()
    except ValueError:
        try:
            v2 = dt.strptime(v2, "%H:%M:%S").time()
        except ValueError:
            showerror("Error", "Invalid Time format used", parent=UserVault)
            return values[2].delete(0, END)

    if v3 not in {"YES", "NO"}:
        return showerror("Error", "Status of completion must be YES/NO", parent=UserVault)

    sv_up = "save" if query is None else "update"

    try:
        cursor.execute(
            f"insert into events values {(name_user.upper(), v0.upper(), str(v1), str(v2), v3)}"
            if query is None else query.format(repr(v0.upper()), repr(str(v1)), repr(str(v2)), repr(v3))
        )
    except con.errors.IntegrityError:
        return showerror("Error", f"Data with Event Title {v0 !r} already exists", parent=UserVault)
    except:
        return showerror("Error", f"Sorry, we were unable to {sv_up} your Data!", parent=UserVault)
    else:
        mydb.commit()
        showinfo("Successful", f"Your Data has been {sv_up + 'd'}!", parent=UserVault)
    finally:
        {v.delete(0, END) for v in values}
        values[2].insert(0, "(Optional - Default 00:00:00)")
        values[3].insert(0, "YES / NO (Default NO)")


def display_records(
    parent: Tk, tablename: str, title: str, query: str, no_records: tuple[str]
) -> None:
    """fetches and displays records from the database and helps User to update thier records"""
    global window, trv

    try:
        window.destroy()
    except NameError:
        pass
    finally:
        icon = {"passwords": ICONS[12], "contacts": ICONS[13], "events": ICONS[14]}

    try:
        cursor.execute(query)
    except:
        return showerror("Error", "Sorry, some unexpected error occurred", parent=parent)
    else:
        data, count = cursor.fetchall(), cursor.rowcount
        height = 20*count + 70
        if not count:
            return showinfo(*no_records, parent=parent)
        if count != 1:
            if parent is root:
                data.sort(key=(lambda row: (row[0], row[1])))
            else:
                data.sort(key=(lambda row: (row[1], row[2])))

    window, ns = Toplevel(parent), "Not Specified"
    window.resizable(False, False)
    window.title(title)
    window.iconbitmap(ICONS[15] if parent is root else icon[tablename])

    if parent is not root:
        name = data[0][0].title()

    if tablename == "passwords":
        headings = ["S.No.", "Username", "Password", "Application/URL", "Notes"]
        widths = [50, 150, 150, 150, 200]
        if "name" in locals():
            check_name(name)        # updates decryption keys
    elif tablename == "contacts":
        headings = ["S.No.", "Name of Contact", "Contact Number", "Alternate Number", "Date of Birth", "Place"]
        widths = [50, 150, 150, 150, 200, 150]
    else:
        headings = ["S.No.", "Title of Event", "Date of Event", "Time of Event", "Status of Completion"]
        widths = [50, 150, 200, 150, 170]

    if parent is root:
        headings[0], widths[0] = "Name of User", 150
    window.geometry(f"{sum(widths)+45}x{height}")

    table, columns = Frame(window, cursor=CURSORS[4] if parent is root else CURSORS[7]), range(len(headings))
    table.pack(side=LEFT, padx=20)
    trv = ttk.Treeview(table, columns=tuple(columns), show="headings", height=str(count), selectmode="browse")

    for i in columns:
        trv.heading(i, text=headings[i])
        trv.column(i, minwidth=widths[i], width=widths[i])

    for i in range(len(data)):
        row = list(data[i])

        if tablename == "passwords":
            app_url = row[3].endswith((".COM", ".NET", ".IN"))
            if parent is root:
                check_name(row[0].title())        # updates decryption key for every User separately
            row[1], row[2] = row[1].lower(), decrypt(row[2])
            row[3] = row[3].lower() if app_url else row[3].capitalize() if row[3] else ns
            row[4] = row[4].capitalize() if row[4] else ns

        elif tablename == "contacts":
            row[1], row[2], row[5] = row[1].title(), row[2].zfill(10), row[5].title()
            row[3] = row[3].zfill(10) if row[3] else ns
            row[4] = row[4].strftime("%A, %B %d, '%Y") if row[4] != dt.min.date() else ns

        else:
            row[1] = row[1].title()
            row[2] = row[2].strftime("%A, %B %d, '%Y")
            row[3] = (dt.min + row[3]).time().strftime("%I:%M:%S %p")

        row[0] = (i + 1) if parent is not root else row[0].title()
        trv.insert("", "end", values=tuple(row))

    trv.pack()

    if parent is root:
        title, message = "Unable to change Data", "Admins are not allowed to edit (delete/update) the User's Data"
        for event in "<Button-3>", "<Double-Button-1>":
            trv.bind(event, (lambda event: showwarning(title, message, parent=window)))
        return style.map("Treeview", background=[("selected", "green")])

    menu = None

    def edit_row(event: Event) -> None:
        """displays a menu to delete/update User's records"""
        nonlocal menu

        if event.y not in range(25, 20*count + 26):
            return
        if event.num == 3:
            trv.selection_set(trv.identify_row(event.y))

        menu = Menu(window, tearoff=False)
        menu.add_command(label="Delete Row", command=(lambda: get_row(tablename, True, name)))
        menu.add_command(label="Update Row", command=(lambda: get_row(tablename, False, name)))
        menu.tk_popup(x=event.x_root, y=event.y_root)

    trv.bind("<Button-3>", edit_row)
    trv.bind("<Double-Button-1>", edit_row)


def get_row(tablename: str, selection: bool, name_user: str) -> None:
    """displays update/delete data prompts in UserVault"""

    items = trv.item(trv.focus())["values"]
    style.map("Treeview", background=[("selected", "red" if selection else "#f59304")])

    if selection:
        if askyesno("Confirm", "Do you want to delete the selected data?", parent=window):
            delete_row(items, tablename, name_user)
            window.destroy()
    elif askyesno("Confirm", "Do you want to update this data?", parent=window):
        update_row(items, tablename, name_user)
        window.destroy()

    style.map("Treeview", background=[("selected", "#0078d7")])


def delete_row(row: tuple[str], table: str, name_user: str) -> None:
    """deletes a row from a Table in the database"""

    pri_key = {"passwords": "username", "contacts": "contact_no", "events": "evttitle"}[table]
    value = repr(row[1]) if table != "contacts" else row[2]
    try:
        cursor.execute(f"delete from {table} where {pri_key} = {value} and user = {name_user !r}")
    except:
        return showerror("Error", "Sorry, we were unable to delete your Data!", parent=window)
    else:
        mydb.commit()
        showinfo("Successful", "Your Data has been deleted", parent=window)


def update_row(row: tuple[str], table: str, name_user: str) -> None:
    """updates a row from a Table in the database"""

    UserVault.title(f"Update your {table.capitalize()}")
    specs = dict(master=UserVault, width=37, bd=2, font=("ariel", 19, "bold"), relief=FLAT, cursor=CURSORS[6], bg=color)

    u1 = "username = {}, password = {}, app_url = {}, notes = {} where username ="
    u2 = "fullname = {}, contact_no = {}, alternate_no = {}, birthday = {}, city = {} where contact_no ="
    u3 = "evttitle = {}, evtdate = {}, evttime = {}, completed = {} where evttitle ="

    attrs = {
        "passwords": (ICONS[12], IMAGES[58], 3, True, 75, save_pass, f"update passwords set {u1} {row[1] !r}"),
        "contacts": (ICONS[13], IMAGES[59], 5, False, 71.25, save_cont, f"update contacts set {u2} {str(row[2]) !r}"),
        "events": (ICONS[14], IMAGES[60], 4, False, 75, save_evnt, f"update events set {u3} {row[1] !r}"),
    }.get(table)

    UserVault.iconbitmap(attrs[0])
    Label(UserVault, image=attrs[1]).place(x=0, y=0)
    entries = [Entry(**specs) for _ in range(attrs[2])] + ([Text(height=3.4, **specs)] if attrs[3] else [])
    extra = 15 if table == "events" else 0

    if table != "passwords":
        ind = 2 if table == "events" else -2
        if row[ind] != "Not Specified":
            row[ind] = dt.strptime(row[ind], "%A, %B %d, '%Y").strftime("%d-%m-%Y")
        if table == "events":
            row[3] = dt.strptime(row[3], "%I:%M:%S %p").strftime("%H:%M:%S")

    for i in range(len(entries)):
        entries[i].place(x=202.5, y=(112.5 + extra + (i * (attrs[4] + extra//2))))
        row[i+1] = "" if row[i+1] == "Not Specified" else row[i+1]
        try:
            entries[i].insert(0, row[i+1])
        except TclError:
            entries[i].insert(0.0, row[i+1])

    def discard() -> None:
        """asks if the User to cancel the updates"""

        if askokcancel("Discard Changes?", "Do you wish to Cancel all changes?", parent=UserVault):
            return vault_window(name_user)

    def update() -> None:
        """asks if the User to save the updates"""

        if askokcancel("Save Changes?", "Do you wish to save your Updates?", parent=UserVault):
            if confirm(save_data=attrs[5], user=name_user, msg=False, entryboxes=entries, query=attrs[6]):
                vault_window(name_user)

    Button(UserVault, image=IMAGES[61], cursor=CURSORS[0], bd=0, command=update).place(x=8.25, y=469.5)
    Button(UserVault, image=IMAGES[62], cursor=CURSORS[0], bd=0, command=discard).place(x=390, y=469.5)


def admin_mode() -> None:
    """requests access to the admin mode-window"""
    global admin

    if not askyesno("Log Users Out?", "Running Admin Mode will log all users out. Still continue?"):
        return

    try:
        plt.close("all")
        UserVault.destroy()
    except NameError:
        pass

    try:
        admin.destroy()
    except NameError:
        pass
    finally:
        admin = Toplevel(root)
        admin.geometry("534x96")
        admin.resizable(False, False)
        admin.title("Access Admin Mode")
        admin.iconbitmap(ICONS[16])

    def access() -> None:
        """grants or revokes access to Admin Status"""

        credentials = tuple(box.get().strip() for box in entries)

        if not all(credentials):
            return showwarning("Required Fields", "Entries cannot be empty", parent=admin)

        if credentials != CREDENTIALS:
            return showerror("ACCESS DENIED", "Cannot access Admin Mode", parent=admin)

        showinfo("ACCESS GRANTED", "Welcome to KeepMyPass' Admin Mode")
        admin.destroy()
        admin_window()

    text1, text2 = "Enter Name of the Admin:", "Enter Password to Admin Mode:"
    text = 49*" " + "Run Admin Mode" + 49*" "
    Label(admin, font=("ariel", 11, "bold"), text=text1.ljust(30)).place(x=5, y=5)
    Label(admin, font=("ariel", 11, "bold"), text=text2.ljust(30)).place(x=5, y=32.5)

    specs = dict(width=35, bd=2, font=("ariel", 11, "bold"), relief=FLAT, cursor=CURSORS[6], bg="#e1e1e1")
    entries = [Entry(admin, **specs) for _ in range(2)]
    entries[0].place(x=242.5, y=5)
    entries[1].place(x=242.5, y=32.5)
    entries[1].bind("<Return>", (lambda event: access()))

    Button(admin, text=text, font=("ariel", 11, "bold"), bd=2, cursor=CURSORS[0], command=access).place(x=3.5, y=60)


def admin_window() -> None:
    """starts the admin mode-window for the Programmer"""

    empty_screen(root)
    root.title("Search Mode")
    root.iconbitmap(ICONS[15])

    Label(image=IMAGES[63]).place(x=0, y=0)
    box = Entry(width=49, bd=2, font=("ariel", 19, "bold"), relief=FLAT, cursor=CURSORS[6], bg=color)
    box.bind("<Return>", (lambda event: search(box, var)))
    box.place(x=15, y=106.5)

    def info() -> None:
        """displays information about admin mode"""
        messages = [
            "An Admin can search through all User's Vaults at once.",
            "Select the type of data you want to see and enter a search key.",
            "Any data that matches your search will be displayed.",
            "You can for '*' to show all data of the selected type of all the current Users.",
            "You may also see an informative Stack Plot showing Number of each item stored per active User.",
            "An active User is one who has at least one record stored in our database."
        ]
        showinfo("Search User Vaults", " ".join(messages))

    def exit_admin() -> None:
        """displays the exit admin mode-prompt"""

        if askyesno("EXIT?", "Do you quit Admin Mode?"):
            try:
                window.destroy()
                style.map("Treeview", background=[("selected", "#0078d7")])
            except NameError:
                pass
            finally:
                main_window()

    def update() -> None:
        """updates the entrybox to display a relevant message"""

        text = box.get().strip().casefold()
        if not text or text in {f"search user {tb}" for tb in {"passwords", "contacts", "events"}}:
            box.delete(0, END)
            box.insert(0, f"Search User {var.get()}")

    var, items = StringVar(), ["Passwords", "Contacts", "Events"]
    for i in range(3):
        button = Radiobutton(bg="white", bd=17, variable=var, value=items[i], command=update, cursor=CURSORS[0])
        button.place(x=52.5, y=(225 + (i * 76)))
    var.set("Passwords")
    update()

    Button(image=IMAGES[8] , bd=3, command=info, cursor=CURSORS[4]).place(x=699.375, y=0)
    Button(image=IMAGES[33], bd=3, cursor=CURSORS[0], command=graph_admin).place(x=0, y=0)
    Button(image=IMAGES[64], bd=2, cursor=CURSORS[0], command=(lambda: search(box, var))).place(x=708.75, y=100)
    Button(image=IMAGES[65], bd=0, cursor=CURSORS[0], command=exit_admin).place(x=11.25, y=457.5)


def search(entrybox: Entry, variable: StringVar) -> None:
    """fetches matching record(s) from the database and displays them"""

    skey, tablename = entrybox.get().strip().casefold(), variable.get().lower()

    enter_txt = {f"search user {table}" for table in {"passwords", "contacts", "events"}}
    if not skey or skey in enter_txt:
        return showwarning("Required Field", "Please enter a Search Key")

    m = f"'%{skey}%'"
    if tablename == "passwords":
        cond = f"username like {m} or app_url like {m} or notes like {m}"
    elif tablename == "contacts":
        cond = f"contact_no like {m} or alternate_no like {m} or fullname like {m} or birthday like {m} or city like {m}"
    else:
        cond = f"evttitle like {m} or evtdate like {m} or evttime like {m} or completed like {m}"

    cond = True if skey == "*" else f"user like {m} or " + cond
    message = ("No Matches", "Data matching your search could not be found") if skey != "*" else \
              ("Empty Database", f"There are no {tablename.capitalize()} in the Database!")

    display_records(
        parent=root, tablename=tablename,
        title=f"Searched {tablename.capitalize()}",
        query=f"select * from {tablename} where {cond}",
        no_records=message
    )


def graph_admin() -> None:
    """displays the STACK PLOT: number of each item per active User in admin mode"""

    plt.close("all")
    data, users, count = [], [], 0

    for table in "passwords", "contacts", "events":
        try:
            cursor.execute(f"select user, count(*) from {table} group by user order by user")
        except:
            return showerror("Error", "Sorry, we were unable to grab the information necessary for this Graph")
        else:
            current_rows, count = cursor.fetchall(), (count + cursor.rowcount)
            data.append(current_rows)
            users.extend(current_rows)

    users, numbers, colors = sorted({row[0].title() for row in users}), [[], [], []], ["green", "#d11718", "#008fd5"]

    for user in set(users):
        for i in range(3):
            for name, n in data[i]:
                if user.casefold() == name.casefold():
                    break
            else:
                data[i].append((user, 0))
            data[i].sort(key=(lambda row: row[0]))

    for i in range(3):
        for name, n in data[i]:
            numbers[i].append(n)

    users = ["\n"+users[i] if i%2 else users[i] for i in range(len(users))]

    plt.style.use("grayscale")
    plt.figure("Graph - Number of Items by each User", figsize=(1.575*len(users), 5.375))
    plt.title("Frequency of Passwords, Contacts & Events per active User")
    plt.get_current_fig_manager().window.wm_iconbitmap(ICONS[17])

    plt.stackplot(users, *numbers, colors=colors, labels=["Passwords", "Contacts", "Events"])
    plt.xlabel("Name of User(s)")
    plt.ylabel("Number of Item(s)")

    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    connect()