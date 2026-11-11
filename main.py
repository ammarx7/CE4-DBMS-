import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime

# ==========================================
# DATABASE CONNECTION
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "Sculpture_Foundry.db")


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS foundries (
            foundry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            foundry_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            contact_email TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sculpture_casts (
            cast_id INTEGER PRIMARY KEY AUTOINCREMENT,
            foundry_id INTEGER NOT NULL,
            sculpture_title TEXT NOT NULL,
            casting_date TEXT NOT NULL,
            FOREIGN KEY (foundry_id)
            REFERENCES foundries(foundry_id)
            ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS material_costs (
            cost_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cast_id INTEGER NOT NULL,
            material_description TEXT NOT NULL,
            cost_amount REAL NOT NULL CHECK(cost_amount >= 0),
            FOREIGN KEY (cast_id)
            REFERENCES sculpture_casts(cast_id)
            ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# INSERT SAMPLE DATA IF MISSING
# ==========================================

def seed_sample_data():
    conn = connect_db()
    cursor = conn.cursor()

    foundries = [
        ("Chola Bronze Works", "chola@example.com"),
        ("Heritage Art Foundry", "heritage@example.com"),
        ("Deccan Sculpture Studio", "deccan@example.com"),
        ("Lotus Metal Arts", "lotus@example.com")
    ]

    for name, email in foundries:
        cursor.execute("""
            INSERT OR IGNORE INTO foundries
            (foundry_name, contact_email)
            VALUES (?, ?)
        """, (name, email))

    casts = [
        ("Chola Bronze Works", "Dancing Nataraja", "2026-10-12"),
        ("Chola Bronze Works", "Temple Guardian", "2026-10-18"),
        ("Heritage Art Foundry", "Reclining Buddha", "2026-10-20"),
        ("Deccan Sculpture Studio", "The Meditating Sage", "2026-10-25"),
        ("Lotus Metal Arts", "River Goddess", "2026-11-02")
    ]

    for foundry_name, title, date in casts:
        cursor.execute("""
            SELECT foundry_id
            FROM foundries
            WHERE foundry_name = ?
        """, (foundry_name,))

        result = cursor.fetchone()

        if result:
            foundry_id = result[0]

            cursor.execute("""
                SELECT cast_id
                FROM sculpture_casts
                WHERE foundry_id = ?
                AND sculpture_title = ?
                AND casting_date = ?
            """, (foundry_id, title, date))

            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO sculpture_casts
                    (foundry_id, sculpture_title, casting_date)
                    VALUES (?, ?, ?)
                """, (foundry_id, title, date))

    costs = [
        ("Dancing Nataraja", "Bronze Ingot (kg)", 18500),
        ("Dancing Nataraja", "Patina Chemicals", 3200),
        ("Temple Guardian", "Mould Making", 7500),
        ("Reclining Buddha", "Bronze Ingot (kg)", 24000),
        ("Reclining Buddha", "Finishing and Polishing", 4600),
        ("The Meditating Sage", "Mould Making", 6800),
        ("River Goddess", "Patina Chemicals", 2900)
    ]

    for title, material, amount in costs:
        cursor.execute("""
            SELECT cast_id
            FROM sculpture_casts
            WHERE sculpture_title = ?
        """, (title,))

        result = cursor.fetchone()

        if result:
            cast_id = result[0]

            cursor.execute("""
                SELECT cost_id
                FROM material_costs
                WHERE cast_id = ?
                AND material_description = ?
                AND cost_amount = ?
            """, (cast_id, material, amount))

            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO material_costs
                    (cast_id, material_description, cost_amount)
                    VALUES (?, ?, ?)
                """, (cast_id, material, amount))

    conn.commit()
    conn.close()


# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()
root.title("Sculpture Foundry & Casting Cost Tracking Dashboard")
root.geometry("1250x750")
root.minsize(950, 600)
root.configure(bg="#edf2f7")


# ==========================================
# STYLING
# ==========================================

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    rowheight=30,
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold"),
    background="#263746",
    foreground="white"
)

style.configure(
    "TButton",
    font=("Arial", 10, "bold"),
    padding=7
)

style.configure(
    "TNotebook.Tab",
    font=("Arial", 10, "bold"),
    padding=[15, 9]
)


# ==========================================
# HEADING
# ==========================================

heading = tk.Label(
    root,
    text="SCULPTURE FOUNDRY & CASTING COST TRACKING",
    font=("Arial", 20, "bold"),
    bg="#263746",
    fg="white",
    pady=20
)
heading.pack(fill="x")

subtitle = tk.Label(
    root,
    text="Foundry Management | Sculpture Casting | Material Cost Analysis",
    font=("Arial", 11),
    bg="#edf2f7",
    fg="#34495e",
    pady=10
)
subtitle.pack()


# ==========================================
# NOTEBOOK TABS
# ==========================================

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=15, pady=10)

