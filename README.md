# KeepMyPass

## About KeepMyPass

KeepMyPass is a Password-Management System built in Python using MySQL integration with a graphical-user interface. It was developed in `January, 2020` as a Grade-XII (CBSE) Computer Science Project. It also contains an Event-Managemment and a Contact-Management Systems.

## Acknowledgement & Certification

This project was done partly under assistance of my Grade-XII Computer Science teacher. It is them that I owe the success of my project to. According to them, this project meets all the requirements of Grade-XII Computer Science Project, 2019-20.

It lays the foundations of all the core-concepts taught to us, and covers the topics in elaborate detail. The code is well-presented and easy to understand. The presentation of the app is crisp, and makes a user enjoy its execution.

## Concepts Covered

- Binary-Data File Handling through Python
- MySQL Database Management through Python-MySQL integration
- Creating Graphical-User Interfaces

## Illustration Credits 
*All the illustrations used have been taken from [LastPass](https://www.lastpass.com/), and I claim that I, in no way, can and will use my project for commercial purposes whatsoever with these illustrations.*

## Some features of the App

### Information Feature

> Help buttons are provided on various screens to help the user navigate through the App. The help-text is clear and easy to understand.

### "Forgot Password?" Feature

> If a User forgets their MasterPassword, they can retrieve their lost Account using this feature.

### Password-Generation Feature

> The Secure-Vault contains a Password-Generator that generates (pseudo)random passwords.*

### (Pseudo) Security Features

> The following steps have been taken to store the User's data securely:
> - Binary Files include fake data records.*
> - The data being written into Binary File is encrypted twice.*
> - Only one User can log in at a time.
> - All data is stored in the database in encrypted format, and is decrypted only if the User wishes to see it.
> - The keys for Encryption and Decryption are unique for all Users.

## Footnotes & Security Issues


## Run
Clone the repository on your device and navigate to the folder. 

To run the main application, execute:

```
python3 main.py
```

## Future Plans

- Patch as many Security Issues as possible
- Improve UI/design
- Involvement of real encryption/decryption algorithms instead of character-mapping
