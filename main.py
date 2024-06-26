import tkinter as tk
from tkinter import messagebox, simpledialog, Text
import mysql.connector
import uuid
import re

# Database connection
def db_connect():
    return mysql.connector.connect(
        host="localhost",
        user="yourusername", # root by default
        password="yourpassword",  
        database="note_taking_app"
    )

# Helper functions
def generate_unique_id():
    return str(uuid.uuid4())

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# User registration
def register_user(username, password, email):
    if not is_valid_email(email):
        messagebox.showerror("Error", "Invalid email address")
        return

    conn = db_connect()
    cursor = conn.cursor()

    unique_id = generate_unique_id()
    try:
        cursor.execute("INSERT INTO users (unique_id, username, password, email) VALUES (%s, %s, %s, %s)",
                       (unique_id, username, password, email))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful! Your unique ID is: " + unique_id)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

        # Open login screen after successful registration
        app.create_login_screen()

# User login
def login_user(username, password):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Password reset
def reset_password(username, email, new_password):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=%s WHERE username=%s AND email=%s", (new_password, username, email))
    conn.commit()
    cursor.close()
    conn.close()

# Notes operations
def add_note(user_id, title, content):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (user_id, title, content) VALUES (%s, %s, %s)", (user_id, title, content))
    conn.commit()
    cursor.close()
    conn.close()

def get_notes(user_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM notes WHERE user_id=%s", (user_id,))
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return notes

def update_note(note_id, title, content):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE notes SET title=%s, content=%s WHERE id=%s", (title, content, note_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_note(note_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id=%s", (note_id,))
    conn.commit()
    cursor.close()
    conn.close()

