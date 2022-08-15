# keep-my-pass

## About keep-my-pass

keep-my-pass is a Password-Management System built in Python using MySQL integration with a graphical-user interface. It was developed in `January, 2020` as a Grade-XII (CBSE) Computer Science Project. It also contains an Event-Managemment and a Contact-Management Systems.

## Acknowledgement & Certification

This project was done partly under assistance of my Grade-XII Computer Science teacher. It is them that I owe the success of my project to. According to them, this project met all the requirements of Grade-XII Computer Science Project, 2019-20.

It lays the foundations of all the core-concepts taught to us, and covers the topics in elaborate detail. The code is well-presented and easy to understand. The presentation of the app is crisp, and makes a user enjoy its execution.

## Back-End Details

### Binary-Data Files

Following is a list of Binary-Data Files used in this project, described along with their structure and purpose:

- `passwords.dat`
    - For storage of 'MasterPasswords'
    - Each record is a `dictionary` of the format: `{"username": [*MasterPasswords]}`
- `pkeys.dat`
    - For storage of encryption and decryption keys for each user
    - Each entry in a record is a `mapping` of `chars`
    - Each record is a `tuple` of the format: `(encKey1, decKey1, encKey2, decKey2)`
## Illustration Credits

## Footnotes (Security Issues)

## Future Plans
