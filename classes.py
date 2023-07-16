from collections import deque, UserDict
from datetime import datetime
import pickle


DATE_FORMAT = "%d.%m.%Y"
N = 2


class Field:
    def __bool__(self):
        return bool(self.value)
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        return self.value == other.value
        

class Birthday(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    def __str__(self):
        return self.value.strftime(DATE_FORMAT)

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        try:
            self.__value = datetime.strptime(value, DATE_FORMAT).date()
        except (TypeError, ValueError):
            pass


class Name(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if value.isalpha():
            self.__value = value.title()


class Phone(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if value.isdecimal() and len(value) == 12:
            self.__value = value


class Record:
    def __init__(self, name, *phones, birthday=None):
        self.name = name
        self.phones = []
        self.birthday = deque(maxlen=1)
        for phone in phones:
            self.add_phone(phone)
        self.set_birthday(birthday)

    def __str__(self):
        result = f"Name: {self.name}\n"
        if self.phones:
            result += f"    Phone(s): {', '.join(map(str, self.phones))}\n"
        else:
            result += f"    Phone(s):\n"
        if self.birthday:
            result += f"    Birthday: {self.birthday[0]}, {self.days_to_birthday()} day(s) to next birthday\n"
        else:
            result += f"    Birthday:\n"
        result += "\n"
        return result

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            timedelta = self.birthday[0].value.replace(year=today.year) - today
            if timedelta.days < 0:
                timedelta = self.birthday[0].value.replace(year=today.year+1) - today
            return timedelta.days

    def add_phone(self, phone):
        if phone in self.phones:
            return "The phone is exist"
        if phone:
            self.phones.append(phone)
        return "Add phone success"

    def change_phone(self, old_phone, new_phone):
        if old_phone == new_phone:
            return "Old and new phones should be different"
        if new_phone in self.phones:
            return "The new phone is already exist"
        for i, phone in enumerate(self.phones):
            if phone == old_phone:
                if new_phone:
                    self.phones[i] = new_phone
                    return "Change success"
        return "The phone is not found"

    def remove_phone(self, phone):
        try:
            self.phones.remove(phone)
            return "Remove phone success"
        except ValueError:
            return "The phone is not found"
    
    def set_birthday(self, birthday):
        if birthday:
            self.birthday.append(birthday)
            return "Set birthday success"
        return "The birthday value is invalid"
    

class AddressBook(UserDict):
    def iterator(self):
        return AddressBookIterator(self)

    def add_record(self, name, *phones, birthday=None):
        name = Name(name)
        phones = list(map(Phone, phones))
        birthday = Birthday(birthday)
        if not name:
            return "The name is invalid"
        key = str(name)
        if key in self.data.keys():
            if not phones and not birthday:
                return "The contact is exist"
            else:
                if phones:
                    for phone in phones:
                        self.data[key].add_phone(phone)
                if birthday:
                    self.data[key].set_birthday(birthday)
                return "Add data in record success"
        record = Record(name, *phones, birthday=birthday)
        self.data[key] = record
        return "Add record success"
    
    def change_record(self, old_name, new_name, *phones, birthday=None):
        old_name = Name(old_name)
        phones = list(map(Phone, phones))
        birthday = Birthday(birthday)
        if not old_name:
            return "The old name is invalid"
        if new_name:
            new_name = Name(new_name)
            if not new_name:
                return "The new name is invalid"
            if str(new_name) in self.data.keys():
                return "The contact with new name is already exist"
        key = str(old_name)
        if key in self.data.keys():
            if new_name:
                record = self.data.pop(key)
                record = Record(new_name, *record.phones, birthday=record.birthday[0] if record.birthday else None)
                key = str(new_name)
                self.data[key] = record
            if phones:
                for el in enumerate(phones):
                    if not el[0] % 2:
                        self.data[key].change_phone(phones[el[0]], phones[el[0]+1])
            if birthday:
                self.data[key].set_birthday(birthday)
            return "Change record success"
        return "The contact is not found"
    
    def remove_record(self, name, *phones, phone_key=None, birthday_key=None):
        name = Name(name)
        phones = list(map(Phone, phones))
        if not name:
            return "The name is invalid"
        key = str(name)
        if key in self.data.keys():
            if not phone_key and not birthday_key:
                self.data.pop(key)
                return "Remove record success"
            else:
                if phone_key:
                    if phones:
                        for phone in phones:
                            self.data[key].remove_phone(phone)
                    else:
                        self.data[key].phones.clear()
                if birthday_key:
                    self.data[key].birthday.clear()
                return "Remove data in record success"
    
    def show(self, name_string=None, phone_string=None):
        if not self.data:
            result = "The address book is empty"
        elif not name_string and not phone_string:
            result = ""
            for record in self.values():
                result += str(record)
        else:
            result = ""
            for key, record in self.items():
                found_in_phones = False
                if phone_string:
                    for phone in record.phones:
                        if phone_string in phone.value:
                            found_in_phones = True
                            break
                if (name_string and name_string.casefold() in key.casefold()) or found_in_phones:
                    result += str(record)
        if not result:
            return "Not found"
        return result
    
    def load_from_file(self, file_name):
        try:
            with open(file_name, "rb") as fh:
                self.data = pickle.load(fh)
                return "Load suscces"
        except:
            return "File not found, corrupted or empty"
        
    def save_to_file(self, file_name):
        with open(file_name, "wb") as fh:
            pickle.dump(self, fh)
            return "Save success"


class AddressBookIterator:
    def __init__(self, address_book: AddressBook):
        self.address_book = address_book
        self.keys = list(self.address_book.keys())
        self.len_keys = len(self.keys)

    def __iter__(self):
        self.current_index = 0
        return self
    
    def __next__(self):
        if self.current_index >= self.len_keys:
            raise StopIteration
        result = ""
        for _ in range(N):
            key = self.keys[self.current_index]
            record = self.address_book[key]
            result += str(record)
            self.current_index += 1
            if self.current_index >= self.len_keys:
                break
        return result