from classes import AddressBook


def add(address_book, *args):
    name_key, phone_key, birthday_key = tuple(args[1:4])
    len_args = len(args)
    if birthday_key and len_args - birthday_key != 2:
            return error("There is should be single birthday value")
    if phone_key:
        number_of_phones = birthday_key - phone_key - 1 if birthday_key else len_args - phone_key - 1
        if number_of_phones == 0:
            return error("There is should be at least one phone")
    if (phone_key and phone_key - name_key != 2) or (not phone_key and birthday_key and birthday_key - name_key != 2) \
    or (not phone_key and not birthday_key and len_args - name_key != 2):
        return error("There is should be single name")
    name = args[name_key+1].title()
    phones = args[phone_key+1:birthday_key if birthday_key else len(args)] if phone_key else []
    birthday = args[-1] if birthday_key else None
    return address_book.add_record(name, *phones, birthday=birthday)


def change(address_book, *args):
    name_key, phone_key, birthday_key = tuple(args[1:4])
    len_args = len(args)
    if birthday_key and len_args - birthday_key != 2:
        return error("There is should be single birthday value")
    if phone_key:
        number_of_phones = birthday_key - phone_key - 1 if birthday_key else len_args - phone_key - 1
        if number_of_phones == 0 or number_of_phones % 2:
            return error("There are should be even number of phones")
    if (phone_key and phone_key - name_key not in (2, 3)) or (not phone_key and birthday_key and birthday_key - name_key not in (2, 3)) \
    or (not phone_key and not birthday_key and len_args - name_key not in (2, 3)):
        return error("There are should be one or two names")
    old_name = args[name_key+1].title()
    new_name = None
    if len_args - name_key != 2 and not args[name_key+2].startswith("-"):
        new_name = args[name_key+2]
        if old_name.casefold() == new_name.casefold():
            return error("Old and new names should be different")
    phones = args[phone_key+1:birthday_key if birthday_key else len(args)] if phone_key else []
    birthday = args[-1] if birthday_key else None
    return address_book.change_record(old_name, new_name, *phones, birthday=birthday)


def remove(address_book, *args):
    name_key, phone_key, birthday_key = tuple(args[1:4])
    len_args = len(args)
    if birthday_key and len_args - birthday_key != 1:
        return error("There is shouldn't be birthday value, just key")
    if (phone_key and phone_key - name_key != 2) or (not phone_key and birthday_key and birthday_key - name_key != 2) \
    or (not phone_key and not birthday_key and len_args - name_key != 2):
        return error("There is should be single name")
    name = args[name_key+1].title()
    phones = args[phone_key+1:birthday_key if birthday_key else len(args)] if phone_key else []
    return address_book.remove_record(name, *phones, phone_key=phone_key, birthday_key=birthday_key)


def show(address_book, *args):
    if args[1] == "all":
        return address_book.show()
    name_key, phone_key = tuple(args[1:3])
    len_args = len(args)
    if not name_key and not phone_key:
        return error("There is should be at least one key")
    if name_key and ((phone_key and phone_key - name_key != 2) or (not phone_key and len_args - name_key != 2)):
        return error("There is should be single name")
    if phone_key and len_args - phone_key != 2:
        return error("There is should be single phone")
    name_string = args[name_key+1] if name_key else None
    phone_string = args[phone_key+1] if phone_key else None
    return address_book.show(name_string, phone_string)


def error(message):
    return message


def exit():
    return "Good bye!"


def hello():
    return "Can I help you?"


def no_command():
    return "Unknown command"


def parser(text):
    if not text:
        return no_command, None
    args = text.strip().split()
    text = text.strip().casefold()
    arg0 = args[0].casefold()
    if (arg0 not in ("add", "change", "remove", "show") and text not in ("show all", "good bye", "bye", "close", "exit", "hello")):
        return no_command, None
    if text == "show all":
        return show, args
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
        
    if arg0 == "add":
        return add, args
    elif arg0 == "change":
        return change, args
    elif arg0 == "remove":
        return remove, args
    elif text == "good bye" or text == "bye" or text == "close" or text == "exit":
        return exit, None
    elif text == "hello":
        return hello, None
    elif arg0 == "show":
        return show, args


def main():
    address_book = AddressBook()
    address_book.load_from_file("data.bin")

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

    address_book.save_to_file("data.bin")


if __name__ == "__main__":
    main()