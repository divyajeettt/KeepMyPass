# KeepMyPass

## About KeepMyPass

KeepMyPass is a Password-Management System built in Python using MySQL integration with a graphical-user interface. It was developed in `June/July, 2020` as a Grade-XII (CBSE) Computer Science Project. It also contains an Event-Managemment and a Contact-Management System.

## Acknowledgement & Certification

This project was done partly under assistance of my Grade-XII Computer Science teacher. It is them that I owe the success of my project to. According to them, this project meets all the requirements of Grade-XII Computer Science Project, 2019-20.

It lays the foundations of all the core-concepts taught to us, and covers the topics in elaborate detail. The code is well-presented and easy to understand. The presentation of the app is crisp, and makes a user enjoy its execution.

## Concepts Covered

- Binary-Data File Handling through Python
- MySQL Database Management through Python-MySQL integration using `mysql.connector`[¹](https://pypi.org/project/mysql-connector-python/)
- Creating Graphical-User Interfaces using `tkinter`[²](https://docs.python.org/3/library/tkinter.html)

## Some features of the App

### Information Feature

> Help buttons are provided on various screens to assist the user navigate through the App. The help-text is clear and easy to understand.

### Forgot-Password Feature

> If a User forgets their MasterPassword, they can retrieve their lost Account using this feature.

### Password-Generation Feature

> The Secure-Vault contains a Password-Generator that generates (pseudo)random passwords.*

### (Pseudo) Security Features

> - Binary Files include fake data records.*
> - The data being written into Binary File is encrypted twice.*
> - Only one User can log in at a time.
> - All data is stored in the database in encrypted format, and is decrypted only if the User wishes to see it.
> - The keys for encryption/decryption are unique for every User.

### Admin-Mode Feature

> Using a password-protected Admin-Mode, a person can search through all User-Vaults at once.* The search can be used to search specific records or all records of a particular type.

## Footnotes & Security Issues

- The project uses the <b>insecure</b> Python module `pickle`[³](https://docs.python.org/3/library/pickle.html). 
- In the project, it has been mentioned (in several places) that the generated passwords are 'secure'. Do note that the passwords are however *[pseudorandom](https://en.wikipedia.org/wiki/Pseudorandomness#:~:text=A%20pseudorandom%20sequence%20of%20numbers,completely%20deterministic%20and%20repeatable%20process.)*, although an element of the password-generation function does use `os.urandom()`[⁴](https://docs.python.org/3/library/os.html#os.urandom).
- The Admin-Mode feature has only been added to the project to meet the requirements set by CBSE. In no way should the feature be taken advantage of. I, the developer, completely understand that being able to access all the stored data, and providing its access to the end-users is <b>very problematic and unethical</b>.
- The encryption technique implemented <b>solely</b> comprises of different types of character mappings and [ROT-ciphers](https://en.wikipedia.org/wiki/ROT13), i.e. no real encryption algorithm has been used in the project. 
- Inclusion of fake records in the Binary Files does not really affect the security of actual data records.
- Encrypting the data twice has no added benefit as compared to encrypting it only once.
- `file_reader.py` has only been added as a back-end functionality checker. It is not meant for use.

## Illustration Credits 

*All illustrations used in the project have been taken from [LastPass](https://www.lastpass.com/), and I claim that I, in no way, can and will use my project for commercial purposes whatsoever with these illustrations.*

## Run

To use, clone the repository on your device, navigate to the folder, and execute:

```
python3 main.py
```

## Future Plans & Scopes of Improvemnt

- Patch as many Security Issues as possible
- Improve UI/design
- Involvement of real encryption/decryption algorithms instead of character-mapping
- Use of an alternate package to handle Binary Files
- Implementation of an alternative to store encryption/decryption keys
- The password to the Admin-Mode should <b>not</b> be hard-coded into the file
- Branch the project, wherein the Admin-Mode will be removed
