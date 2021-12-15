import tkinter as tk
import mysql.connector
import tkinter.ttk as ttk

mydb = mysql.connector.connect(host="localhost", user="root", password="")
cursor = mydb.cursor(buffered=True)

cursor.execute("CREATE DATABASE IF NOT EXISTS tododb")
cursor.execute("USE tododb")

# Create tables.
command = """CREATE TABLE IF NOT EXISTS todo_users(
        email VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        PRIMARY KEY (email)
        )"""
cursor.execute(command)
command = """CREATE TABLE IF NOT EXISTS user_items(
        itemName VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        FOREIGN KEY (email) REFERENCES todo_users(email)
        )"""
cursor.execute(command)
mydb.commit()
print("Tables created.")

# Initialize root window object.
window = tk.Tk()
window.title("Todo List")
window.iconbitmap("logo.ico")
window.resizable(False, False)


# Define Text Input class.
class TextInput:
    def __init__(self,  frame, text, height=50, focus=False, padx=40, pady=10):
        self.bg_color = "#221f1f"
        self.fg_color = "#a19a9a"

        input_frame = tk.Frame(frame, width=400, height=height, bg=self.bg_color)
        self.input_label = tk.Label(input_frame, text=text, bg=self.bg_color, fg=self.fg_color)
        self.input_field = tk.Entry(input_frame, width=40, bg=self.fg_color, fg=self.bg_color)

        if focus:
            self.input_field.focus()

        self.input_label.pack(side="left")
        self.input_field.pack(side="right")
        input_frame.pack(pady=pady, padx=padx)
        input_frame.pack_propagate(0)

    def get_input_ref(self):
        return self.input_field


