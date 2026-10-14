import os
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

BD_CON = {
    "host": "localhost",
    "database": "gomnishe",
    "user": "postgres",
    "password": "4640",
    "port": "5432",
}

product_images = []


def connect_db():
    return psycopg2.connect(**BD_CON)


def get_fio(login):
    con = None
    cur = None
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute(
            """
            SELECT name_users, fam_users, otch_users
            FROM public.users
            WHERE login_users = %s
            """,
            (login,)
        )
        row = cur.fetchone()
        if row:
            return f"{row[1]} {row[0]} {row[2] or ''}".strip()
        return None
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
        return None
    finally:
        if cur:
            cur.close()
        if con:
            con.close()

def get_login():
    login = e_login.get().strip()
    if not login:
        messagebox.showwarning("Вход", "Введите логин.")
        return

    fio = get_fio(login)
    if fio:
        f_registracia.pack_forget()
        f_katalog.pack(fill="both", expand=True)
        l_fio.config(text=f"Здравствуйте, {fio}")
    else:
        messagebox.showerror("Вход", "Пользователь с таким логином не найден.")


def go_to_login():
    f_katalog.pack_forget()
    f_registracia.pack(fill="both", expand=True)


def back_to_catalog():
    f_registracia.pack_forget()
    f_katalog.pack(fill="both", expand=True)


def on_mousewheel(event):
    if getattr(event, "delta", 0):
        canvas.yview_scroll(int(-event.delta / 120), "units")
    elif getattr(event, "num", None) == 4:
        canvas.yview_scroll(-1, "units")
    elif getattr(event, "num", None) == 5:
        canvas.yview_scroll(1, "units")