# GUI Setup
class NoteTakingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Note Taking App")
        self.root.geometry("800x600")
        self.current_user_id = None
        self.current_note_id = None
        self.title_entry = None
        self.content_text = None
        self.font_size = 14
        self.is_bold = False
        self.is_italic = False

        self.create_main_screen()

    def create_main_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Welcome to the Note Taking App", font=("Arial", 24)).pack(pady=20)

        tk.Button(self.root, text="Register", command=self.create_register_screen, bg="#4CAF50", fg="white", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Login", command=self.create_login_screen, bg="#2196F3", fg="white", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Reset Password", command=self.create_reset_password_screen, bg="#FFC107", fg="white", font=("Arial", 16)).pack(pady=10)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_register_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Register", font=("Arial", 24)).pack(pady=20)

        tk.Label(self.root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Label(self.root, text="Email").pack(pady=5)
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Button(self.root, text="Register", command=self.register_action, bg="#4CAF50", fg="white", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.create_main_screen, bg="#9E9E9E", fg="white", font=("Arial", 16)).pack(pady=10)

    def register_action(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()

        if not is_valid_email(email):
            messagebox.showerror("Error", "Invalid email address")
            return

        conn = db_connect()
        cursor = conn.cursor()

        unique_id = generate_unique_id()
        try:
            cursor.execute("INSERT INTO users (unique_id, username, password, email) VALUES (%s, %s, %s, %s)",
                           (unique_id, username, password, email))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! Your unique ID is: " + unique_id)
            self.create_login_screen()  # Open login screen after successful registration
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def create_login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Login", font=("Arial", 24)).pack(pady=20)

        tk.Label(self.root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        def login():
            username = self.username_entry.get()
            password = self.password_entry.get()
            user = login_user(username, password)
            if user:
                self.current_user_id = user[0]
                self.create_notes_screen()
            else:
                messagebox.showerror("Error", "Invalid username or password")

        tk.Button(self.root, text="Login", command=login, bg="#2196F3", fg="white", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.create_main_screen, bg="#9E9E9E", fg="white", font=("Arial", 16)).pack(pady=10)

    def create_reset_password_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Reset Password", font=("Arial", 24)).pack(pady=20)

        tk.Label(self.root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Email").pack(pady=5)
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Label(self.root, text="New Password").pack(pady=5)
        self.new_password_entry = tk.Entry(self.root, show="*")
        self.new_password_entry.pack()

        def reset_password_action():
            username = self.username_entry.get()
            email = self.email_entry.get()
            new_password = self.new_password_entry.get()
            if username and email and new_password:
                reset_password(username, email, new_password)
                self.create_login_screen()
            else:
                messagebox.showerror("Error", "All fields are required")

        tk.Button(self.root, text="Reset Password", command=reset_password_action, bg="#FFC107", fg="white", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.create_main_screen, bg="#9E9E9E", fg="white", font=("Arial", 16)).pack(pady=10)

    def create_notes_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Your Notes", font=("Arial", 24)).pack(pady=20)

        notes = get_notes(self.current_user_id)
        for note in notes:
            note_frame = tk.Frame(self.root, relief="ridge", borderwidth=2)
            note_frame.pack(pady=5, padx=10, fill="x")
            tk.Label(note_frame, text=note[1], font=("Arial", 16)).pack(pady=5, padx=5)
            tk.Label(note_frame, text=note[2], font=("Arial", 14), wraplength=500).pack(pady=5, padx=5)
            tk.Button(note_frame, text="Edit", command=lambda n=note: self.edit_note_screen(n), bg="#2196F3", fg="white", font=("Arial", 14)).pack(side="left", padx=5, pady=5)
            tk.Button(note_frame, text="Delete", command=lambda n=note: self.delete_note_action(n), bg="#f44336", fg="white", font=("Arial", 14)).pack(side="right", padx=5, pady=5)

        tk.Button(self.root, text="Add Note", command=self.add_note_screen, bg="#4CAF50", fg="white", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Logout", command=self.create_main_screen, bg="#9E9E9E", fg="white", font=("Arial", 16)).pack(pady=10)

    def add_note_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Add Note", font=("Arial", 24)).pack(pady=20)

        tk.Label(self.root, text="Title").pack(pady=5)
        self.title_entry = tk.Entry(self.root, width=50)
        self.title_entry.pack()

        tk.Label(self.root, text="Content").pack(pady=5)
        self.content_text = Text(self.root, wrap="word", width=60, height=15)
        self.content_text.pack()

        font_options_frame = tk.Frame(self.root)
        font_options_frame.pack(pady=10)

        tk.Button(font_options_frame, text="Increase Font Size", command=self.increase_font_size, bg="#9E9E9E", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(font_options_frame, text="Decrease Font Size", command=self.decrease_font_size, bg="#9E9E9E", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(font_options_frame, text="Bold", command=self.toggle_bold, bg="#9E9E9E", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(font_options_frame, text="Italic", command=self.toggle_italic, bg="#9E9E9E", fg="white", font=("Arial", 12)).pack(side="left", padx=5)

        tk.Button(self.root, text="Add Note", command=self.add_note_action, bg="#4CAF50", fg="white", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.create_notes_screen, bg="#9E9E9E", fg="white", font=("Arial", 16)).pack(pady=10)

    def increase_font_size(self):
        self.font_size += 1
        self.update_text_font()

    def decrease_font_size(self):
        if self.font_size > 1:
            self.font_size -= 1
            self.update_text_font()

    def toggle_bold(self):
        self.is_bold = not self.is_bold
        self.update_text_font()

    def toggle_italic(self):
        self.is_italic = not self.is_italic
        self.update_text_font()

    def update_text_font(self):
        font = ("Arial", self.font_size)
        if self.is_bold:
            font = ("Arial Bold", self.font_size)
        if self.is_italic:
            font = ("Arial Italic", self.font_size)

        self.content_text.config(font=font)

    def add_note_action(self):
        title = self.title_entry.get()
        content = self.content_text.get("1.0", tk.END).strip()
        if title and content:
            add_note(self.current_user_id, title, content)
            self.create_notes_screen()
        else:
            messagebox.showerror("Error", "All fields are required")

    def edit_note_screen(self, note):
        self.clear_screen()

        tk.Label(self.root, text="Edit Note", font=("Arial", 24)).pack(pady=20)

        tk.Label(self.root, text="Title").pack(pady=5)
        self.title_entry = tk.Entry(self.root, width=50)
        self.title_entry.insert(0, note[1])
        self.title_entry.pack()

        tk.Label(self.root, text="Content").pack(pady=5)
        self.content_text = Text(self.root, wrap="word", width=60, height=15)
        self.content_text.insert("1.0", note[2])
        self.content_text.pack()

        font_options_frame = tk.Frame(self.root)
        font_options_frame.pack(pady=10)

        tk.Button(font_options_frame, text="Increase Font Size", command=self.increase_font_size, bg="#9E9E9E", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(font_options_frame, text="Decrease Font Size", command=self.decrease_font_size, bg="#9E9E9E", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(font_options_frame, text="Bold", command=self.toggle_bold, bg="#9E9E9E", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(font_options_frame, text="Italic", command=self.toggle_italic, bg="#9E9E9E", fg="white", font=("Arial", 12)).pack(side="left", padx=5)

        tk.Button(self.root, text="Save Changes", command=lambda: self.save_changes(note), bg="#4CAF50", fg="white", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.create_notes_screen, bg="#9E9E9E", fg="white", font=("Arial", 16)).pack(pady=10)

    def save_changes(self, note):
        title = self.title_entry.get()
        content = self.content_text.get("1.0", tk.END).strip()
        if title and content:
            update_note(note[0], title, content)
            self.create_notes_screen()
        else:
            messagebox.showerror("Error", "All fields are required")

    def delete_note_action(self, note):
        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this note?")
        if confirm:
            delete_note(note[0])
            self.create_notes_screen()

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = NoteTakingApp(root)
    root.mainloop()
