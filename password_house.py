import random
import string
import hashlib
import os
from cryptography.fernet import Fernet
from colorama import init, Fore, Style
import pyfiglet
from datetime import datetime, timedelta
import base64
import time
import getpass

# Initialize colorama
init(autoreset=True)

# Function to generate a Fernet key from the master password
def generate_fernet_key_from_password(master_password):
    hash_value = hashlib.sha256(master_password.encode()).digest()
    key = base64.urlsafe_b64encode(hash_value)  # This will give us 32 bytes
    return key

# Password generation function
def generate_password(domain, username, length=12, use_upper=True, use_lower=True, use_digits=True, use_special=True):
    char_sets = []
    if use_upper:
        char_sets.append(string.ascii_uppercase)
    if use_lower:
        char_sets.append(string.ascii_lowercase)
    if use_digits:
        char_sets.append(string.digits)
    if use_special:
        char_sets.append(string.punctuation)

    all_chars = ''.join(char_sets)
    
    password = ''.join(random.choice(all_chars) for _ in range(length))
    
    # Add random character for enhanced security
    password = list(password)
    password[random.randint(0, length-1)] = random.choice(string.punctuation + string.digits)
    random.shuffle(password)
    
    return ''.join(password)

# Encrypt password data with Fernet
def encrypt_password_data(password, key):
    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password.encode())
    return encrypted_password

# Decrypt password data with Fernet
def decrypt_password_data(encrypted_password, key):
    cipher = Fernet(key)
    decrypted_password = cipher.decrypt(encrypted_password).decode()
    return decrypted_password

# Hash the master password for storage
def hash_master_password(master_password):
    return hashlib.sha256(master_password.encode()).hexdigest()

# User login system
def login_system():
    while True:
        print(Fore.YELLOW + "Login or Register:")
        print(Fore.CYAN + "1. Login")
        print(Fore.CYAN + "2. Register")
        print(Fore.RED + "3. Exit")
        action = input(Fore.MAGENTA + "Choose an option (1/2/3): ").strip()

        if action == '1':
            return login_user()
        elif action == '2':
            return register_user()
        elif action == '3':
            print(Fore.GREEN + "Exiting the program.")
            exit()
        else:
            print(Fore.RED + "Invalid action. Please choose again.")

# Registration function for new user
def register_user():
    while True:
        username = input(Fore.GREEN + "Enter your desired username: ").strip()

        # Ensure the user directory exists
        if not os.path.exists('users'):
            os.mkdir('users')
        
        # Check if username exists
        if os.path.exists(f"users/{username}.txt"):
            print(Fore.RED + "Username already exists. Try a different one.")
            continue
        
        master_password = getpass.getpass(Fore.GREEN + "Set your master password: ").strip()
        master_password_hash = hash_master_password(master_password)
        
        # Store the new user credentials in an encrypted file
        key = generate_fernet_key_from_password(master_password)  # Encryption key
        encrypted_master_password = encrypt_password_data(master_password, key)

        with open(f"users/{username}.txt", "wb") as file:
            file.write(encrypted_master_password)

        print(Fore.GREEN + f"User {username} successfully registered.")
        return username, master_password

# Login function for existing users
def login_user():
    while True:
        username = input(Fore.GREEN + "Enter your username: ").strip()

        if not os.path.exists(f"users/{username}.txt"):
            print(Fore.RED + "Username does not exist. Please try again.")
            continue

        master_password = getpass.getpass(Fore.GREEN + "Enter your master password: ").strip()
        
        # Read the stored encrypted master password
        with open(f"users/{username}.txt", "rb") as file:
            encrypted_master_password = file.read()

        # Decrypt the stored master password
        key = generate_fernet_key_from_password(master_password)
        try:
            decrypted_master_password = decrypt_password_data(encrypted_master_password, key)
        except Exception as e:
            print(Fore.RED + "Incorrect password. Please try again.")
            continue
        
        if decrypted_master_password == master_password:
            print(Fore.GREEN + f"Login successful for {username}.")
            return username, master_password
        else:
            print(Fore.RED + "Incorrect password. Please try again.")

# Store encrypted password data with username
def store_password(domain, username, password, master_password):
    key = generate_fernet_key_from_password(master_password)  # Generate key from master password
    encrypted_password = encrypt_password_data(password, key)
    
    password_data = {
        'domain': domain,
        'username': username,
        'password': encrypted_password,
        'expiry_date': (datetime.now() + timedelta(days=90)).isoformat()  # Password expiry in 90 days
    }

    if not os.path.exists('passwords'):
        os.mkdir('passwords')

    with open(f"passwords/{domain}_{username}.txt", "wb") as file:
        file.write(encrypted_password)

    print(Fore.GREEN + f"Password for {domain} stored securely.")

