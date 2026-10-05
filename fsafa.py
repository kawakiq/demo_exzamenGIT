'''
import tkinter as tk

window = tk.Tk()
window.title("Моя визитка")
window.geometry("350x250")

l1 = tk.Label(window, text = "Паша", font=("Arial", 20))
l1.pack(pady=20)

l2 = tk.Label(window, text = "Стундент", font=("Arial", 20))
l2.pack(pady=20)

l3 = tk.Label(window, text = "МСК", font=("Arial", 20))
l3.pack(pady=20)

window.mainloop()
'''


'''
import tkinter as tk

n = 0
window = tk.Tk()
window.title("Счетчик кликов")
window.geometry("300x250")

def click():
    global n
    n += 1
    l1.config(text=n)

def sbros():
    global n
    n = 0
    l1.config(text=n)

l1 = tk.Label(window, text = n, font=("Arial", 20))
l1.pack(pady=5)

b1 = tk.Button(window, text="Клик!", font=("Arial", 20), command=click)
b1.pack(pady=5)

b2 = tk.Button(window, text="Сброс", font=("Arial", 20), command=sbros)
b2.pack(pady=5)

window.mainloop()
'''

'''
import tkinter as tk

sen1 = 0
sen2 = 0
answer = 0

window = tk.Tk()
window.title("Калькулятор")
window.geometry("300x250")

def umhzh():
    global sen1, sen2, answer
    try:
        sen1 = float(e1.get())
        sen2 = float(e2.get())
        answer = sen1 * sen2
        l3.config(text=str(answer))
    except ValueError:
        l3.config(text="Ошибка ввода")

f1 = tk.Frame(window)
f1.pack(pady=20, padx=20)

tk.Label(f1, text="1:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
e1 = tk.Entry(f1, width=5)
e1.grid(row=0, column=1, padx=5, pady=5)

tk.Label(f1, text="2:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
e2 = tk.Entry(f1, width=5)
e2.grid(row=1, column=1, padx=5, pady=5)

b1 = tk.Button(f1, text="*", font=("Arial", 10), command=umhzh)
b1.grid(row=3, column=0, columnspan=2, pady=10)

l3 = tk.Label(f1, text=str(answer))
l3.grid(row=4, column=0, columnspan=2, pady=10)

window.mainloop()
'''