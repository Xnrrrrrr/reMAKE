import secrets
import sqlite3
import string
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

DATABASE_FILE = "passwords.db"
ENCRYPTION_KEY_FILE = "encryption_key.bin"
encoded_password = None  # Declare encoded_password at the global scope
encryption_key = None

def create_tables(connection):
    cursor = connection.cursor()

    # Create accounts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts
                      (id INTEGER PRIMARY KEY, username TEXT, password TEXT, medium TEXT)''')

    # Create master_accounts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS master_accounts
                      (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')

    connection.commit()

def load_or_generate_encryption_key():
    global encryption_key

    try:
        with open(ENCRYPTION_KEY_FILE, 'rb') as key_file:
            encryption_key = key_file.read()
    except FileNotFoundError:
        # If the key file doesn't exist, generate a new key
        encryption_key = generate_strong_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as key_file:
            key_file.write(encryption_key)

def create_master_account(connection, encryption_key):
    cursor = connection.cursor()

    # Check if there is already a master account
    cursor.execute("SELECT COUNT(*) FROM master_accounts")
    count = cursor.fetchone()[0]

    if count == 0:
        # Prompt for master account creation
        master_username = input("Enter the master account username: ")
        master_password = input("Enter the master account password: ")

        # Hash and encrypt master account password
        master_password_hash = hashlib.sha256(master_password.encode()).digest()
        master_password_encrypted = encrypt_password(master_password_hash, encryption_key)

        # Save master account information
        cursor.execute("INSERT INTO master_accounts (username, password) VALUES (?, ?)",
                       (master_username, master_password_encrypted))
        connection.commit()
        print("Master account created successfully.")
    else:
        print("Master account already exists.")

def generate_strong_key():
    # Generate a strong random key (replace this with a secure key management solution)
    return secrets.token_bytes(32)

def encrypt_password(password, key):
    # Pad the password to meet block size requirements
    password = password.ljust(32)

    # Generate an IV (Initialization Vector)
    iv = b'\x00' * 16

    print(f"Encryption Key: {key}")
    print(f"Encryption IV: {iv}")

    # Create a cipher object using AES in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())

    # Encrypt the password
    encryptor = cipher.encryptor()
    encrypted_password = encryptor.update(password) + encryptor.finalize()

    # Encode the encrypted password for storage
    global encoded_password
    encoded_password = base64.b64encode(encrypted_password)
    print(f"Encrypted Password: {encoded_password}")

    return encoded_password

def authenticate_master_account(connection, encryption_key, encoded_password):
    cursor = connection.cursor()

    while True:
        print("\033[34m")  # Set text color to blue
        username = input("Enter master account username: ")
        password = input("Enter master account password: ")
        print("\033[0m")  # Reset text color to default

        password_hash = hashlib.sha256(password.encode()).digest()

        cursor.execute("SELECT password FROM master_accounts WHERE username = ?", (username,))
        encrypted_password = cursor.fetchone()

        if encrypted_password:
            decrypted_password_bytes = decrypt_and_decode_password(encrypted_password[0], encryption_key)

            print(f"Decrypted Password Bytes: {decrypted_password_bytes}")
            print(f"Entered Password Hash: {password_hash}")

            # Test against password_hash
            if password_hash == decrypted_password_bytes:
                print("Authentication successful.")
                break
            else:
                print("Authentication failed. Passwords do not match.")
        else:
            print("Authentication failed. User not found.")


def decrypt_and_decode_password(encoded_password, key):
    # Decode the encoded password
    encrypted_password = base64.b64decode(encoded_password)

    # Generate an IV (Initialization Vector)
    iv = b'\x00' * 16

    print(f"Decryption Key: {key}")
    print(f"Decryption IV: {iv}")

    # Create a cipher object using AES in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())

    # Decrypt the password
    decryptor = cipher.decryptor()
    decrypted_password = decryptor.update(encrypted_password) + decryptor.finalize()

    # Return the decrypted password as bytes
    print(f"Decrypted Password Bytes: {decrypted_password}")
    return decrypted_password

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

    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def save_account(connection, username, password, medium, encryption_key):
    cursor = connection.cursor()

    # Hash and encrypt the password before saving
    hashed_and_encrypted_password = encrypt_password(password, encryption_key)

    # Save the hashed and encrypted password in the accounts table
    cursor.execute("INSERT INTO accounts (username, password, medium) VALUES (?, ?, ?)",
                   (username, hashed_and_encrypted_password, medium))
    connection.commit()

    return hashed_and_encrypted_password

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

> Written by Xnrrrrrr
> v1.0

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
    global encryption_key
    connection = sqlite3.connect(DATABASE_FILE)
    create_tables(connection)
    load_or_generate_encryption_key()
    create_master_account(connection, encryption_key)
    welcome_message()

    # Authenticate master account before allowing access
    authenticate_master_account(connection, encryption_key, encoded_password)

    try:
        while True:
            print_menu()
            choice = input("Enter your choice (1, 2, 3, or 4): ")

            if choice == '1':
                username = input("\nEnter the username for the account: ")
                medium = input("Enter the medium (e.g., Facebook, Instagram): ")

                # Ask the user for the password
                password = input("Enter the password for the account: ")

                # Save the hashed password in the accounts table
                hashed_password = save_account(connection, username, password, medium, encryption_key)

                print(
                    f"\nGenerated and Saved Account:\n  Username: {username}, Hashed Password: {hashed_password}, Medium: {medium}")

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

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        connection.close()

if __name__ == "__main__":
    main()