# Define screens, buttons and event handlers.
class GuiWindow:
    def __init__(self, bg_color, fg_color, root):
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.root = root
        self.items = []
        self.list_vars = {}
        self.list_buttons = {}
        self.list_buttons_edit = {}

    # Methods involving MySQL.
    # Fetch all records from user_items table.
    def update_items(self):
        query = f"SELECT itemName FROM user_items WHERE email=\"{self.email}\""
        cursor.execute(query)
        self.items = [i[0] for i in cursor]
        print("Logged in user's item list:", self.items)

    # Search for itemName by keyword in user_items table.
    def search_items(self):
        search_string = "%" + self.name_field.get_input_ref().get() + "%"
        query = f"SELECT * FROM user_items WHERE email=\"{self.email}\" AND itemName LIKE\"{search_string}\""
        cursor.execute(query)
        self.items = [i[0] for i in cursor]
        print("Search string:", search_string)

        self.list_frame.destroy()
        self.item_list_window()

    # Delete item from user_items table.
    def delete_list_item(self, label):
        query = f"DELETE FROM user_items WHERE email=\"{self.email}\" AND itemName=\"{label}\""
        cursor.execute(query)
        mydb.commit()
        print("Item name of the record to be deleted:", label)

        self.update_items()
        self.list_frame.destroy()
        self.item_list_window()

    # Delete itemName in user_items table.
    def edit_item_handler(self):
        # Get value from name input field.
        name = self.name_field.get_input_ref().get()

        query = f"UPDATE user_items SET itemName=\"{name}\" WHERE email=\"{self.email}\" AND itemName=\"{self.edit_name}\""
        cursor.execute(query)
        mydb.commit()
        print(f"Updated itemName from \"{self.edit_name}\" to \"{name}\".")

        self.update_items()
        self.open_window(self.change_item_frame, self.item_list_window)

    # Insert item in user_items table.
    def add_item_handler(self):
        # Get value from name input field.
        item_name = self.name_field.get_input_ref().get()

        query = f"INSERT INTO user_items VALUES(\"{item_name}\", \"{self.email}\")"
        cursor.execute(query)
        mydb.commit()
        print(f"Inserted new record into user_items: (\"{item_name}\", \"{self.email}\")")

        self.update_items()
        self.open_window(self.change_item_frame, self.item_list_window)

    # Check if user record exists in todo_users table. 
    def log_in_handler(self):
        # Get value from user input fields.
        self.email = self.email_field.get_input_ref().get()
        password = self.password_field.get_input_ref().get()

        query = f"SELECT * FROM todo_users WHERE email=\"{self.email}\" AND password=\"{password}\""
        cursor.execute(query)

        # Return error if fields are empty.
        if not self.email or not password:
            self.warning_label["text"] = "Please fill all the fields."
            return

        print(f"Checking if user exists:\nEmail: {self.email}\nPassword: {password}")
        # Return error if user does not exist in todo_users table.
        if not cursor.rowcount:
            self.warning_label["text"] = "Username or password invalid."
            print("No record corresponding to the given email and password found.")
            return
        print("Record found.")

        self.update_items()
        self.open_window(self.form_frame, self.item_list_window)

    # Insert new user record into todo_users table.
    def register_handler(self):
        # Get value from user input fields.
        self.email = self.email_field.get_input_ref().get()
        name = self.name_field.get_input_ref().get()
        password = self.password_field.get_input_ref().get()

        if not self.email or not password or not name:
            self.warning_label["text"] = "Please fill all the fields."
            return
        try:
            query = f"INSERT INTO todo_users VALUES(\"{self.email}\", \"{name}\", \"{password}\")"
            cursor.execute(query)
            mydb.commit()
            print(f"Inserted new record into todo_users: (\"{self.email}\", \"{name}\", \"{password}\")")
            self.open_window(self.form_frame, self.item_list_window)
        except:
            self.warning_label["text"] = "Email already registered."

   # Warning text for form handling.
    def warning_text(self, frame):
        self.warning_label = tk.Label(frame, text="", fg="#f10000", bg=self.bg_color)
        self.warning_label.pack()

    # Define button widget method.
    def primary_button(self, frame, text, handler, pady=10, small=False):
        button = tk.Button(
            frame,
            text=text,
            font=("Tahoma", 8),
            command=handler,
            bg=self.fg_color,
            fg=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        if not small:
            pady = 20
            button.configure(width=10, font=("Tahoma", 12))
        button.pack(pady=pady)

    def open_window(self, initial_frame, target_frame, extra_frame=False):
        initial_frame.destroy()
        if extra_frame:
            extra_frame.destroy()
        target_frame()

    def open_edit_window(self, edit_name):
        self.edit_name = edit_name
        self.open_window(self.list_frame, lambda: self.change_item_window(2))

    # Login/Register Window
    def form_window(self, category):
        if category == 1:
            primary_text = "Log In"
            secondary_text = "Don't have an account? Register"
            handler = self.log_in_handler
            goto_category = 2
        elif category == 2:
            primary_text = "Register"
            secondary_text = "Already have an account? Log in"
            handler = self.register_handler
            goto_category = 1

        self.form_frame = tk.Frame(self.root, width=400, height=400, bg=self.bg_color)

        header = tk.Label(
            self.form_frame,
            text=primary_text,
            font=("Tahoma", 24),
            width=30, fg=self.fg_color, bg=self.bg_color
        )
        header.pack(pady=30)

        self.warning_text(self.form_frame)
        self.email_field = TextInput(self.form_frame, "Email: ", 30, focus=True)
        if category == 2:
            self.name_field = TextInput(self.form_frame, "Name: ", 30)
        self.password_field = TextInput(self.form_frame, "Password: ", 30)

        self.primary_button(self.form_frame, secondary_text, lambda: self.open_window(
            self.form_frame, lambda: self.form_window(goto_category), self.warning_label), small=True)
        self.primary_button(self.form_frame, primary_text, handler)

        self.form_frame.pack()
        self.form_frame.pack_propagate(0)

    # Edit/Add Item Window
    def change_item_window(self, category):
        if category == 1:
            primary_text = "Add Item"
            handler = self.add_item_handler
        elif category == 2:
            primary_text = "Edit Item"
            handler = self.edit_item_handler

        self.change_item_frame = tk.Frame(self.root, width=400, height=400, bg=self.bg_color)
        header = tk.Label(
            self.change_item_frame,
            text=primary_text,
            font=("Tahoma", 24),
            width=30, fg=self.fg_color, bg=self.bg_color
        )
        header.pack(pady=30)
        self.name_field = TextInput(self.change_item_frame, "Item Name: ", focus=True, padx=50, pady=40)
        self.primary_button(self.change_item_frame, "Save", handler)
        self.primary_button(self.change_item_frame, "Go back to the To-do List.", lambda: self.open_window(self.change_item_frame, self.item_list_window), small=True)

        self.change_item_frame.pack()
        self.change_item_frame.pack_propagate(0)

    # To-do List Window
    def item_list_window(self):
        self.list_frame = tk.Frame(self.root, width=400, height=400, bg=self.bg_color)
        header = tk.Label(
            self.list_frame,
            text="To-do List",
            font=("Tahoma", 24),
            width=30, fg=self.fg_color, bg=self.bg_color
        )
        header.pack(pady=10)
        self.primary_button(self.list_frame, "Add Item", lambda: self.open_window(self.list_frame, lambda: self.change_item_window(1)), pady=2, small=True)
        self.name_field = TextInput(self.list_frame, "Search: ", 30, focus=True, padx=50, pady=5)
        self.primary_button(self.list_frame, "Search", self.search_items, pady=2, small=True)

        # Create the todo list dynamically.
        self.items_frame = tk.Frame(self.list_frame, width=400, height=300, bg=self.bg_color)
        for i in self.items:
            self.list_vars[i] = tk.Frame(
                self.items_frame,
                width=400,
                height=50,
                bg=self.fg_color,
                relief=tk.GROOVE,
                borderwidth=5,
            )
            list_item_text = tk.Label(self.list_vars[i], text=i, bg=self.fg_color, fg=self.bg_color)
            self.list_buttons[i+"_button"] = tk.Button(
                self.list_vars[i],
                text="X",
                bg="#f10000",
                fg="#ffffff",
                width=2,
                command=lambda i=i: self.delete_list_item(i)
            )
            self.list_buttons_edit[i+"_button_edit"] = tk.Button(
                self.list_vars[i],
                text="E",
                bg="#00b86b",
                fg="#ffffff",
                width=2,
                command=lambda i=i: self.open_edit_window(i)
            )

            list_item_text.pack(side="left", padx=10)
            self.list_buttons_edit[i + "_button_edit"].pack(side="right", padx=10)
            self.list_buttons[i+"_button"].pack(side="right", padx=10)
            self.list_vars[i].pack(padx=40)
            self.list_vars[i].pack_propagate(0)

        self.items_frame.pack(pady=10)
        self.list_frame.pack()
        self.list_frame.pack_propagate(0)


# Initialize an object of the class GuiWindow.
windows = GuiWindow("#221f1f", "#a19a9a", window)
# Display login window.
windows.form_window(1)
window.mainloop()
