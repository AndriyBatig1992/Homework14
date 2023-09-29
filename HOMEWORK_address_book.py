from HOMEWORK_classess_ab import AddressBook, Record, AddressBookFileHandler, Phone, Email, Birthday, Name, ConsoleUserView, UserView, GuiUserView
from functools import wraps
from colorama import init as init_colorama, Fore, Style
from pathlib import Path
from store import COMMANDS
from typing import Union


ADDRESSBOOK_LOGO = """
                .o8        .o8                                       
               "888       "888                                       
 .oooo.    .oooo888   .oooo888  oooo d8b  .ooooo.   .oooo.o  .oooo.o 
`P  )88b  d88' `888  d88' `888  `888""8P d88' `88b d88(  "8 d88(  "8 
 .oP"888  888   888  888   888   888     888ooo888 `"Y88b.  `"Y88b.  
d8(  888  888   888  888   888   888     888    .o o.  )88b o.  )88b 
`Y888""8o `Y8bod88P" `Y8bod88P" d888b    `Y8bod8P' 8""888P' 8""888P' 

             .o8                           oooo        
            "888                           `888        
             888oooo.   .ooooo.   .ooooo.   888  oooo  
             d88' `88b d88' `88b d88' `88b  888 .8P'   
             888   888 888   888 888   888  888888.    
             888   888 888   888 888   888  888 `88b.  
             `Y8bod8P' `Y8bod8P' `Y8bod8P' o888o o888o 
"""


FILE_PATH = Path.home() / "orgApp" / "address_book.json"  # for working on different filesystems
FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

def command_parser(user_input: str) -> tuple[callable, str]:
    """
    Parse user input to determine the corresponding command and data.
    This function parses the user's input to identify the command they want to
    execute and the associated data, if any..
    """
    if not user_input:
        raise IndexError("Nothing was entered ...")
    func, data = None, []
    lower_input_end_spaced = user_input.lower() + ' '
    for command, aliases in COMMANDS.items():
        for alias in aliases:
            if lower_input_end_spaced.startswith(alias + ' '):
                func = globals()[f'handle_{command}']
                data = user_input[len(alias) + 1:].strip()
                break
        if func:
            break
    if not func:
        raise ValueError(f"There is no such command {user_input.split()[0]}")
    return func, data


def handle_add_record(arg: str, address_book: AddressBook, viewer: UserView) -> Union[str, bool, None, Record]:
    """
    Command handler for 'add' command. Adds a new contact to the address book.
    """
    name = viewer.get_data_input("Enter name:")
    if not Name(name).validate(name):
        viewer.display_error_message("Invalid name. Please use only letters and more than one.")
        return 'Was entered invalid name'
    if name.lower().strip() in [record.name.value.lower().strip() for record in address_book.data.values()]:
        viewer.display_error_message("A contact with that name already exists!!!")
        return 'Already exists'

    new_record = Record(name)

    phone = viewer.get_data_input("Enter the phone number (+380________):")
    if not phone:
        viewer.display_message('The phone was not entered')
    elif Phone(phone).validate(phone):
        new_record.phones = [Phone(phone)]
    else:
        viewer.display_error_message("Invalid phone")

    email = viewer.get_data_input("Enter an email in an acceptable format:")
    if not email:
        viewer.display_message('The email was not entered')
    elif Email(email).validate(email):
        new_record.email = Email(email)
    else:
        viewer.display_error_message("Invalid email")

    birthday = viewer.get_data_input("Enter birthday in the format(dd.mm.yyyy):")
    if not birthday:
        viewer.display_message('The birthday was not entered')
    elif Birthday(birthday).validate(birthday):
        new_record.birthday = Birthday(birthday)
    else:
        viewer.display_error_message("Invalid birthday")

    if address_book.add_record(new_record):
        viewer.display_contacts(address_book.get_all_records())
        viewer.display_message(f"The contact {new_record.name} has been successfully added to the address book.")
        return 'The process is finished'
    else:
        viewer.display_message("The data is not valid")
        return None