# Retrieve all passwords and display the username along with the domain and password
def retrieve_all_passwords(master_password):
    if not os.path.exists('passwords'):
        print(Fore.RED + "No passwords stored yet.")
        return
    
    key = generate_fernet_key_from_password(master_password)  # Generate key from master password
    print(Fore.CYAN + "Displaying all stored passwords:")
    
    for password_file in os.listdir('passwords'):
        if password_file.endswith(".txt"):
            domain_username = password_file.replace(".txt", "")
            domain, username = domain_username.split("_")  # Extract domain and username from the filename
            
            with open(f"passwords/{password_file}", "rb") as file:
                encrypted_password = file.read()
            
            decrypted_password = decrypt_password_data(encrypted_password, key)
            print(Fore.GREEN + f"Domain: {domain}, Username: {username}, Password: {decrypted_password}")

# Password Strength Checker (using blocks instead of stars)
def check_password_strength(password):
    strength = 0
    if len(password) >= 8:
        strength += 1
    if any(char.isdigit() for char in password):
        strength += 1
    if any(char.isupper() for char in password):
        strength += 1
    if any(char.islower() for char in password):
        strength += 1
    if any(char in string.punctuation for char in password):
        strength += 1

    # Graphical representation using blocks
    strength_graph = '█' * strength
    max_strength = 5
    bar = f"[{strength_graph:<{max_strength}}] {strength}/{max_strength}"

    if strength == max_strength:
        color = Fore.GREEN
    elif strength >= 3:
        color = Fore.YELLOW
    else:
        color = Fore.RED
    
    return color + bar

# Display the welcome screen with ASCII art
def display_welcome():
    ascii_banner = pyfiglet.figlet_format("Password House")
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLUE]

    # Display the banner with color animation effect (only once)
    for _ in range(4):  # Change colors 4 times to simulate animation
        color = random.choice(colors)
        print(color + ascii_banner)
        time.sleep(0.3)
        os.system('clear')  # Clears the terminal screen

    # Final banner
    print(Fore.YELLOW + ascii_banner)
    print(Fore.CYAN + "Your secure password manager.")

# Logout function
def logout():
    print(Fore.YELLOW + "\nYou have been logged out.")
    return login_system()

# Main function
def main():
    display_welcome()

    # Login or Register user
    user_credentials = login_system()
    if user_credentials is None:
        return

    username, master_password = user_credentials

    # Option to generate a new password, update, retrieve, or delete passwords
    while True:
        print(Fore.CYAN + "\nChoose an option:")
        print(Fore.YELLOW + "1. Generate a new password")
        print(Fore.YELLOW + "2. Check the strength of a password")
        print(Fore.YELLOW + "3. Retrieve a stored password")
        print(Fore.YELLOW + "4. Display all passwords")
        print(Fore.RED + "5. Logout")
        print(Fore.RED + "6. Exit")
        
        action = input(Fore.MAGENTA + "Choose an option (1/2/3/4/5/6): ").strip()
        
        if action == '1':
            domain = input(Fore.GREEN + "Enter the domain (e.g., example.com): ").strip()
            username_input = input(Fore.GREEN + "Enter the username: ").strip()
            password_length = int(input(Fore.GREEN + "Enter the desired password length (default 12): ").strip() or 12)
            use_upper = input(Fore.GREEN + "Use uppercase letters? (y/n): ").strip().lower() == 'y'
            use_lower = input(Fore.GREEN + "Use lowercase letters? (y/n): ").strip().lower() == 'y'
            use_digits = input(Fore.GREEN + "Use digits? (y/n): ").strip().lower() == 'y'
            use_special = input(Fore.GREEN + "Use special characters? (y/n): ").strip().lower() == 'y'
            
            password = generate_password(domain, username_input, password_length, use_upper, use_lower, use_digits, use_special)
            print(Fore.GREEN + f"Generated password: {password}")
            print(check_password_strength(password))  # Display strength
            store_password(domain, username_input, password, master_password)
        elif action == '2':
            user_password = getpass.getpass(Fore.CYAN + "Enter password to check strength: ")
            print(check_password_strength(user_password))
        elif action == '3':
            retrieve_all_passwords(master_password)
        elif action == '4':
            retrieve_all_passwords(master_password)
        elif action == '5':
            logout()
        elif action == '6':
            print(Fore.GREEN + "Exiting...")
            break
        else:
            print(Fore.RED + "Invalid choice. Please try again.")

# Run the main program
if __name__ == "__main__":
    main()