foundry_tab = ttk.Frame(notebook)
cast_tab = ttk.Frame(notebook)
cost_tab = ttk.Frame(notebook)
dashboard_tab = ttk.Frame(notebook)

notebook.add(foundry_tab, text="Foundries")
notebook.add(cast_tab, text="Sculpture Casts")
notebook.add(cost_tab, text="Material Costs")
notebook.add(dashboard_tab, text="Combined Dashboard")


# ==========================================
# TREEVIEW FUNCTION
# ==========================================

def create_tree(parent, columns):
    frame = ttk.Frame(parent)

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        height=14
    )

    for column in columns:
        tree.heading(
            column,
            text=column.replace("_", " ").title()
        )

        tree.column(
            column,
            width=165,
            anchor="center"
        )

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return frame, tree


# ==========================================
# UPDATE DROPDOWNS
# ==========================================

def update_dropdowns():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT foundry_id, foundry_name
        FROM foundries
        ORDER BY foundry_id
    """)

    foundries = cursor.fetchall()

    foundry_combo["values"] = [
        f"{row[0]} - {row[1]}" for row in foundries
    ]

    if foundry_combo.get() not in foundry_combo["values"]:
        foundry_combo.set("")

    cursor.execute("""
        SELECT cast_id, sculpture_title
        FROM sculpture_casts
        ORDER BY cast_id
    """)

    casts = cursor.fetchall()

    cast_combo["values"] = [
        f"{row[0]} - {row[1]}" for row in casts
    ]

    if cast_combo.get() not in cast_combo["values"]:
        cast_combo.set("")

    conn.close()


# ==========================================
# REFRESH FOUNDRIES
# ==========================================

def refresh_foundries():
    foundry_tree.delete(*foundry_tree.get_children())

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT foundry_id, foundry_name, contact_email
        FROM foundries
        ORDER BY foundry_id
    """)

    for row in cursor.fetchall():
        foundry_tree.insert("", "end", values=row)

    conn.close()


# ==========================================
# REFRESH SCULPTURE CASTS
# ==========================================

def refresh_casts():
    cast_tree.delete(*cast_tree.get_children())

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sc.cast_id,
            f.foundry_name,
            sc.sculpture_title,
            sc.casting_date
        FROM sculpture_casts sc
        JOIN foundries f
        ON sc.foundry_id = f.foundry_id
        ORDER BY sc.cast_id
    """)

    for row in cursor.fetchall():
        cast_tree.insert("", "end", values=row)

    conn.close()


# ==========================================
# REFRESH MATERIAL COSTS
# ==========================================

def refresh_costs():
    cost_tree.delete(*cost_tree.get_children())

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            mc.cost_id,
            sc.sculpture_title,
            mc.material_description,
            mc.cost_amount
        FROM material_costs mc
        JOIN sculpture_casts sc
        ON mc.cast_id = sc.cast_id
        ORDER BY mc.cost_id
    """)

    for row in cursor.fetchall():
        cost_tree.insert("", "end", values=row)

    conn.close()


# ==========================================
# REFRESH COMBINED DASHBOARD
# ==========================================

def refresh_dashboard():
    dashboard_tree.delete(*dashboard_tree.get_children())

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sc.cast_id,
            f.foundry_name,
            sc.sculpture_title,
            sc.casting_date,
            mc.material_description,
            mc.cost_amount
        FROM foundries f
        INNER JOIN sculpture_casts sc
        ON f.foundry_id = sc.foundry_id
        INNER JOIN material_costs mc
        ON sc.cast_id = mc.cast_id
        ORDER BY sc.cast_id, mc.cost_id
    """)

    rows = cursor.fetchall()

    for row in rows:
        dashboard_tree.insert("", "end", values=row)

    conn.close()

    total_cost = sum(float(row[5]) for row in rows)

    total_label.config(
        text=f"Total Material Cost: ₹{total_cost:,.2f}"
    )

    records_label.config(
        text=f"Total Cost Records: {len(rows)}"
    )


# ==========================================
# REFRESH ALL TABLES
# ==========================================

def refresh_all():
    refresh_foundries()
    refresh_casts()
    refresh_costs()
    refresh_dashboard()
    update_dropdowns()


# ==========================================
# ADD FOUNDRY
# ==========================================

def add_foundry():
    name = foundry_name_entry.get().strip()
    email = foundry_email_entry.get().strip()

    if not name or not email:
        messagebox.showwarning(
            "Input Error",
            "Please enter foundry name and email."
        )
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO foundries
            (foundry_name, contact_email)
            VALUES (?, ?)
        """, (name, email))

        conn.commit()
        conn.close()

        foundry_name_entry.delete(0, tk.END)
        foundry_email_entry.delete(0, tk.END)

        refresh_all()

        messagebox.showinfo(
            "Success",
            "Foundry added successfully!"
        )

    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Error",
            "This foundry already exists."
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# ==========================================
# ADD SCULPTURE CAST
# ==========================================

