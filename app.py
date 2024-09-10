import sqlite3
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox, simpledialog

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_manager (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# --- Key Management ---
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    with open("key.key", "rb") as key_file:
        return key_file.read()

# --- Encryption & Decryption ---
def encrypt_password(plain_password, key):
    fernet = Fernet(key)
    return fernet.encrypt(plain_password.encode())

def decrypt_password(encrypted_password, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password).decode()

# --- Password Manager Operations ---
def add_password(service, username, password):
    key = load_key()
    encrypted_password = encrypt_password(password, key)

    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO password_manager (service, username, password) 
        VALUES (?, ?, ?)
    """, (service, username, encrypted_password))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Password added successfully!")

def get_password(service):
    key = load_key()

    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM password_manager WHERE service=?", (service,))
    result = cursor.fetchone()
    conn.close()

    if result:
        username, encrypted_password = result
        password = decrypt_password(encrypted_password, key)
        return username, password
    else:
        return None

# --- GUI Setup ---
class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")

        # Service label and entry
        self.service_label = tk.Label(root, text="Service:")
        self.service_label.grid(row=0, column=0, padx=10, pady=10)
        self.service_entry = tk.Entry(root)
        self.service_entry.grid(row=0, column=1, padx=10, pady=10)

        # Username label and entry
        self.username_label = tk.Label(root, text="Username:")
        self.username_label.grid(row=1, column=0, padx=10, pady=10)
        self.username_entry = tk.Entry(root)
        self.username_entry.grid(row=1, column=1, padx=10, pady=10)

        # Password label and entry
        self.password_label = tk.Label(root, text="Password:")
        self.password_label.grid(row=2, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(root)
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)

        # Add button
        self.add_button = tk.Button(root, text="Add Password", command=self.add_password)
        self.add_button.grid(row=3, column=0, padx=10, pady=10)

        # Retrieve button
        self.retrieve_button = tk.Button(root, text="Retrieve Password", command=self.retrieve_password)
        self.retrieve_button.grid(row=3, column=1, padx=10, pady=10)

    def add_password(self):
        service = self.service_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if service and username and password:
            add_password(service, username, password)
        else:
            messagebox.showwarning("Input Error", "All fields are required!")

    def retrieve_password(self):
        service = self.service_entry.get()

        if service:
            result = get_password(service)
            if result:
                username, password = result
                messagebox.showinfo("Password Retrieved", f"Username: {username}\nPassword: {password}")
            else:
                messagebox.showerror("Not Found", "No password found for this service.")
        else:
            messagebox.showwarning("Input Error", "Service is required!")

# Initialize the database
init_db()

# Generate the encryption key (run this once)
#generate_key()

# Start the Tkinter application
root = tk.Tk()
app = PasswordManagerApp(root)
root.mainloop()
