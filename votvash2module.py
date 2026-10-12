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


def get_fio(login):
    con = None
    cur = None
    try:
        con = psycopg2.connect(**BD_CON)
        cur = con.cursor()
        cur.execute(
            """
            SELECT name_users, fam_users, otch_users
            FROM public.users
            WHERE login_users = %s;
            """,
            (login,),
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
        messagebox.showwarning("Ошибка", "Введите логин!")
        return

    fio = get_fio(login)
    if fio:
        f_registracia.pack_forget()
        f_katalog.pack(fill="both", expand=True)
        l_fio.config(text=f"Добро пожаловать, {fio}")
    else:
        messagebox.showerror("Ошибка", "Пользователь не найден!")


def go_to_registration():
    f_katalog.pack_forget()
    f_registracia.pack(fill="both", expand=True)


def on_mousewheel(event):
    # Windows и macOS
    if getattr(event, "delta", 0):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    # Linux
    elif getattr(event, "num", None) == 4:
        canvas.yview_scroll(-1, "units")
    elif getattr(event, "num", None) == 5:
        canvas.yview_scroll(1, "units")


def katalog():
    con = None
    cur = None
    try:
        con = psycopg2.connect(**BD_CON)
        cur = con.cursor()
        cur.execute(
            """
            SELECT m.name_models, c.name_categoria, m.img,
                   m.prooizvodstvo, m.opisanie, m.coctav, m.zena
            FROM public.models AS m
            LEFT JOIN public.categoria AS c
                ON m.id_categoria = c.id_categoria
            ORDER BY m.id_models ASC;
            """
        )
        rows = cur.fetchall()

        for widget in products_frame.winfo_children():
            widget.destroy()
        product_images.clear()

        for idx, row in enumerate(rows):
            name, category, image_name, maker, description, composition, price = row

            card = tk.Frame(
                products_frame,
                bg="white",
                bd=1,
                relief="solid",
                padx=12,
                pady=10,
            )
            card.grid(row=idx, column=0, sticky="ew", padx=10, pady=6)
            card.grid_columnconfigure(1, weight=1)

            image_label = tk.Label(
                card,
                text="Нет фото",
                width=14,
                height=7,
                bg="#f0f0f0",
                fg="#666666",
            )
            image_label.grid(row=0, column=0, rowspan=5, padx=(0, 14), sticky="n")

            if image_name:
                image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_name)
                try:
                    photo = tk.PhotoImage(file=image_path)
                    factor = max(
                        1,
                        (photo.width() + 119) // 120,
                        (photo.height() + 119) // 120,
                    )
                    if factor > 1:
                        photo = photo.subsample(factor, factor)
                    product_images.append(photo)
                    image_label.config(image=photo, text="", width=120, height=120)
                except (tk.TclError, OSError):
                    pass

            tk.Label(
                card,
                text=name or "Название не указано",
                font=("Calibri", 13, "bold"),
                bg="white",
                anchor="w",
                justify="left",
                wraplength=650,
            ).grid(row=0, column=1, sticky="ew", pady=(0, 5))

            tk.Label(
                card,
                text=f"Категория: {category or 'Не указана'}",
                font=("Calibri", 10),
                fg="#555555",
                bg="white",
                anchor="w",
            ).grid(row=1, column=1, sticky="ew")

            tk.Label(
                card,
                text=f"Производитель: {maker or 'Не указан'}",
                font=("Calibri", 10),
                bg="white",
                anchor="w",
            ).grid(row=2, column=1, sticky="ew", pady=(2, 0))

            tk.Label(
                card,
                text=description or "Описание отсутствует",
                font=("Calibri", 10),
                bg="white",
                anchor="w",
                justify="left",
                wraplength=650,
            ).grid(row=3, column=1, sticky="ew", pady=(5, 0))

            tk.Label(
                card,
                text=f"Состав: {composition or 'Не указан'}",
                font=("Calibri", 9),
                fg="#555555",
                bg="white",
                anchor="w",
                justify="left",
                wraplength=650,
            ).grid(row=4, column=1, sticky="ew", pady=(4, 0))

            tk.Label(
                card,
                text=f"{price:,} руб.".replace(",", " "),
                font=("Calibri", 13, "bold"),
                fg="#176b3a",
                bg="white",
                anchor="e",
            ).grid(row=5, column=1, sticky="ew", pady=(8, 0))

        products_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    except Exception as e:
        messagebox.showerror("Ошибка БД", str(e))
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


window = tk.Tk()
window.title("Chudo-obuv")
window.geometry("1000x750")
window.minsize(700, 500)

# Каталог
f_katalog = tk.Frame(window, bg="#f5f5f5")
f_katalog.pack(fill="both", expand=True)
f_katalog.grid_columnconfigure(0, weight=1)
f_katalog.grid_rowconfigure(2, weight=1)

header = tk.Frame(f_katalog, bg="#f5f5f5", padx=12, pady=10)
header.grid(row=0, column=0, sticky="ew")
header.grid_columnconfigure(0, weight=1)

l_fio = tk.Label(header, text="Каталог обуви", font=("Arial", 15, "bold"), bg="#f5f5f5")
l_fio.grid(row=0, column=0, sticky="w")

b_vhod = tk.Button(header, text="Вход", command=go_to_registration)
b_vhod.grid(row=0, column=1, padx=(10, 0))

f_filtri = tk.Frame(f_katalog, padx=12, pady=6, bg="#f5f5f5")
f_filtri.grid(row=1, column=0, sticky="ew")

tk.Label(f_filtri, text="Найти:", bg="#f5f5f5").grid(row=0, column=0, padx=(0, 5))
e_poisk = tk.Entry(f_filtri, width=35)
e_poisk.grid(row=0, column=1, padx=2)

c_size_znachenia = ["38", "39", "40", "41", "42"]
c_size = ttk.Combobox(f_filtri, values=c_size_znachenia, width=8, state="readonly")
c_size.set("Размер")
c_size.grid(row=0, column=2, padx=5)

c_categoria_znachenia = ["Детская", "Женская", "Мужская"]
c_categoria = ttk.Combobox(
    f_filtri, values=c_categoria_znachenia, width=12, state="readonly"
)
c_categoria.set("Категория")
c_categoria.grid(row=0, column=3, padx=5)

catalog_area = tk.Frame(f_katalog, bg="#f5f5f5")
catalog_area.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
catalog_area.grid_rowconfigure(0, weight=1)
catalog_area.grid_columnconfigure(0, weight=1)

canvas = tk.Canvas(catalog_area, bg="#f5f5f5", highlightthickness=0)
scrollbar = ttk.Scrollbar(catalog_area, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

products_frame = tk.Frame(canvas, bg="#f5f5f5")
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

f_registracia = tk.Frame(window, padx=20, pady=20)
tk.Label(f_registracia, text="Логин:", font=("Calibri", 11)).grid(
    row=0, column=0, padx=5, pady=5
)
e_login = tk.Entry(f_registracia, width=30)
e_login.grid(row=0, column=1, padx=5, pady=5)
tk.Button(f_registracia, text="Войти", command=get_login).grid(
    row=1, column=0, columnspan=2, pady=10
)
tk.Button(
    f_registracia,
    text="Назад в каталог",
    command=lambda: (f_registracia.pack_forget(), f_katalog.pack(fill="both", expand=True)),
).grid(row=2, column=0, columnspan=2)

katalog()
window.mainloop()
