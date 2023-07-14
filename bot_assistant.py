import pickle
from classes import AddressBook


def error(message):
    return message


def exit():
    return "Good bye!"


def hello():
    return "Can I help you?"


def no_command():
    return "Unknown command"


def parser(text):
    args = text.strip().split()
    text = text.strip().casefold()
    arg0 = args[0].casefold()
    if not args or (arg0 not in ("add", "change", "remove", "show") and text not in ("show all", "good bye", "bye", "close", "exit", "hello")):
        return no_command, None
    if text == "show all":
        return AddressBook.show, args
    name_key = None
    phone_key = None
    birthday_key = None
    for i, arg in enumerate(args):
        arg = arg.casefold()
        if arg == "-name" or arg == "-names":
            if name_key:
                return error, "There are shouldn't be duplicate keys"
            else:
                name_key = i
        if arg == "-phone" or arg == "-phones":
            if phone_key:
                return error, "There are shouldn't be duplicate keys"
            else:
                phone_key = i
        if arg == "-birthday":
            if birthday_key:
                return error, "There are shouldn't be duplicate keys"
            else:
                birthday_key = i

    if arg0 == "add" or arg0 == "change" or arg0 == "remove":
        if not name_key:
            return error, "The -name(s) key is necessary for adding, changing or removing"
        if (birthday_key and phone_key and (birthday_key < name_key or birthday_key < phone_key)) or (phone_key and phone_key < name_key):
            return error, "The order of keys for adding, changing or removing should be: -name(s) -phone(s) -birthday"
    elif arg0 == "show":
        if name_key and phone_key and phone_key < name_key:
            return error, "The order of keys for showing should be: -name(s) -phone(s)"
        if birthday_key:
            return error, "Showing by birthday are not allowed"
        
    if arg0 == "add" or arg0 == "change" or arg0 == "remove" or arg0 == "show":
        if name_key:
            name_key += 3
        if phone_key:
            phone_key += 3
        if birthday_key:
            birthday_key += 3
        args.insert(1, birthday_key)
        args.insert(1, phone_key)
        args.insert(1, name_key)
        len_args = len(args)
        
    if arg0 == "add":
        if birthday_key and len_args - birthday_key != 2:
            return error, "There is should be single birthday value"
        if phone_key:
            number_of_phones = birthday_key - phone_key - 1 if birthday_key else len_args - phone_key - 1
            if number_of_phones == 0:
                return error, "There is should be at least one phone"
        if (phone_key and phone_key - name_key != 2) or (not phone_key and birthday_key and birthday_key - name_key != 2) \
        or (not phone_key and not birthday_key and len_args - name_key != 2):
            return error, "There is should be single name"
        return AddressBook.add_record, args
    elif arg0 == "change":
        if birthday_key and len_args - birthday_key != 2:
            return error, "There is should be single birthday value"
        if phone_key:
            number_of_phones = birthday_key - phone_key - 1 if birthday_key else len_args - phone_key - 1
            if number_of_phones == 0 or number_of_phones % 2:
                return error, "There are should be even number of phones"
        if (phone_key and phone_key - name_key not in (2, 3)) or (not phone_key and birthday_key and birthday_key - name_key not in (2, 3)) \
        or (not phone_key and not birthday_key and len_args - name_key not in (2, 3)):
            return error, "There are should be one or two names"
        return AddressBook.change_record, args
    elif arg0 == "remove":
        if birthday_key and len_args - birthday_key != 1:
            return error, "There is shouldn't be birthday value, just key"
        if (phone_key and phone_key - name_key != 2) or (not phone_key and birthday_key and birthday_key - name_key != 2) \
        or (not phone_key and not birthday_key and len_args - name_key != 2):
            return error, "There is should be single name"
        return AddressBook.remove_record, args
    elif text == "good bye" or text == "bye" or text == "close" or text == "exit":
        return exit, None
    elif text == "hello":
        return hello, None
    elif arg0 == "show":
        if not name_key and not phone_key:
            return error, "There is should be at least one key"
        if name_key and ((phone_key and phone_key - name_key != 2) or (not phone_key and len_args - name_key != 2)):
            return error, "There is should be single name"
        if phone_key and len_args - phone_key != 2:
            return error, "There is should be single phone"
        return AddressBook.show, args


def main():
    try:
        with open("data.bin", "rb") as fh:
            address_book = pickle.load(fh)
    except (FileNotFoundError, MemoryError):
        address_book = AddressBook()

    while True:
        user_input = input(">>> ")
        command, data = parser(user_input)
        type_data = type(data)
        if type_data == list:
            result = command(address_book, *data)
        elif type_data == str:
            result = command(data)
        else:
            result = command()
        print(result)
        if result == "Good bye!":
            break
    
    for i, record in enumerate(address_book.iterator()):
        print(f"\nPage {i+1}\n")
        print(record)

    with open("data.bin", "wb") as fh:
        pickle.dump(address_book, fh)


if __name__ == "__main__":
    main()