def add_cast():
    foundry = foundry_combo.get()
    title = sculpture_entry.get().strip()
    date = date_entry.get().strip()

    if not foundry or not title or not date:
        messagebox.showwarning(
            "Input Error",
            "Please complete all sculpture cast fields."
        )
        return

    try:
        datetime.strptime(date, "%Y-%m-%d")
        foundry_id = int(foundry.split(" - ")[0])

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sculpture_casts
            (foundry_id, sculpture_title, casting_date)
            VALUES (?, ?, ?)
        """, (foundry_id, title, date))

        conn.commit()
        conn.close()

        sculpture_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)

        refresh_all()

        messagebox.showinfo(
            "Success",
            "Sculpture cast added successfully!"
        )

    except ValueError:
        messagebox.showerror(
            "Invalid Date",
            "Enter date in YYYY-MM-DD format."
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# ==========================================
# ADD MATERIAL COST
# ==========================================

def add_cost():
    cast = cast_combo.get()
    material = material_entry.get().strip()
    amount = amount_entry.get().strip()

    if not cast or not material or not amount:
        messagebox.showwarning(
            "Input Error",
            "Please complete all material cost fields."
        )
        return

    try:
        cast_id = int(cast.split(" - ")[0])
        cost_amount = float(amount)

        if cost_amount < 0:
            raise ValueError

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO material_costs
            (cast_id, material_description, cost_amount)
            VALUES (?, ?, ?)
        """, (cast_id, material, cost_amount))

        conn.commit()
        conn.close()

        material_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)

        refresh_all()

        messagebox.showinfo(
            "Success",
            "Material cost added successfully!"
        )

    except ValueError:
        messagebox.showerror(
            "Invalid Amount",
            "Enter a valid non-negative amount."
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# ==========================================
# DELETE SELECTED RECORD
# ==========================================

def delete_record(table, id_column, tree):
    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Selection Required",
            "Please select a record from the table first."
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this record?"
    )

    if not confirm:
        return

    values = tree.item(selected[0], "values")
    record_id = values[0]

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            f"DELETE FROM {table} WHERE {id_column} = ?",
            (record_id,)
        )

        conn.commit()
        conn.close()

        refresh_all()

        messagebox.showinfo(
            "Success",
            "Record deleted successfully."
        )

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# ==========================================
# FOUNDRIES TAB
# ==========================================

foundry_form = ttk.LabelFrame(
    foundry_tab,
    text="Add New Foundry",
    padding=15
)
foundry_form.pack(fill="x", padx=12, pady=10)

ttk.Label(
    foundry_form,
    text="Foundry Name"
).grid(row=0, column=0, padx=8, pady=8)

foundry_name_entry = ttk.Entry(foundry_form, width=25)
foundry_name_entry.grid(row=0, column=1, padx=8)

ttk.Label(
    foundry_form,
    text="Contact Email"
).grid(row=0, column=2, padx=8)

foundry_email_entry = ttk.Entry(foundry_form, width=25)
foundry_email_entry.grid(row=0, column=3, padx=8)

ttk.Button(
    foundry_form,
    text="Add Foundry",
    command=add_foundry
).grid(row=0, column=4, padx=10)

# DELETE BUTTON AT BOTTOM

foundry_delete_button = ttk.Button(
    foundry_tab,
    text="DELETE SELECTED FOUNDRY",
    command=lambda: delete_record(
        "foundries", "foundry_id", foundry_tree
    )
)

foundry_delete_button.pack(side="bottom", pady=10)

foundry_frame, foundry_tree = create_tree(
    foundry_tab,
    ("foundry_id", "foundry_name", "contact_email")
)

foundry_frame.pack(
    side="top",
    fill="both",
    expand=True,
    padx=12,
    pady=10
)


# ==========================================
# SCULPTURE CASTS TAB
# ==========================================

cast_form = ttk.LabelFrame(
    cast_tab,
    text="Add New Sculpture Cast",
    padding=15
)
cast_form.pack(fill="x", padx=12, pady=10)