def load_filters():
    con = None
    cur = None
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("SELECT name_categoria FROM public.categoria ORDER BY id_categoria")
        categories = ["Все категории"] + [row[0] for row in cur.fetchall()]
        c_categoria["values"] = categories
        c_categoria.set("Все категории")

        cur.execute("SELECT name_razmer FROM public.razmer ORDER BY name_razmer::integer")
        sizes = ["Любой размер"] + [row[0] for row in cur.fetchall()]
        c_size["values"] = sizes
        c_size.set("Любой размер")
    except Exception as e:
        messagebox.showerror("Ошибка БД", str(e))
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def katalog():
    con = None
    cur = None
    try:
        con = connect_db()
        cur = con.cursor()

        query = """
            SELECT m.id_models, m.name_models, c.name_categoria, m.img,
                   m.prooizvodstvo, m.opisanie, m.coctav, m.zena,
                   r.name_razmer, mr.count_m
            FROM public.models AS m
            LEFT JOIN public.categoria AS c
                ON m.id_categoria = c.id_categoria
            LEFT JOIN public.model_razmer AS mr
                ON m.id_models = mr.id_models
            LEFT JOIN public.razmer AS r
                ON mr.id_razmer = r.id_razmer
            WHERE (%s = '' OR m.name_models ILIKE %s
                   OR m.prooizvodstvo ILIKE %s
                   OR m.opisanie ILIKE %s)
              AND (%s = 'Все категории' OR c.name_categoria = %s)
              AND (%s = 'Любой размер' OR r.name_razmer = %s)
            ORDER BY m.id_models, r.name_razmer::numeric
        """
        search = e_poisk.get().strip()
        pattern = f"%{search}%"
        category = c_categoria.get() or "Все категории"
        size = c_size.get() or "Любой размер"

        cur.execute(
            query,
            (search, pattern, pattern, pattern,
             category, category, size, size)
        )
        rows = cur.fetchall()

        products = {}
        for row in rows:
            model_id, name, category_name, image_name, maker, description, composition, price, size_name, stock = row
            if model_id not in products:
                products[model_id] = {
                    "name": name,
                    "category": category_name,
                    "image": image_name,
                    "maker": maker,
                    "description": description,
                    "composition": composition,
                    "price": price,
                    "sizes": []
                }
            if size_name is not None:
                products[model_id]["sizes"].append((size_name, stock or 0))

        for widget in products_frame.winfo_children():
            widget.destroy()
        product_images.clear()

        if not products:
            tk.Label(
                products_frame,
                text="По выбранным условиям ничего не найдено",
                font=("Arial", 12),
                bg="#f4f1ec",
                fg="#555555",
                pady=30
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=12)

        for idx, product in enumerate(products.values()):
            card = tk.Frame(
                products_frame,
                bg="#ffffff",
                highlightbackground="#ddd6cd",
                highlightthickness=1,
                padx=14,
                pady=12
            )
            card.grid(row=idx, column=0, sticky="ew", padx=12, pady=7)
            card.grid_columnconfigure(1, weight=1)

            image_label = tk.Label(
                card,
                text="Нет фото",
                width=15,
                height=7,
                bg="#eeeae4",
                fg="#77716a",
                font=("Arial", 9)
            )
            image_label.grid(row=0, column=0, rowspan=6, padx=(0, 16), sticky="n")

            image_name = product["image"]
            if image_name:
                image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_name)
                try:
                    photo = tk.PhotoImage(file=image_path)
                    factor = max(1, (photo.width() + 119) // 120, (photo.height() + 119) // 120)
                    if factor > 1:
                        photo = photo.subsample(factor, factor)
                    product_images.append(photo)
                    image_label.config(image=photo, text="", width=120, height=120)
                except (tk.TclError, OSError):
                    pass

            tk.Label(
                card,
                text=product["name"] or "Название не указано",
                font=("Arial", 13, "bold"),
                bg="#ffffff",
                fg="#302b26",
                anchor="w",
                justify="left",
                wraplength=650
            ).grid(row=0, column=1, sticky="ew", pady=(0, 5))

            tk.Label(
                card,
                text=f"Категория: {product['category'] or 'не указана'}",
                font=("Arial", 10),
                bg="#ffffff",
                fg="#6a6259",
                anchor="w"
            ).grid(row=1, column=1, sticky="ew")

            tk.Label(
                card,
                text=f"Производитель: {product['maker'] or 'не указан'}",
                font=("Arial", 10),
                bg="#ffffff",
                fg="#403a34",
                anchor="w"
            ).grid(row=2, column=1, sticky="ew", pady=(3, 0))

            tk.Label(
                card,
                text=product["description"] or "Описание отсутствует",
                font=("Arial", 10),
                bg="#ffffff",
                fg="#403a34",
                anchor="w",
                justify="left",
                wraplength=650
            ).grid(row=3, column=1, sticky="ew", pady=(5, 0))

            tk.Label(
                card,
                text=f"Состав: {product['composition'] or 'не указан'}",
                font=("Arial", 9),
                bg="#ffffff",
                fg="#6a6259",
                anchor="w",
                justify="left",
                wraplength=650
            ).grid(row=4, column=1, sticky="ew", pady=(4, 0))

            if product["sizes"]:
                stock_text = "   ".join(
                    f"{shoe_size}: {count} пар" for shoe_size, count in product["sizes"]
                )
            else:
                stock_text = "Нет данных об остатках"

            tk.Label(
                card,
                text=f"Размеры и наличие: {stock_text}",
                font=("Arial", 10, "bold"),
                bg="#ffffff",
                fg="#636261",
                anchor="w",
                justify="left",
                wraplength=650
            ).grid(row=5, column=1, sticky="ew", pady=(7, 0))

            tk.Label(
                card,
                text=f"{product['price']:,} руб.".replace(",", " "),
                font=("Arial", 13, "bold"),
                fg="#636261",
                bg="#ffffff",
                anchor="w"
            ).grid(row=6, column=1, sticky="ew", pady=(8, 0))

        products_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    except Exception as e:
        messagebox.showerror("Ошибка БД", str(e))
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def clear_filters():
    e_poisk.delete(0, tk.END)
    c_categoria.set("Все категории")
    c_size.set("Любой размер")
    katalog()


window = tk.Tk()
window.title("Chudo-obuv")
window.geometry("1040x760")
window.minsize(760, 540)
window.configure(bg="#f4f1ec")

f_katalog = tk.Frame(window, bg="#f4f1ec")
f_katalog.pack(fill="both", expand=True)
f_katalog.grid_columnconfigure(0, weight=1)
f_katalog.grid_rowconfigure(2, weight=1)

header = tk.Frame(f_katalog, bg="#636261", padx=18, pady=15)
header.grid(row=0, column=0, sticky="ew")
header.grid_columnconfigure(0, weight=1)

l_fio = tk.Label(
    header,
    text="Каталог обуви",
    font=("Arial", 17, "bold"),
    bg="#636261",
    fg="white",
    anchor="w"
)
l_fio.grid(row=0, column=0, sticky="ew")

tk.Button(
    header,
    text="Войти",
    command=go_to_login,
    bg="#ffffff",
    fg="#4d3828",
    activebackground="#e8ded2",
    relief="flat",
    padx=14,
    pady=5
).grid(row=0, column=1, padx=(10, 0))

f_filtri = tk.Frame(f_katalog, bg="#f4f1ec", padx=14, pady=12)
f_filtri.grid(row=1, column=0, sticky="ew")
f_filtri.grid_columnconfigure(1, weight=1)

tk.Label(f_filtri, text="Поиск", bg="#f4f1ec", fg="#403a34").grid(
    row=0, column=0, padx=(0, 6), pady=4
)
e_poisk = tk.Entry(f_filtri, font=("Arial", 10), relief="solid", bd=1)
e_poisk.grid(row=0, column=1, sticky="ew", padx=4, pady=4)

c_categoria = ttk.Combobox(f_filtri, width=16, state="readonly")
c_categoria.grid(row=0, column=2, padx=5, pady=4)

c_size = ttk.Combobox(f_filtri, width=14, state="readonly")
c_size.grid(row=0, column=3, padx=5, pady=4)

tk.Button(
    f_filtri,
    text="Найти",
    command=katalog,
    bg="#636261",
    fg="white",
    activebackground="#636261",
    relief="flat",
    padx=12,
    pady=4
).grid(row=0, column=4, padx=(5, 2), pady=4)

tk.Button(
    f_filtri,
    text="Сбросить",
    command=clear_filters,
    bg="#ded6cc",
    fg="#403a34",
    relief="flat",
    padx=10,
    pady=4
).grid(row=0, column=5, padx=(3, 0), pady=4)

catalog_area = tk.Frame(f_katalog, bg="#f4f1ec")
catalog_area.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
catalog_area.grid_rowconfigure(0, weight=1)
catalog_area.grid_columnconfigure(0, weight=1)

canvas = tk.Canvas(catalog_area, bg="#f4f1ec", highlightthickness=0)
scrollbar = ttk.Scrollbar(catalog_area, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

products_frame = tk.Frame(canvas, bg="#f4f1ec")
products_window = canvas.create_window((0, 0), window=products_frame, anchor="nw")


def update_scroll_region(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))


def resize_products_frame(event):
    canvas.itemconfigure(products_window, width=event.width)


products_frame.bind("<Configure>", update_scroll_region)
canvas.bind("<Configure>", resize_products_frame)
canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind_all("<Button-4>", on_mousewheel)
canvas.bind_all("<Button-5>", on_mousewheel)

f_registracia = tk.Frame(window, bg="#f4f1ec", padx=25, pady=25)
tk.Label(
    f_registracia,
    text="Вход в каталог",
    font=("Arial", 16, "bold"),
    bg="#f4f1ec",
    fg="#636261"
).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

tk.Label(f_registracia, text="Логин:", font=("Arial", 11), bg="#f4f1ec").grid(
    row=1, column=0, padx=5, pady=6, sticky="e"
)
e_login = tk.Entry(f_registracia, width=30, font=("Arial", 11), relief="solid", bd=1)
e_login.grid(row=1, column=1, padx=5, pady=6)

tk.Button(
    f_registracia,
    text="Войти",
    command=get_login,
    bg="#636261",
    fg="white",
    relief="flat",
    padx=16,
    pady=5
).grid(row=2, column=0, columnspan=2, pady=10)

tk.Button(
    f_registracia,
    text="Назад в каталог",
    command=back_to_catalog,
    bg="#ded6cc",
    fg="#403a34",
    relief="flat",
    padx=12,
    pady=5
).grid(row=3, column=0, columnspan=2)

load_filters()
katalog()
window.mainloop()
