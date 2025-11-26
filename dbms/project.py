import mysql.connector as MyConn
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ------------------- Database Connection -------------------
def connect_db():
    # First create DB/tables if not exists
    db = MyConn.connect(host="localhost", user="root", password="", port=3306)
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS news_management")
    cursor.execute("USE news_management")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_info(
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50),
            email VARCHAR(50),
            age INT,
            contact_number VARCHAR(20)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news(
            news_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200),
            body TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES user_info(user_id) ON DELETE CASCADE
        )
    """)

    db.commit()
    db.close()

    # Return connection directly to the DB
    return MyConn.connect(host="localhost", user="root", password="", port=3306, database="news_management")


# ------------------- Sample Users -------------------
def insert_sample_data():
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM user_info")
    if cursor.fetchone()[0] == 0:
        users = [
            ("Alice", "alice@example.com", 25, "0123456789"),
            ("Bob", "bob@example.com", 30, "0123456790"),
            ("Charlie", "charlie@example.com", 28, "0123456791"),
            ("David", "david@example.com", 32, "0123456792"),
            ("Eva", "eva@example.com", 27, "0123456793")
        ]
        cursor.executemany("""
            INSERT INTO user_info(username,email,age,contact_number)
            VALUES (%s,%s,%s,%s)
        """, users)
        db.commit()

    db.close()


# ------------------- Sample News -------------------
def insert_sample_news():
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM news")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT user_id FROM user_info ORDER BY user_id")
        ids = [x[0] for x in cursor.fetchall()]

        if not ids:
            db.close()
            return

        data = [
            ("New Species Discovered",
             "Scientists found a new species of frog deep inside the Amazon rainforest. This discovery could lead to more environmental studies.",
             "2025-11-03 09:00:00"),

            ("Breakthrough in AI Art",
             "AI-generated illustrations are improving with advanced models, enabling highly realistic and creative outputs.",
             "2025-11-06 12:30:00"),

            ("Solar Water Purification",
             "A solar-powered water purification device is now helping rural villages access clean drinking water.",
             "2025-11-10 14:15:00")
        ]

        rows = []
        for i, (t, b, d) in enumerate(data):
            rows.append((t, b, d, ids[i % len(ids)]))

        cursor.executemany("""
            INSERT INTO news(title, body, created_at, user_id)
            VALUES (%s,%s,%s,%s)
        """, rows)
        db.commit()

    db.close()

def create_scrollable_treeview(parent, columns, height=20):
    container = tk.Frame(parent, bg="#1e1e1e")
    container.pack(fill="both", expand=True)

    # Scrollbars
    scrollbar_y = tk.Scrollbar(container, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")

    scrollbar_x = tk.Scrollbar(container, orient="horizontal")
    scrollbar_x.pack(side="bottom", fill="x")

    tree = ttk.Treeview(
        container,
        columns=columns,
        show="headings",
        height=height,
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )
    tree.pack(fill="both", expand=True)

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)

    return tree

# -------------------------------------------------------
#        Create scrollable Text widget (light scrollbar)
# -------------------------------------------------------
def create_scrollable_text(parent, width, height):
    frame = tk.Frame(parent, bg="#1e1e1e")
    frame.pack(fill="x", pady=5)

    scrollbar = tk.Scrollbar(frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    text = tk.Text(
        frame,
        width=width,
        height=height,
        bg="#2b2b2b",
        fg="white",
        yscrollcommand=scrollbar.set,
        font=("Segoe UI", 11)
    )
    text.pack(fill="both", expand=True)

    scrollbar.config(command=text.yview)
    return text
# ====================================================
#                 MAIN APPLICATION
# ====================================================
class NewsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📰 News Management System")
        self.root.geometry("1420x780")
        self.root.configure(bg="#1e1e1e")

        ttk.Style().theme_use("clam")

        header = tk.Label(root, text="📰 NEWS BLOG MANAGEMENT SYSTEM",
                          bg="#1e1e1e", fg="white", font=("Segoe UI", 20, "bold"))
        header.pack(pady=10)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_users = tk.Frame(self.notebook, bg="#1e1e1e")
        self.tab_news = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.tab_users, text="Users")
        self.notebook.add(self.tab_news, text="News")

        self.create_users_tab()
        self.create_news_tab()

        # Load initial data
        self.load_users()
        self.load_news()
        self.load_user_combo()

    # ====================================================
    #                  USERS TAB
    # ====================================================
    def create_users_tab(self):
        frame = tk.Frame(self.tab_users, bg="#1e1e1e")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Smaller clean user form
        form = tk.LabelFrame(frame, text="User Form", bg="#1e1e1e", fg="white",
                             font=("Segoe UI",14, "bold"))
        form.place(x=20, y=20, width=360, height=380)

        lbl = {"bg": "#1e1e1e", "fg": "white", "font":("Segoe UI", 11)}
        ent = {"bg": "#2d2d2d", "fg": "white", "font": ("Segoe UI", 11)}

        tk.Label(form, text="Username:", **lbl).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.u_username = tk.Entry(form, width=25, **ent)
        self.u_username.grid(row=0, column=1, padx=10)

        tk.Label(form, text="Email:", **lbl).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.u_email = tk.Entry(form, width=25, **ent)
        self.u_email.grid(row=1, column=1)

        tk.Label(form, text="Age:", **lbl).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.u_age = tk.Entry(form, width=25, **ent)
        self.u_age.grid(row=2, column=1)

        tk.Label(form, text="Contact:", **lbl).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.u_contact = tk.Entry(form, width=25, **ent)
        self.u_contact.grid(row=3, column=1)

        self.btn_u_add = tk.Button(form, text="Add", bg="#575843", fg="white",
                                   width=10, font=("Segoe UI", 11),
                                   command=self.add_user)
        self.btn_u_add.place(x=20, y=198)



        self.btn_u_update = tk.Button(form, text="Update", bg="#575843", fg="white",
                                      width=10, font=("Segoe UI", 11),
                                      state="disabled",
                                      command=self.update_user)
        self.btn_u_update.place(x=180, y=198)


        self.btn_u_delete = tk.Button(form, text="Delete", bg="#575843", fg="white",
                                      width=10, font=("Segoe UI", 11),
                                      state="disabled",
                                      command=self.delete_user)
        self.btn_u_delete.place(x=20, y=250)


        tk.Button(form, text="Clean Form", bg="#575843", fg="white",
                  width=10, font=("Segoe UI", 11),
                  command=self.clear_user_form).place(x=180, y=250)

        tk.Button(form, text="View News", bg="#575843", fg="white",
                  width=10, font=("Segoe UI", 11),
                  command=self.show_user_news_panel).place(x=100, y=299)


        # RIGHT: USERS TABLE (ID hidden; stored in iid)
        table_frame = tk.LabelFrame(
            frame, text="Users List", bg="#1e1e1e", fg="white",
            font=("Segoe UI", 14, "bold")
        )
        table_frame.place(x=400, y=20, width=1000, height=720)

        self.user_list = create_scrollable_treeview(
            table_frame,
            columns=("username", "email", "age", "contact"),
            height=28
        )

        for col, title, w in [
            ("username", "Username", 200),
            ("email", "Email", 250),
            ("age", "Age", 80),
            ("contact", "Contact", 150),
        ]:
            self.user_list.heading(col, text=title)
            self.user_list.column(col, width=w)

        self.user_list.bind("<<TreeviewSelect>>", self.on_user_select)

        # Build hidden panel for user news
        self.create_user_news_panel(frame)

    # ------------------- User News Panel -------------------
    def create_user_news_panel(self, parent):
        self.user_news_panel = tk.Frame(parent, bg="#1e1e1e")

        # BACK BUTTON
        tk.Button(
            self.user_news_panel, text="⬅ Back",
            bg="#444", fg="white",
            command=self.hide_user_news_panel
        ).pack(anchor="w", pady=10, padx=10)

        # HEADER LABEL
        self.user_news_label = tk.Label(
            self.user_news_panel, text="",
            fg="white", bg="#1e1e1e",
            font=("Arial", 14, "bold")
        )
        self.user_news_label.pack(pady=5)

        # TABLE FRAME
        table_frame = tk.Frame(self.user_news_panel, bg="#1e1e1e")
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)


        # TABLE VIEW
        self.user_news_list = ttk.Treeview(
            table_frame,
            columns=("title", "body", "date"),
            show="headings",
            height=20
        )
        self.user_news_list.pack(fill="both", expand=True)

        # HEADINGS
        self.user_news_list.heading("title", text="Title")
        self.user_news_list.heading("body", text="Body Preview")
        self.user_news_list.heading("date", text="Date")

        # COLUMN WIDTHS
        column_widths = {
            "title": 260,
            "body": 520,
            "date": 180
        }
        for col, width in column_widths.items():
            self.user_news_list.column(col, width=width)

        # FULL NEWS VIEWER
        self.full_news_view = tk.Text(
            self.user_news_panel,
            height=11,
            bg="#575843",
            fg="white",
            font=("Segoe UI",12)
        )
        self.full_news_view.pack(fill="x", padx=10, pady=10)

        # On click show full content
        self.user_news_list.bind("<<TreeviewSelect>>", self.show_full_news)


    def show_user_news_panel(self):
        selected = self.user_list.selection()
        if not selected:
            return messagebox.showwarning("Select User", "Please select a user.")

        # Extract user_id from iid
        try:
            user_id = int(selected[0])
        except ValueError:
            return messagebox.showerror("Error", "Invalid user selection.")

        # FETCH NEWS
        db = connect_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT news_id, title, body, created_at
            FROM news
            WHERE user_id=%s
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()

        # FETCH USERNAME
        cursor.execute("SELECT username FROM user_info WHERE user_id=%s", (user_id,))
        username_row = cursor.fetchone()
        username = username_row[0] if username_row else "User"

        db.close()

        # Update label
        self.user_news_label.config(text=f"News posted by {username}")

        # Clear old rows
        for item in self.user_news_list.get_children():
            self.user_news_list.delete(item)

        # Insert data
        for news_id, title, body, created_at in rows:
            preview = (body[:150] + "...") if len(body) > 150 else body
            created_str = created_at.strftime("%Y-%m-%d %H:%M:%S")

            self.user_news_list.insert(
                "", "end",
                values=(title, preview, created_str),
                iid=str(news_id)
            )

        # Clear full viewer
        self.full_news_view.delete("1.0", tk.END)

        # Show panel
        self.user_news_panel.place(x=0, y=0, width=1400, height=720)

    def hide_user_news_panel(self):
        self.user_news_panel.place_forget()

    def show_full_news(self, event):
        selection = self.user_news_list.selection()
        if not selection:
            return

        try:
            news_id = int(selection[0])
        except ValueError:
            return

        # Retrieve full news
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT title, body, created_at FROM news WHERE news_id=%s",(news_id,)
        )
        row = cursor.fetchone()
        db.close()

        if not row:
            return

        title, body, created_at = row
        created_str = created_at.strftime("%Y-%m-%d %H:%M:%S")

        # Display full news
        self.full_news_view.delete("1.0", tk.END)
        self.full_news_view.insert(
            tk.END,
            f"Title: {title}\nDate: {created_str}\n\n{body}"
        )

    # ---------------------- User CRUD ----------------------
    def add_user(self):
        username = self.u_username.get().strip()
        if not username:
            return messagebox.showwarning("Input", "Enter username.")

        try:
            age = int(self.u_age.get().strip()) if self.u_age.get().strip() else None
        except:
            return messagebox.showwarning("Invalid", "Age must be a number.")

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO user_info(username,email,age,contact_number)
            VALUES (%s,%s,%s,%s)
        """, (username, self.u_email.get().strip(), age, self.u_contact.get().strip()))
        db.commit()
        db.close()

        self.clear_user_form()
        self.load_users()
        self.load_user_combo()
        messagebox.showinfo("Success", "User added.")

    def update_user(self):
        selected = self.user_list.selection()
        if not selected:
            return messagebox.showwarning("Select", "Select a user.")

        selected_iid = selected[0]
        try:
            user_id = int(selected_iid)
        except:
            return messagebox.showerror("Error", "Invalid user selection.")

        try:
            age = int(self.u_age.get().strip()) if self.u_age.get().strip() else None
        except:
            return messagebox.showwarning("Invalid", "Age must be a number.")

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE user_info SET username=%s,email=%s,age=%s,contact_number=%s
            WHERE user_id=%s
        """, (self.u_username.get().strip(), self.u_email.get().strip(),
              age, self.u_contact.get().strip(), user_id))
        db.commit()
        db.close()

        self.clear_user_form()
        self.load_users()
        self.load_user_combo()
        messagebox.showinfo("Success", "User updated.")

    def delete_user(self):
        selected = self.user_list.selection()
        if not selected:
            return messagebox.showwarning("Select", "Select a user.")

        selected_iid = selected[0]
        try:
            user_id = int(selected_iid)
        except:
            return messagebox.showerror("Error", "Invalid user selection.")

        if not messagebox.askyesno("Confirm", "Delete this user?"):
            return

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM user_info WHERE user_id=%s", (user_id,))
        db.commit()
        db.close()

        self.clear_user_form()
        self.load_users()
        self.load_user_combo()
        messagebox.showinfo("Success", "User deleted.")

    def load_users(self):
        for i in self.user_list.get_children():
            self.user_list.delete(i)

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT user_id, username, email, age, contact_number FROM user_info")
        for row in cursor.fetchall():
            # row = (user_id, username, email, age, contact_number)
            user_id = row[0]
            values = (row[1], row[2], row[3], row[4])
            # store user_id as iid (hidden)
            self.user_list.insert("", "end", values=values, iid=str(user_id))
        db.close()

    def clear_user_form(self):
        self.u_username.delete(0, tk.END)
        self.u_email.delete(0, tk.END)
        self.u_age.delete(0, tk.END)
        self.u_contact.delete(0, tk.END)

    def on_user_select(self, event):
        selected = self.user_list.selection()
        if not selected:
            return

        selected_iid = selected[0]
        try:
            user_id = int(selected_iid)
        except:
            return

        # fetch the full user record from DB (safer than relying on values)
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT username, email, age, contact_number FROM user_info WHERE user_id=%s", (user_id,))
        row = cursor.fetchone()
        db.close()

        if not row:
            return

        username, email, age, contact = row
        self.u_username.delete(0, tk.END)
        self.u_username.insert(0, username)
        self.u_email.delete(0, tk.END)
        self.u_email.insert(0, email if email else "")
        self.u_age.delete(0, tk.END)
        self.u_age.insert(0, age if age is not None else "")
        self.u_contact.delete(0, tk.END)
        self.u_contact.insert(0, contact if contact else "")
        self.btn_u_update.config(state="normal")
        self.btn_u_delete.config(state="normal")


    # ====================================================
    #                   NEWS TAB
    # ====================================================
    def create_news_tab(self):
        frame = tk.Frame(self.tab_news, bg="#1e1e1e")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # NEWS FORM
        form = tk.LabelFrame(frame, text="News Form", bg="#3F3C3E", fg="white",
                             font=("Arial", 12, "bold"))
        form.place(x=20, y=20, width=1370, height=230)

        tk.Label(form, text="Title:", bg="#100e0f", fg="white").place(x=20, y=20)
        self.n_title = tk.Entry(form, width=60, bg="#2b2b2b", fg="white")
        self.n_title.place(x=80, y=20)

        tk.Label(form, text="Author:", bg="#1e1e1e", fg="white").place(x=850, y=20)
        self.n_author = ttk.Combobox(form, width=30, state="readonly")
        self.n_author.place(x=920, y=20)

        tk.Label(form, text="Body:", bg="#1e1e1e", fg="white").place(x=20, y=70)
        self.n_body = tk.Text(form, width=160, height=6, bg="#2b2b2b", fg="white")
        self.n_body.place(x=80, y=70)

        tk.Button(form, text="Add", bg="#333", fg="white", width=12,
                  command=self.add_news).place(x=250, y=180)
        tk.Button(form, text="Update", bg="#333", fg="white", width=12,
                  command=self.update_news).place(x=350, y=180)
        tk.Button(form, text="Delete", bg="#a00", fg="white", width=12,
                  command=self.delete_news).place(x=450, y=180)
        tk.Button(form, text="Clean Form", bg="#555", fg="white", width=12,
                  command=self.clear_news_form).place(x=550, y=180)
    

        # NEWS TABLE (ID hidden; stored in iid)
        table_frame = tk.LabelFrame(frame, text="All News", bg="#1e1e1e", fg="white",font=("Arial", 12, "bold"))
        table_frame.place(x=20, y=270, width=900, height=480)
        self.news_list = ttk.Treeview(
            table_frame,
            columns=("title", "body", "date", "user"),
            show="headings",
            height=20
        )
        self.news_list.pack(fill="both", expand=True)

        names = ["Title", "Body Preview", "Created", "User"]
        for col, label, w in zip(("title", "body", "date", "user"),names,(220, 350, 150, 120)):
            self.news_list.heading(col, text=label)
            self.news_list.column(col, width=w)

        self.news_list.bind("<<TreeviewSelect>>", self.on_news_select)

        # NEWS PREVIEW PANEL (right side)
        preview_frame = tk.LabelFrame(frame, text="Full News Preview", bg="#433A3A",
                                      fg="white", font=("Segoe UI",12))
        preview_frame.place(x=950, y=270, width=440, height=480)

        self.full_preview = tk.Text(preview_frame, bg="#2C2B2B", fg="white", wrap="word", font=("Segoe UI",10))
        self.full_preview.pack(fill="both", expand=True)

    def on_news_select(self, event):
        selected = self.news_list.selection()
        if not selected:
            return

        news_iid = selected[0]
        try:
            news_id = int(news_iid)
        except:
            return

        # fetch full content from DB
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT news.title, news.body, news.created_at,user_info.username
            FROM news
            LEFT JOIN user_info ON news.user_id = user_info.user_id
            WHERE news_id=%s
        """, (news_id,))
        row = cursor.fetchone()
        db.close()

        if not row:
            return

        title, body, created,username = row
        created_str = created.strftime("%Y-%m-%d %H:%M:%S") if isinstance(created, datetime) else str(created)
        username = username if username else "Unknown"
        self.full_preview.delete("1.0", tk.END)
        self.full_preview.insert(tk.END, f"Author :{username}\nTitle: {title}\nCreated At: {created_str}\n\n{body}")

        # Also populate form for potential update
        self.n_title.delete(0, tk.END)
        self.n_title.insert(0, title)
        self.n_body.delete("1.0", tk.END)
        self.n_body.insert("1.0", body)
        self.n_author.set(username)

        # get author username
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT user_info.username
            FROM news LEFT JOIN user_info ON news.user_id = user_info.user_id
            WHERE news.news_id=%s
        """, (news_id,))
        ur = cursor.fetchone()
        db.close()
        username = ur[0] if ur and ur[0] else ""
        self.n_author.set(username)

    # --------------------- News CRUD ---------------------
    def add_news(self):
        title = self.n_title.get().strip()
        author = self.n_author.get().strip()
        body = self.n_body.get("1.0", tk.END).strip()

        if not title or not author or not body:
            return messagebox.showwarning("Input", "Fill all fields.")

        db = connect_db()
        cursor = db.cursor()

        cursor.execute("SELECT user_id FROM user_info WHERE username=%s", (author,))
        user = cursor.fetchone()
        if not user:
            db.close()
            return messagebox.showerror("Error", "Author not found.")

        cursor.execute("""
            INSERT INTO news(title,body,user_id)
            VALUES (%s,%s,%s)
        """, (title, body, user[0]))
        db.commit()
        db.close()

        self.clear_news_form()
        self.load_news()
        messagebox.showinfo("Success", "News added.")

    def update_news(self):
        selected = self.news_list.selection()
        if not selected:
            return messagebox.showwarning("Select", "Select news.")

        selected_iid = selected[0]
        try:
            news_id = int(selected_iid)
        except:
            return messagebox.showerror("Error", "Invalid news selection.")

        title = self.n_title.get().strip()
        author = self.n_author.get().strip()
        body = self.n_body.get("1.0", tk.END).strip()

        if not title or not author or not body:
            return messagebox.showwarning("Input", "Fill all fields.")

        db = connect_db()
        cursor = db.cursor()

        # get user_id of author
        cursor.execute("SELECT user_id FROM user_info WHERE username=%s", (author,))
        user = cursor.fetchone()
        if not user:
            db.close()
            return messagebox.showerror("Error", "Author not found.")

        user_id = user[0]

        # 🔥 Correct SQL UPDATE statement
        cursor.execute("""
            UPDATE news 
            SET title=%s, body=%s, user_id=%s 
            WHERE news_id=%s
        """, (title, body, user_id, news_id))
        db.commit()
        db.close()
        self.clear_news_form()
        self.load_news()
        messagebox.showinfo("Success", "News updated.")

    
    def delete_news(self):
        selected = self.news_list.selection()
        if not selected:
            return messagebox.showwarning("Select", "Select news.")

        selected_iid = selected[0]
        try:
            news_id = int(selected_iid)
        except:
            return messagebox.showerror("Error", "Invalid news selection.")

        if not messagebox.askyesno("Confirm", "Delete this news?"):
            return

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM news WHERE news_id=%s", (news_id,))
        db.commit()
        db.close()

        self.clear_news_form()
        self.load_news()
        messagebox.showinfo("Success", "News deleted.")

    def load_news(self):
        for i in self.news_list.get_children():
            self.news_list.delete(i)

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT news.news_id, news.title, news.body, news.created_at, user_info.username
            FROM news LEFT JOIN user_info
            ON news.user_id = user_info.user_id
            ORDER BY created_at DESC
        """)

        for row in cursor.fetchall():
            # row = (news_id, title, body, created_at, username)
            news_id = row[0]
            title = row[1]
            body = row[2] or ""
            created = row[3]
            username = row[4] or ""
            preview = body[:150] + "..." if len(body) > 150 else body
            created_str = created.strftime("%Y-%m-%d %H:%M:%S") if isinstance(created, datetime) else str(created)

            # store news_id in iid (hidden)
            self.news_list.insert("", "end", values=(title, preview, created_str, username), iid=str(news_id))

        db.close()

    def clear_news_form(self):
        self.n_title.delete(0, tk.END)
        self.n_body.delete("1.0", tk.END)
        self.n_author.set("")

    def load_user_combo(self):
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT username FROM user_info ORDER BY username ASC")
        users = [x[0] for x in cursor.fetchall()]
        self.n_author["values"] = users
        db.close()


# ====================================================
#                    RUN APPLICATION
# ====================================================
if __name__ == "__main__":
    insert_sample_data()
    insert_sample_news()
    root = tk.Tk()
    app = NewsApp(root)
    root.mainloop()