ttk.Label(
    cast_form,
    text="Select Foundry"
).grid(row=0, column=0, padx=8, pady=8)

foundry_combo = ttk.Combobox(
    cast_form,
    width=25,
    state="readonly"
)
foundry_combo.grid(row=0, column=1, padx=8)

ttk.Label(
    cast_form,
    text="Sculpture Title"
).grid(row=0, column=2, padx=8)

sculpture_entry = ttk.Entry(cast_form, width=25)
sculpture_entry.grid(row=0, column=3, padx=8)

ttk.Label(
    cast_form,
    text="Casting Date"
).grid(row=1, column=0, padx=8, pady=8)

date_entry = ttk.Entry(cast_form, width=25)
date_entry.grid(row=1, column=1, padx=8)

ttk.Label(
    cast_form,
    text="Format: YYYY-MM-DD"
).grid(row=1, column=2, padx=8)

ttk.Button(
    cast_form,
    text="Add Sculpture Cast",
    command=add_cast
).grid(row=1, column=3, padx=8)

# DELETE BUTTON AT BOTTOM

cast_delete_button = ttk.Button(
    cast_tab,
    text="DELETE SELECTED SCULPTURE CAST",
    command=lambda: delete_record(
        "sculpture_casts", "cast_id", cast_tree
    )
)

cast_delete_button.pack(side="bottom", pady=10)

cast_frame, cast_tree = create_tree(
    cast_tab,
    ("cast_id", "foundry_name", "sculpture_title", "casting_date")
)

cast_frame.pack(
    side="top",
    fill="both",
    expand=True,
    padx=12,
    pady=10
)


# ==========================================
# MATERIAL COSTS TAB
# ==========================================

cost_form = ttk.LabelFrame(
    cost_tab,
    text="Add New Material Cost",
    padding=15
)
cost_form.pack(fill="x", padx=12, pady=10)

ttk.Label(
    cost_form,
    text="Select Sculpture"
).grid(row=0, column=0, padx=8, pady=8)

cast_combo = ttk.Combobox(
    cost_form,
    width=25,
    state="readonly"
)
cast_combo.grid(row=0, column=1, padx=8)

ttk.Label(
    cost_form,
    text="Material Description"
).grid(row=0, column=2, padx=8)

material_entry = ttk.Entry(cost_form, width=25)
material_entry.grid(row=0, column=3, padx=8)

ttk.Label(
    cost_form,
    text="Cost Amount (₹)"
).grid(row=1, column=0, padx=8, pady=8)

amount_entry = ttk.Entry(cost_form, width=25)
amount_entry.grid(row=1, column=1, padx=8)

ttk.Button(
    cost_form,
    text="Add Material Cost",
    command=add_cost
).grid(row=1, column=3, padx=8)

# DELETE BUTTON AT BOTTOM

cost_delete_button = ttk.Button(
    cost_tab,
    text="DELETE SELECTED MATERIAL COST",
    command=lambda: delete_record(
        "material_costs", "cost_id", cost_tree
    )
)

cost_delete_button.pack(side="bottom", pady=10)

cost_frame, cost_tree = create_tree(
    cost_tab,
    ("cost_id", "sculpture_title", "material_description", "cost_amount")
)

cost_frame.pack(
    side="top",
    fill="both",
    expand=True,
    padx=12,
    pady=10
)


# ==========================================
# COMBINED DASHBOARD TAB
# ==========================================

dashboard_info = ttk.Frame(dashboard_tab)
dashboard_info.pack(fill="x", padx=12, pady=12)

total_label = ttk.Label(
    dashboard_info,
    text="Total Material Cost: ₹0.00",
    font=("Arial", 13, "bold")
)
total_label.pack(side="left", padx=15)

records_label = ttk.Label(
    dashboard_info,
    text="Total Cost Records: 0",
    font=("Arial", 13, "bold")
)
records_label.pack(side="right", padx=15)

dashboard_frame, dashboard_tree = create_tree(
    dashboard_tab,
    (
        "cast_id",
        "foundry_name",
        "sculpture_title",
        "casting_date",
        "material_description",
        "cost_amount"
    )
)

dashboard_frame.pack(
    fill="both",
    expand=True,
    padx=12,
    pady=10
)

ttk.Button(
    dashboard_tab,
    text="REFRESH DASHBOARD",
    command=refresh_all
).pack(side="bottom", pady=10)


# ==========================================
# START APPLICATION
# ==========================================

try:
    create_tables()
    seed_sample_data()
    refresh_all()

except sqlite3.Error as error:
    messagebox.showerror(
        "Database Error",
        f"Unable to load database:\n{error}"
    )
    root.destroy()

else:
    root.mainloop()