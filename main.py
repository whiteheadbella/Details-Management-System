import tkinter as tk
from tkinter import messagebox, simpledialog
import pymysql

def connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',  
        database='detailsdb'
    )

# Globals
current_index = [0]
records = []
edit_mode = [False]
new_mode = [False]

def load_records():
    global records
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code, description, price FROM items ORDER BY code")
    records = cursor.fetchall()
    conn.close()

# GUI setup
window = tk.Tk()
window.title("Details Management System - MySQL (XAMPP)")
window.geometry("400x400")

code_var = tk.StringVar()
desc_var = tk.StringVar()
price_var = tk.StringVar()

tk.Label(window, text="Item Code").pack()
code_entry = tk.Entry(window, textvariable=code_var, state='readonly')
code_entry.pack()

tk.Label(window, text="Description").pack()
desc_entry = tk.Entry(window, textvariable=desc_var, state='readonly')
desc_entry.pack()

tk.Label(window, text="Price").pack()
price_entry = tk.Entry(window, textvariable=price_var, state='readonly')
price_entry.pack()

def show_record(index):
    if len(records) == 0:
        code_var.set("")
        desc_var.set("")
        price_var.set("")
    else:
        rec = records[index]
        code_var.set(rec[0])
        desc_var.set(rec[1])
        price_var.set(str(rec[2]))

def next_record():
    if len(records) == 0:
        messagebox.showwarning("Empty", "No records available.")
        return
    current_index[0] = (current_index[0] + 1) % len(records)
    show_record(current_index[0])

def previous_record():
    if len(records) == 0:
        messagebox.showwarning("Empty", "No records available.")
        return
    current_index[0] = (current_index[0] - 1) % len(records)
    show_record(current_index[0])

def search_record():
    code = simpledialog.askstring("Search", "Enter Item Code to search:")
    if not code:
        return

    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code, description, price FROM items WHERE code=%s", (code,))
    result = cursor.fetchone()
    conn.close()

    if result:
        code_var.set(result[0])
        desc_var.set(result[1])
        price_var.set(str(result[2]))
        messagebox.showinfo("Found", f"Item found:\nCode: {result[0]}\nDescription: {result[1]}\nPrice: {result[2]}")
    else:
        messagebox.showwarning("Not Found", "Item not found.")

def confirm_edit():
    desc_entry.config(state='normal')
    price_entry.config(state='normal')
    code_entry.config(state='readonly')
    edit_mode[0] = True
    new_mode[0] = False

def new_record():
    code_var.set("")
    desc_var.set("")
    price_var.set("")
    code_entry.config(state='normal')
    desc_entry.config(state='normal')
    price_entry.config(state='normal')
    new_mode[0] = True
    edit_mode[0] = False

def cancel_edit():
    desc_entry.config(state='readonly')
    price_entry.config(state='readonly')
    code_entry.config(state='readonly')
    show_record(current_index[0])
    edit_mode[0] = False
    new_mode[0] = False

def save_record():
    code = code_var.get().strip()
    desc = desc_var.get().strip()
    price = price_var.get().strip()

    if not code or not desc or not price:
        messagebox.showwarning("Error", "All fields are required.")
        return

    try:
        price_val = float(price)
    except ValueError:
        messagebox.showwarning("Error", "Price must be a number.")
        return

    conn = connection()
    cursor = conn.cursor()

    if new_mode[0]:
        try:
            cursor.execute("INSERT INTO items (code, description, price) VALUES (%s, %s, %s)", (code, desc, price_val))
            conn.commit()
            messagebox.showinfo("Added", "New item added.")
        except pymysql.err.IntegrityError:
            messagebox.showwarning("Duplicate", "Item code already exists.")
    elif edit_mode[0]:
        cursor.execute("UPDATE items SET description=%s, price=%s WHERE code=%s", (desc, price_val, code))
        conn.commit()
        messagebox.showinfo("Updated", "Item updated.")
    else:
        messagebox.showwarning("Error", "Click New or Confirm to add/edit.")
        conn.close()
        return

    conn.close()

    desc_entry.config(state='readonly')
    price_entry.config(state='readonly')
    code_entry.config(state='readonly')
    edit_mode[0] = False
    new_mode[0] = False
    load_records()
    show_record(current_index[0])
    
def delete_record():
    if len(records) == 0:
        messagebox.showwarning("Error", "No records to delete.")
        return

    confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this item?")
    if confirm:
        code = records[current_index[0]][0]
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE code=%s", (code,))
        conn.commit()
        conn.close()

        load_records()
        current_index[0] = max(0, current_index[0]-1)
        show_record(current_index[0])

def clear_fields():
    code_var.set("")
    desc_var.set("")
    price_var.set("")

def exit_program():
    window.destroy()

# Buttons
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

tk.Button(button_frame, text="New", command=new_record, width=10).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Search", command=search_record, width=10).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Confirm", command=confirm_edit, width=10).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Cancel", command=cancel_edit, width=10).grid(row=0, column=3, padx=5)

tk.Button(button_frame, text="Next", command=next_record, width=10).grid(row=1, column=0, padx=5)
tk.Button(button_frame, text="Previous", command=previous_record, width=10).grid(row=1, column=1, padx=5)
tk.Button(button_frame, text="Save", command=save_record, width=10).grid(row=2, column=0, padx=5)
tk.Button(button_frame, text="Clear", command=clear_fields, width=10).grid(row=2, column=1, padx=5)
tk.Button(button_frame, text="Delete", command=delete_record, width=10).grid(row=2, column=2, padx=5)
tk.Button(button_frame, text="Exit", command=exit_program, width=10).grid(row=3, column=1, pady=5)

# Initialize
load_records()
show_record(current_index[0])
window.mainloop()
