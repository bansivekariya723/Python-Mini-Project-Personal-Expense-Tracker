import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def init_db():
    """Initializes the SQLite database and creates the expenses table if it doesn't exist."""
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

# ==========================================
# 2. CORE FUNCTIONS
# ==========================================
def add_expense():
    """Adds a new expense record to the database."""
    exp_date = entry_date.get().strip()
    category = combo_category.get().strip()
    amount_str = entry_amount.get().strip()
    description = entry_desc.get().strip()

    # Input validation
    if not exp_date or not category or not amount_str:
        messagebox.showwarning("Input Error", "Please fill in Date, Category, and Amount.")
        return

    try:
        amount = float(amount_str)
        if amount <= 0:
            messagebox.showwarning("Input Error", "Amount must be greater than zero.")
            return
    except ValueError:
        messagebox.showerror("Invalid Input", "Amount must be a valid number.")
        return

    # Insert into database
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (date, category, amount, description)
        VALUES (?, ?, ?, ?)
    """, (exp_date, category, amount, description))
    conn.commit()
    conn.close()

    # Refresh table and reset inputs
    clear_fields()
    load_expenses()
    messagebox.showinfo("Success", "Expense added successfully!")

def load_expenses():
    """Fetches all expenses from the database and populates the table."""
    # Clear existing rows in table
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, category, amount, description FROM expenses ORDER BY id DESC")
    rows = cursor.fetchall()

    total_amount = 0.0
    for row in rows:
        tree.insert("", tk.END, values=(row[0], row[1], row[2], f"{row[3]:.2f}", row[4]))
        total_amount += row[3]

    conn.close()

    # Update total display
    lbl_total_value.config(text=f"${total_amount:,.2f}")

def delete_expense():
    """Deletes the selected expense from the table and database."""
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select an expense row to delete.")
        return

    item_data = tree.item(selected_item[0])["values"]
    expense_id = item_data[0]

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete expense ID {expense_id}?")
    if confirm:
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()

        load_expenses()
        messagebox.showinfo("Deleted", "Expense deleted successfully.")

def clear_fields():
    """Clears input fields and resets date to today."""
    entry_date.delete(0, tk.END)
    entry_date.insert(0, str(date.today()))
    combo_category.set("Food")
    entry_amount.delete(0, tk.END)
    entry_desc.delete(0, tk.END)

# ==========================================
# 3. GUI SETUP (TKINTER)
# ==========================================
init_db()

root = tk.Tk()
root.title("Personal Expense Tracker")
root.geometry("750 x 540".replace(" ", ""))
root.resizable(False, False)

# Form Frame (Inputs)
frame_form = tk.LabelFrame(root, text=" Add New Expense ", font=("Arial", 11, "bold"), padx=15, pady=10)
frame_form.pack(fill=tk.X, padx=15, pady=10)

# Row 1: Date & Category
tk.Label(frame_form, text="Date (YYYY-MM-DD):", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
entry_date = tk.Entry(frame_form, font=("Arial", 10), width=18)
entry_date.grid(row=0, column=1, padx=(5, 20), pady=5)
entry_date.insert(0, str(date.today()))

tk.Label(frame_form, text="Category:", font=("Arial", 10)).grid(row=0, column=2, sticky=tk.W, pady=5)
categories = ["Food", "Transport", "Bills", "Shopping", "Entertainment", "Other"]
combo_category = ttk.Combobox(frame_form, values=categories, state="readonly", font=("Arial", 10), width=16)
combo_category.grid(row=0, column=3, padx=5, pady=5)
combo_category.set("Food")

# Row 2: Amount & Description
tk.Label(frame_form, text="Amount ($):", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
entry_amount = tk.Entry(frame_form, font=("Arial", 10), width=18)
entry_amount.grid(row=1, column=1, padx=(5, 20), pady=5)

tk.Label(frame_form, text="Description:", font=("Arial", 10)).grid(row=1, column=2, sticky=tk.W, pady=5)
entry_desc = tk.Entry(frame_form, font=("Arial", 10), width=18)
entry_desc.grid(row=1, column=3, padx=5, pady=5)

# Buttons Frame
frame_buttons = tk.Frame(frame_form)
frame_buttons.grid(row=2, column=0, columnspan=4, pady=(10, 0))

btn_add = tk.Button(frame_buttons, text="Add Expense", font=("Arial", 10, "bold"), bg="#28a745", fg="white", padx=15, pady=3, command=add_expense)
btn_add.pack(side=tk.LEFT, padx=5)

btn_clear = tk.Button(frame_buttons, text="Clear Fields", font=("Arial", 10), padx=10, pady=3, command=clear_fields)
btn_clear.pack(side=tk.LEFT, padx=5)

# Table Frame (Display Expenses)
frame_table = tk.LabelFrame(root, text=" Expense Records ", font=("Arial", 11, "bold"), padx=10, pady=10)
frame_table.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

columns = ("ID", "Date", "Category", "Amount", "Description")
tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=10)

tree.heading("ID", text="ID")
tree.heading("Date", text="Date")
tree.heading("Category", text="Category")
tree.heading("Amount", text="Amount ($)")
tree.heading("Description", text="Description")

tree.column("ID", width=50, anchor=tk.CENTER)
tree.column("Date", width=110, anchor=tk.CENTER)
tree.column("Category", width=120, anchor=tk.CENTER)
tree.column("Amount", width=100, anchor=tk.E)
tree.column("Description", width=260, anchor=tk.W)

# Scrollbar for table
scrollbar = ttk.Scrollbar(frame_table, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(fill=tk.BOTH, expand=True)

# Bottom Summary Frame
frame_bottom = tk.Frame(root, padx=15, pady=5)
frame_bottom.pack(fill=tk.X, padx=15, pady=(0, 10))

btn_delete = tk.Button(frame_bottom, text="Delete Selected Expense", font=("Arial", 10), bg="#dc3545", fg="white", padx=10, pady=3, command=delete_expense)
btn_delete.pack(side=tk.LEFT)

lbl_total_text = tk.Label(frame_bottom, text="Total Expenses:", font=("Arial", 12, "bold"))
lbl_total_text.pack(side=tk.LEFT, padx=(30, 5))

lbl_total_value = tk.Label(frame_bottom, text="$0.00", font=("Arial", 12, "bold"), fg="#007bff")
lbl_total_value.pack(side=tk.LEFT)

# Initial data load
load_expenses()

# Start application
root.mainloop()
