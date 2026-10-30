import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

DB = {"host": "localhost", "database": "postgres", "user": "postgres", "password": "123", "port": "5432"}
user_login = user_role = None
all_products = []

def get_conn():
    return psycopg2.connect(**DB)

def login():
    global user_login, user_role
    login_value = login_entry.get().strip()
    if not login_value:
        messagebox.showwarning("Ошибка", "Поле логина не может быть пустым.\nВведите логин и повторите попытку.")
        return
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""SELECT u.first_name, u.last_name, u.middle_name, r.role_name
                           FROM users u JOIN roles r ON u.role_id = r.role_id
                           WHERE u.login = %s""", (login_value,))
            user_row = cur.fetchone()
        if not user_row:
            messagebox.showerror("Ошибка", f"Пользователь с логином «{login_value}» не найден.\nПроверьте правильность ввода логина.")
            return
        user_login, user_role = login_value, user_row[3]
        reg_frame.pack_forget()
        welcome_lbl.config(text=f"{user_row[1]} {user_row[0]} {user_row[2] or ''}".strip())
        catalog_frame.pack(fill="both", expand=True)
        load_catalog_data()
    except Exception as error:
        messagebox.showerror("Ошибка БД", "Не удалось подключиться к базе данных.\n"
                             f"Текст ошибки: {error}\nПроверьте, что сервер PostgreSQL запущен и параметры подключения верны.")

def load_catalog_data():
    global all_products
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT p.product_id, p.product_name, p.category_id, p.image_path, p.manufacturer, p.description, p.composition, p.price,
                       CASE WHEN EXISTS (SELECT 1 FROM ordered_item oi JOIN orders o ON oi.order_id = o.order_id
                                         WHERE oi.product_id = p.product_id
                                           AND o.order_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
                                           AND o.order_date < DATE_TRUNC('month', CURRENT_DATE)) THEN 0 ELSE 25 END AS calc_discount,
                       COALESCE(SUM(si.quantity), 0) AS total_qty
                FROM products p LEFT JOIN stock_items si ON p.product_id = si.product_id
                GROUP BY p.product_id ORDER BY p.product_name""")
            all_products = cur.fetchall()
        apply_filters()
    except Exception as error:
        messagebox.showerror("Ошибка БД", f"Не удалось загрузить каталог товаров.\nТекст ошибки: {error}")

def get_price(product):
    return round(float(product[7]) * (1 - float(product[8]) / 100), 2)

def apply_filters():
    for w in cards_container.winfo_children():
        w.destroy()
    for product in all_products:
        card = tk.Frame(cards_container, bd=1, relief="solid", bg="white")
        card.pack(fill="x", pady=5, padx=5)
        holder = tk.Frame(card, width=80, height=80, bg="#d0d0d0")
        holder.pack_propagate(False); holder.pack(side="left", padx=5, pady=5)
        for path in (f"Images/{product[3]}", "picture.png"):
            try:
                img = tk.PhotoImage(file=path).subsample(4, 4)
                lbl = tk.Label(holder, image=img, bg="#d0d0d0"); lbl.image = img
                lbl.pack(expand=True); card.img = img; break
            except Exception:
                continue
        else:
            tk.Label(holder, text="Нет\nфото", bg="#d0d0d0", fg="#666").pack(expand=True)
        info = tk.Frame(card, bg="white"); info.pack(side="left", padx=10, fill="x", expand=True)
        tk.Label(info, text=f"{product[4]} | {product[1]}", bg="white",
                 font=("Calibri", 11, "bold")).pack(anchor="w")
        line = tk.Frame(info, bg="white"); line.pack(anchor="w", fill="x")
        tk.Label(line, text=f"Категория: {product[2]} | В наличии: ", bg="white",
                 font=("Calibri", 11)).pack(side="left")
        low = product[9] <= 3
        tk.Label(line, text=f"{product[9]} шт.", bg="#ffcccc" if low else "white",
                 fg="red" if low else "black",
                 font=("Calibri", 11, "bold" if low else "normal")).pack(side="left")
        tk.Label(info, text=f"Состав: {product[6]}", bg="white", font=("Calibri", 11)).pack(anchor="w")
        tk.Label(info, text=f"Цена: {get_price(product)} руб.", bg="white",
                 font=("Calibri", 11, "bold")).pack(anchor="w")
    cards_container.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

window = tk.Tk()
window.title("Чудо Обувь - Каталог")
try: window.iconbitmap("icon.ico")
except Exception: pass
window.geometry("950x650")

reg_frame = tk.Frame(window); reg_frame.pack(expand=True)
tk.Label(reg_frame, text="Вход в систему", font=("Arial", 14, "bold")).pack(pady=20)
tk.Label(reg_frame, text="Логин:", font=("Arial", 12)).pack()
login_entry = tk.Entry(reg_frame, font=("Arial", 12)); login_entry.pack(pady=5)
tk.Button(reg_frame, text="Войти", command=login, width=15).pack(pady=10)

catalog_frame = tk.Frame(window)
top_bar = tk.Frame(catalog_frame); top_bar.pack(fill="x", pady=5, padx=5)
try:
    logo_img = tk.PhotoImage(file="logo.png").subsample(3, 3)
    tk.Label(top_bar, image=logo_img, bg=window.cget("bg")).pack(side="left", padx=10)
except Exception:
    tk.Label(top_bar, text="ЧУДО ОБУВЬ", font=("Arial", 14, "bold"), fg="#007bff").pack(side="left", padx=10)
welcome_lbl = tk.Label(top_bar, text="", font=("Arial", 10, "bold")); welcome_lbl.pack(side="right", padx=10)
tk.Button(top_bar, text="Выйти", command=lambda: (catalog_frame.pack_forget(),
          reg_frame.pack(expand=True), welcome_lbl.config(text=""))).pack(side="right", padx=5)

canvas = tk.Canvas(catalog_frame, highlightthickness=0); canvas.pack(side="left", fill="both", expand=True)
scrollbar = ttk.Scrollbar(catalog_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)
cards_container = tk.Frame(canvas)
canvas_window = canvas.create_window((0, 0), window=cards_container, anchor="nw")

def on_canvas_configure(event):
    canvas.itemconfig(canvas_window, width=event.width)
    canvas.configure(scrollregion=canvas.bbox("all"))

def on_cards_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas.bind("<Configure>", on_canvas_configure)
cards_container.bind("<Configure>", on_cards_configure)
window.mainloop()