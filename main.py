import sqlite3
import random
import string

DATABASE_FILE = "passwords.db"

def create_tables(connection):
    cursor = connection.cursor()

    # Create accounts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts
                      (id INTEGER PRIMARY KEY, username TEXT, password TEXT, medium TEXT)''')

    # Create master_accounts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS master_accounts
                      (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')

    connection.commit()

def create_master_account(connection):
    cursor = connection.cursor()

    # Check if there is already a master account
    cursor.execute("SELECT COUNT(*) FROM master_accounts")
    count = cursor.fetchone()[0]

    if count == 0:
        # Prompt for master account creation
        master_username = input("Enter the master account username: ")
        master_password = input("Enter the master account password: ")

        # Save master account information
        cursor.execute("INSERT INTO master_accounts (username, password) VALUES (?, ?)",
                       (master_username, master_password))
        connection.commit()
        print("Master account created successfully.")
    else:
        print("Master account already exists.")

def authenticate_master_account(connection):
    cursor = connection.cursor()

    while True:
        username = input("Enter master account username: ")
        password = input("Enter master account password: ")

        cursor.execute("SELECT COUNT(*) FROM master_accounts WHERE username = ? AND password = ?", (username, password))
        count = cursor.fetchone()[0]

        if count > 0:
            print("Authentication successful.")
            break
        else:
            print("Authentication failed. Please try again.")

def generate_password(length=12, uppercase=True, digits=True, special_characters=True):
    characters = string.ascii_lowercase
    if uppercase:
        characters += string.ascii_uppercase
    if digits:
        characters += string.digits
    if special_characters:
        characters += string.punctuation

    if length < 1:
        raise ValueError("Password length must be at least 1")

    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def save_account(connection, username, password, medium):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO accounts (username, password, medium) VALUES (?, ?, ?)", (username, password, medium))
    connection.commit()

def load_accounts(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM accounts")
    accounts = cursor.fetchall()
    return accounts

def view_accounts(connection):
    accounts = load_accounts(connection)

    if not accounts:
        print("No accounts found.")
    else:
        print("\nStored Accounts:")
        for account in accounts:
            print(f"  ID: {account[0]}, Username: {account[1]}, Password: {account[2]}, Medium: {account[3]}")

def generate_random_password():
    password = generate_password()
    print(f"\nGenerated Random Password: {password}")
    return password

def welcome_message():
    welcome_art = """
\033[91m
 _______     _       ______    ______   ______        _       ______   ______   ____  ____  
|_   __ \   / \    .' ____ \ .' ____ \ |_   _ `.     / \     |_   _ `.|_   _ `.|_  _||_  _| 
  | |__) | / _ \   | (___ \_|| (___ \_|  | | `. \   / _ \      | | `. \ | | `. \ \ \  / /   
  |  ___/ / ___ \   _.____`.  _.____`.   | |  | |  / ___ \     | |  | | | |  | |  \ \/ /    
 _| |_  _/ /   \ \_| \____) || \____) | _| |_.' /_/ /   \ \_  _| |_.' /_| |_.' /  _|  |_    
|_____||____| |____|\______.' \______.'|______.'|____| |____||______.'|______.'  |______|   

\033[0m
    """
    print(welcome_art)

def print_menu():
    border = "+" + "-"*30 + "+"
    menu = f"""
--------------------------------
|           Menu:              |
| 1. Generate Password         |
|    and Save Account          |
| 2. Generate Random Password  |
|    (not saved)               |
| 3. View Accounts             |
| 4. Exit                      |
--------------------------------
    """
    print(menu)

def main():
    connection = sqlite3.connect(DATABASE_FILE)
    create_tables(connection)
    create_master_account(connection)
    welcome_message()

    # Authenticate master account before allowing access
    authenticate_master_account(connection)

    while True:

        print_menu()

        choice = input("Enter your choice (1, 2, 3, or 4): ")

        if choice == '1':
            username = input("\nEnter the username for the account: ")
            medium = input("Enter the medium (e.g., Facebook, Instagram): ")
            password = generate_password()
            save_account(connection, username, password, medium)
            print(f"\nGenerated and Saved Account:\n  Username: {username}, Password: {password}, Medium: {medium}")
        elif choice == '2':
            generate_random_password()
        elif choice == '3':
            view_accounts(connection)
        elif choice == '4':
            print("\nExiting program.")
            connection.close()
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, 3, or 4.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
