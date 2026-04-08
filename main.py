import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

products = []
sales = []
DATA_FILE = "custok_data.json"

root = tk.Tk()
root.title("CUStok Demo - Stok Takip Sistemi")
root.geometry("1000x600")
root.configure(bg="#1c1c2e")

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview",
                background="#2b2b3c",
                foreground="white",
                rowheight=28,
                fieldbackground="#2b2b3c",
                font=("Segoe UI", 10))
style.map("Treeview", background=[("selected", "#4CAF50")])
style.configure("Treeview.Heading",
                background="#3a3a5a",
                foreground="white",
                font=("Segoe UI", 11, "bold"))

def save_data():
    data = {"products": products, "sales": sales}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            products.clear()
            products.extend(data.get("products", []))
            sales.clear()
            sales.extend(data.get("sales", []))
    except FileNotFoundError:
        pass


sidebar = tk.Frame(root, bg="#0f172a", width=180)
sidebar.pack(side="left", fill="y")


logo_label = tk.Label(sidebar, text="📦 CUStok", font=("Segoe UI", 18, "bold"),
                      bg="#0f172a", fg="#4CAF50")
logo_label.pack(pady=20)


def show_frame(frame):
    for f in [frame_products, frame_sales, frame_graph]:
        f.pack_forget()
    frame.pack(fill="both", expand=True, padx=10, pady=10)

btn_products = tk.Button(sidebar, text="Ürünler", font=("Segoe UI", 12),
                         bg="#2196F3", fg="white", command=lambda: show_frame(frame_products))
btn_products.pack(pady=10, fill="x", padx=10)

btn_sales = tk.Button(sidebar, text="Satışlar", font=("Segoe UI", 12),
                      bg="#9C27B0", fg="white", command=lambda: show_frame(frame_sales))
btn_sales.pack(pady=10, fill="x", padx=10)

btn_graph = tk.Button(sidebar, text="Grafik", font=("Segoe UI", 12),
                      bg="#FF9800", fg="white", command=lambda: show_frame(frame_graph))
btn_graph.pack(pady=10, fill="x", padx=10)


frame_products = tk.Frame(root, bg="#1c1c2e")
frame_sales = tk.Frame(root, bg="#1c1c2e")
frame_graph = tk.Frame(root, bg="#1c1c2e")

tk.Label(frame_products, text="Ürün İsmi", bg="#1c1c2e", fg="white").grid(row=0, column=0)
tk.Label(frame_products, text="Stok", bg="#1c1c2e", fg="white").grid(row=0, column=1)

name_entry = tk.Entry(frame_products, width=30)
name_entry.grid(row=1, column=0, padx=10, pady=5)
stock_entry = tk.Entry(frame_products, width=15)
stock_entry.grid(row=1, column=1, padx=10, pady=5)

def update_table():
    for row in tree.get_children():
        tree.delete(row)
    for p in products:
        tree.insert("", tk.END, values=(p["id"], p["name"], p["stock"]))

def add_product():
    name = name_entry.get().title()
    stock = stock_entry.get()
    if not name or not stock:
        messagebox.showerror("Hata", "Boş bırakma!")
        return
    product = {"id": len(products)+1, "name": name, "stock": int(stock)}
    products.append(product)
    update_table()
    save_data()
    name_entry.delete(0, tk.END)
    stock_entry.delete(0, tk.END)

add_btn = tk.Button(frame_products, text="➕ Ürün Ekle", bg="#4CAF50", fg="white",
                    command=add_product)
add_btn.grid(row=1, column=2, padx=10)

columns = ("ID", "Ürün", "Stok")
tree = ttk.Treeview(frame_products, columns=columns, show="headings", height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=200)
tree.grid(row=2, column=0, columnspan=3, pady=20)


tk.Label(frame_products, text="Satış Adedi", bg="#1c1c2e", fg="white").grid(row=3, column=0)
quantity_entry = tk.Entry(frame_products, width=10)
quantity_entry.grid(row=4, column=0, pady=5)

def sell_product():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Hata", "Ürün seç!")
        return
    quantity = quantity_entry.get()
    if not quantity:
        messagebox.showerror("Hata", "Adet gir!")
        return
    item = tree.item(selected[0])
    product_id = item["values"][0]
    for p in products:
        if p["id"] == product_id:
            if p["stock"] < int(quantity):
                messagebox.showerror("Hata", "Yetersiz stok!")
                return
            p["stock"] -= int(quantity)
            sales.append({"product_id": product_id, "quantity": int(quantity)})
            update_table()
            save_data()
            quantity_entry.delete(0, tk.END)
            return

sell_btn = tk.Button(frame_products, text="💸 Satış Yap", bg="#2196F3", fg="white",
                     command=sell_product)
sell_btn.grid(row=4, column=1, padx=10)

sales_tree = ttk.Treeview(frame_sales, columns=("Ürün","Adet"), show="headings", height=15)
sales_tree.heading("Ürün", text="Ürün")
sales_tree.heading("Adet", text="Adet")
sales_tree.column("Ürün", anchor="center", width=200)
sales_tree.column("Adet", anchor="center", width=100)
sales_tree.pack(fill="both", expand=True, padx=20, pady=20)

def update_sales_table():
    for row in sales_tree.get_children():
        sales_tree.delete(row)
    for s in sales:
        for p in products:
            if p["id"] == s["product_id"]:
                sales_tree.insert("", tk.END, values=(p["name"], s["quantity"]))

frame_sales.bind("<Visibility>", lambda e: update_sales_table())

fig = plt.Figure(figsize=(5,4), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=frame_graph)
canvas.get_tk_widget().pack(fill="both", expand=True)

def draw_graph():
    ax.clear()
    product_names = []
    quantities = []
    for p in products:
        sold = sum(s["quantity"] for s in sales if s["product_id"]==p["id"])
        product_names.append(p["name"])
        quantities.append(sold)
    ax.bar(product_names, quantities, color="#4CAF50")
    ax.set_ylabel("Satılan Adet")
    ax.set_title("Ürün Satış Grafiği")
    canvas.draw()

frame_graph.bind("<Visibility>", lambda e: draw_graph())

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                data = json.loads(content)
                products.clear()
                products.extend(data.get("products", []))
                sales.clear()
                sales.extend(data.get("sales", []))
            else:
                products.clear()
                sales.clear()
    except FileNotFoundError:
        products.clear()
        sales.clear()

update_table()
show_frame(frame_products)

root.mainloop()