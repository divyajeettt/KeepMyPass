import pickle


def decrypt(string: str) -> str:
    """decrypts the given string and returns it"""

    dec = [dkey2[char] for char in string[::2]]
    string, copy = "".join(dec), ""

    for i in range(0, len(string), 3):
        copy += dkey1[string[i:i+3]]

    return copy.swapcase()[::-1]


def file_reader() -> tuple[int, list[dict[str, list[str]]]]:
    """reads the Binary Files and returns the number of records and list of users"""

    with open("passwords.dat", "rb") as f1, open("pkeys.dat", "rb") as f2:
        counter, dicts = 0, []
        while True:
            try:
                rec = pickle.load(f1)
            except EOFError:
                break
            else:
                counter += 1
                if counter % 16:
                    continue

            ekey1, dkey1, ekey2, dkey2 = pickle.load(f2)
            name = tuple(rec.keys())[0]
            passwords = rec[name]

            for i in range(len(passwords)):
                passwords[i] = decrypt(passwords[i])

            dicts.append({decrypt(name): passwords})

    return counter, dicts


def main() -> None:
    """__main__ function"""

    counter, dicts = file_reader()

    print("number of records =", counter)
    print("actual number of users =", counter // 16, "\n")

    for i, d in enumerate(dicts, start=1):
        print(i, d)


if __name__ == "__main__":
    main()