def validate_and_get_contact_by_name(address_book: AddressBook, viewer: UserView) -> Union[bool, None, Record]:
    """
    Checks the presence and validity of a contact by name.
    Returns the contact found or False if the contact is not found or is invalid.
    """
    name = viewer.get_data_input("Enter name:")
    if not Name(name).validate(name):
        viewer.display_error_message("Invalid name. Please use only letters and more than one.")
        return False
    contact = address_book.get_record_by_name(name)
    if contact is None:
        viewer.display_message(f"The contact with the name {name} was not found in the address book.")
        return None
    return contact


def handle_add_phone_number(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'add_phone' command. Adds phone
    to a contact in the address book.
    """
    contact = validate_and_get_contact_by_name(address_book, viewer)
    if not contact:
        return 'The is no contact'
    new_phone = viewer.get_data_input("Enter phone in an acceptable format:")
    if not Phone(new_phone).validate(new_phone):
        viewer.display_error_message("The phone is not valid.")
        return 'Was entered invalid phone'
    if new_phone in [record.value for record in contact.phones]:
        viewer.display_error_message(f"The phone {new_phone} has already existed.")
        return 'Was entered phone which existed'
    contact.add_phone_number(new_phone)
    viewer.display_contacts(address_book.get_all_records())
    viewer.display_message("Phone number successfully added.")
    return "Finished when added phone."


def handle_add_email(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'add_email' command. Adds an email
    address to a contact in the address book.
    """
    contact = validate_and_get_contact_by_name(address_book, viewer)
    if not contact:
        return 'The is no contact'
    if contact.email:
        viewer.display_message(f"The contact already has email.")
        return 'An email was entered, but the contact already has one.'
    email = viewer.get_data_input("Enter email in an acceptable format:")
    if not Email(email).validate(email):
        viewer.display_error_message("The email is not valid.")
        return 'Was entered invalid email'
    contact.add_email(email)
    viewer.display_contacts(address_book.get_all_records())
    viewer.display_message(f"Email {email} added successfully")
    return f"Finished when added email"


def handle_change_phone_number(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'change_phone' command. Changes the phone number of a contact.
    """
    contact = validate_and_get_contact_by_name(address_book, viewer)
    if not contact:
        return 'The is no contact'
    if not contact.phones:
        viewer.display_message(f"The contact {contact.name.value} does not have phone.")
        return 'Was entered phone, but contact have not phone number'

    old_phone = viewer.get_data_input("Enter old phone in an acceptable format:")
    if not Phone(old_phone).validate(old_phone):
        viewer.display_error_message("The old_phone is not valid.")
        return 'Was entered old invalid phone'
    if old_phone not in [record.value for record in contact.phones]:
        viewer.display_error_message(f"The phone {old_phone} does not exist in {contact.name.value}.")
        return 'Was entered phone, but contact have not it'

    new_phone = viewer.get_data_input("Enter new_phone in an acceptable format:")
    if not Phone(new_phone).validate(new_phone):
        viewer.display_error_message("The new_phone was not entered or it is not valid.")
        return 'Was entered new invalid phone'
    elif new_phone in [record.value for record in contact.phones]:
        viewer.display_error_message(f"The new_phone {new_phone} is already exist.")
        return 'Was entered phone, but the new phone matches the old one'
    else:
        contact.change_phone_number(old_phone, new_phone)
        viewer.display_contacts(address_book.get_all_records())
        viewer.display_message(f'The phone has been successfully changed from {old_phone} to {new_phone}.')
    return "Finished when changed phone"


def handle_change_email(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'change_email' command. Changes the email address of a contact.
    """
    contact = validate_and_get_contact_by_name(address_book, viewer)
    if not contact:
        return 'The is no contact'
    if not contact.email:
        viewer.display_message(f"The contact {contact.name.value} does not have email.")
        return 'Was entered email, but contact have not phone email'

    old_email = viewer.get_data_input("Enter old email in an acceptable format:")
    if not Email(old_email).validate(old_email):
        viewer.display_error_message("The old_email is not valid.")
        return 'Was entered old invalid email'
    elif old_email != contact.email.value:
        viewer.display_error_message(f"The email {old_email} does not exist.")
        return 'Was entered old email, but it does not exist'

    new_email = viewer.get_data_input("Enter new email in an acceptable format:")
    if not Email(new_email).validate(new_email):
        viewer.display_error_message("The new email is not valid.")
        return 'Was entered new invalid email'
    contact.change_email(old_email, new_email)
    viewer.display_contacts(address_book.get_all_records())
    viewer.display_message(f"The email has been successfully changed from {old_email} to {new_email}.")
    return "Finished when changed email"

def handle_remove_phone_number(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'remove_phone' command. Removes a phone
    number from a contact in the address book.
    """
    contact = validate_and_get_contact_by_name(address_book, viewer)
    if not contact:
        return 'The is no contact'
    if not contact.phones:
        viewer.display_message(f"The contact {contact.name.value} does not have phone.")
        return 'Was entered phone, but contact have not phone number'

    phone_to_remove = viewer.get_data_input("Enter phone in an acceptable format:")
    if not Phone(phone_to_remove).validate(phone_to_remove):
        viewer.display_error_message("The phone is not valid.")
        return 'Was entered invalid phone'
    if phone_to_remove not in [record.value for record in contact.phones]:
        viewer.display_error_message(f"The phone {phone_to_remove} does not exist.")
        return 'Was entered phone, but it does not exist'
    contact.remove_phone_number(phone_to_remove)
    viewer.display_contacts(address_book.get_all_records())
    viewer.display_message(f"The phone number {phone_to_remove} has been successfully deleted.")
    return "Finished when removed phone"


def handle_remove_email(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'remove_email' command. Removes an email
    address from a contact in the address book.
    """
    contact = validate_and_get_contact_by_name(address_book, viewer)
    if not contact:
        return 'The is no contact'
    if not contact.email:
        viewer.display_message(f"The contact {contact.name.value} does not have email.")
        return 'Was entered email, but contact have not email'

    email_to_remove = viewer.get_data_input("Enter email in an acceptable format:")
    if not Email(email_to_remove).validate(email_to_remove):
        viewer.display_error_message("The email is not valid.")
        return 'Was entered invalid email'
    elif email_to_remove != contact.email.value:
        viewer.display_error_message(f"The email {email_to_remove} does not exist in contact {contact.name.value}.")
        return 'Was entered email, but it does not exist'
    contact.remove_email(email_to_remove)
    viewer.display_contacts(address_book.get_all_records())
    viewer.display_message(f"The email {email_to_remove} has been successfully deleted.")
    return "Finished when removed email"


def handle_remove_record(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'remove' command. Removes a contact from
    the address book.
    """
    contact = validate_and_get_contact_by_name(address_book, viewer)
    if not contact:
        return 'The is no contact'
    name=contact.name.value
    if address_book.remove_record(name):
        viewer.display_contacts(address_book.get_all_records())
        viewer.display_message(f"Contact {name} has been successfully removed from the address book.")
        return "Finished when removed contact"

def handle_find_records(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'find' command. Searches for contacts
    in the address book based on user-specified criteria.
    """
    search_criteria = {}
    viewer.display_message("What criteria would you like to search by?\n1. Search by name\n2. Search by phone number.")
    search_option = viewer.get_data_input("Select an option (1 or 2): ")
    if search_option == "1":
        search_name = viewer.get_data_input("Enter a name to search for (minimum 2 characters): ").strip().lower()
        if len(search_name) >= 2:
            search_criteria['name'] = search_name
        else:
            viewer.display_error_message("You entered too few characters for the name. Name search canceled.")
            return 'Failed when entered characters for the name!!!'
    elif search_option == "2":
        search_phones = viewer.get_data_input("Please enter a part of the phone number for the search (minimum 5 characters): ").strip()
        if len(search_phones) >= 5:
            search_criteria['phones'] = search_phones
        else:
            viewer.display_error_message("You entered too few characters for a phone number. Phone number search canceled.")
            return 'Failed when entered characters for a phone number!!!'
    else:
        viewer.display_error_message("Invalid option selected.")
        return 'Failed option selected!!!'
    results = address_book.find_records(**search_criteria)
    if results:
        find = ', '.join([record.name.value for record in results])
        viewer.display_message(f"Search results: {find}")
        return 'Finish!!!'
    else:
        viewer.display_error_message("The contact meeting the specified criteria was not found.")
        return 'Failed!!!'


def handle_get_all_records(arg: str, address_book, viewer: UserView) -> str:
    """
    Command handler for 'all' command. Retrieves and
    returns None.
    """
    viewer.display_contacts(address_book.get_all_records())
    return 'Found!!!'


def handle_days_to_birthday(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
     Command handler for 'when_birthday' command. Calculates the
     days until the birthday of a contact
    """
    contact = validate_and_get_contact_by_name(address_book, viewer)
    if not contact:
        return 'The is no contact'
    if contact.birthday:
        days = contact.days_to_birthday()
        viewer.display_message(f"Name {contact.name.value} has {days} days left until their birthday.")
        return 'Found'
    else:
        return viewer.display_message(f"The contact {contact.name.value} does not have a birthdate specified.")


def handle_get_birthdays_per_week(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'get_list' command. Retrieves birthdays
    for the specified number of days ahead.
    """
    num_str = viewer.get_data_input("Enter the number of days: ")
    if num_str.isdigit():
        num_days = int(num_str)
        birthdays_list = address_book.get_birthdays_per_week(num_days)
        if birthdays_list:
            viewer.display_message("\n".join(birthdays_list))
            return 'Found'
        else:
            viewer.display_message("No birthdays today.")
            return 'Not founded'
    else:
        viewer.display_error_message('Not a number')
        return 'Failed'

def handle_load_from_file(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'load_from_file' command. Loads the address
    book data from a file.
    """
    arg = arg.strip()
    if arg and (not Path(arg).exists() or not Path(arg).is_file()):
        return viewer.display_message(f"The file path does not exist")
    arg = arg if arg else str(FILE_PATH)
    file_handler = AddressBookFileHandler(arg)
    loaded_address_book = file_handler.load_from_file()
    address_book.data.update(loaded_address_book.data)
    return viewer.display_message(f"The address book is loaded from a file {arg}")

def handle_save_to_file(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """
    Command handler for 'save' command. Saves the address
    book data to a file.
    """
    FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_handler = AddressBookFileHandler(str(FILE_PATH))
    file_handler.save_to_file(address_book)
    return viewer.display_message(f"The address book has been saved at the following path {str(FILE_PATH)}")


def handle_exit(arg: str, address_book: AddressBook, viewer: UserView) -> bool:
    """
    Command handler for 'exit' command. Exits the address book application.
    """
    handle_save_to_file(arg, address_book, viewer)
    return False


def handle_help(arg: str, address_book: AddressBook, viewer: UserView) -> str:
    """Outputs the command menu"""
    viewer.display_commands()
    return 'Help'

def input_error(func):
    """
    A decorator wrapper for error handling.

    Args:
        func (callable): The function to wrap with error handling.

    Returns:
        callable: The wrapped function with error handling.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except IndexError as e:
            print(Fore.RED, 'Not enough data.', str(e))
        except ValueError as e:
            print(Fore.RED, 'Wrong value.', str(e))
        except KeyError as e:
            print(Fore.RED, 'Wrong key.', str(e)[1:-1])
        except TypeError as e:
            print(Fore.RED, 'Wrong type of value.', str(e))
        except FileNotFoundError as e:
            print(Fore.RED, e)
        except Exception as e:
            print(Fore.RED, e)
    return wrapper

@input_error
def main_cycle(address_book: AddressBook, viewer: UserView) -> bool:
    """
    Return True if it needs to stop the program. False otherwise.
    """
    user_input = viewer.get_user_input()
    func, argument = command_parser(user_input)
    result = func(argument, address_book, viewer)
    return result

def prepare() -> UserView:
    """
    Prints initial information to the user and returns
    the chosen viewer mode.
    """
    init_colorama()
    print(Fore.BLUE + Style.BRIGHT + ADDRESSBOOK_LOGO)
    print(Fore.CYAN + "Welcome to your ADDRESS BOOK!")
    print()

    print("Choose how to show commands in the console or on the screen:")
    print("1 - Console")
    print("2 - Screen")
    mode = input("Enter your choice (1/2): ").strip()
    if mode == '1':
        viewer = ConsoleUserView()
    elif mode == '2':
        viewer = GuiUserView()
    else:
        print("Invalid choice. Defaulting to Console mode.")
        viewer = ConsoleUserView()
    viewer.display_commands()
    return viewer

def main():
    """
    Main entry point for the address book program.
    This function initializes the address book, prepares
    the environment, and enters the main program loop.
    """
    address_book = AddressBook()
    viewer = prepare()
    print(handle_load_from_file('', address_book, viewer))

    while True:
        if not main_cycle(address_book, viewer):
            break


if __name__ == '__main__':
    main()