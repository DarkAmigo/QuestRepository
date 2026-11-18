import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from repository import InventoryRepository

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Облік товарів (Склад)")
        self.root.geometry("1000x650")
        
        self.repo = InventoryRepository()

        # Змінні для полів введення
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.qty_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.location_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_data)

        self.create_menu()
        self.create_widgets()
        self.refresh_table()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Відкрити...", command=self.open_file)
        file_menu.add_command(label="Зберегти", command=self.save_file)
        file_menu.add_command(label="Зберегти як...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.root.quit)
        
        menubar.add_cascade(label="Файл", menu=file_menu)
        self.root.config(menu=menubar)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Верхня панель: Пошук
        search_frame = ttk.LabelFrame(main_frame, text="Швидкий пошук", padding=5)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Пошук за назвою або категорією:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)

        # Середня частина: Таблиця (Treeview) з прокруткою
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('id', 'name', 'category', 'quantity', 'price', 'location', 'created_at')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='browse')

        headers = {
            'id': 'ID', 'name': 'Назва', 'category': 'Категорія', 
            'quantity': 'Кількість', 'price': 'Ціна (₴)', 
            'location': 'Склад/Полиця', 'created_at': 'Дата створення'
        }
        for col, text in headers.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=110, anchor=tk.W)
        self.tree.column('id', width=50, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # Нижня частина: Форма введення та кнопки
        bottom_frame = ttk.Frame(main_frame, padding=5)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)

        form_frame = ttk.LabelFrame(bottom_frame, text="Деталі товару", padding=10)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        fields = [
            ("name", "Назва:", self.name_var, 0, 0),
            ("category", "Категорія:", self.category_var, 0, 2),
            ("quantity", "Кількість:", self.qty_var, 1, 0),
            ("price", "Ціна:", self.price_var, 1, 2),
            ("location", "Склад/Полиця:", self.location_var, 2, 0)
        ]

        self.entries = {}
        for key, label_text, var, row, col in fields:
            ttk.Label(form_frame, text=label_text).grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(form_frame, textvariable=var, width=20)
            entry.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=5)
            self.entries[key] = entry

        # Панель кнопок
        btn_frame = ttk.Frame(bottom_frame, padding=5)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        ttk.Button(btn_frame, text="Додати", command=self.add_record, width=15).pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="Оновити", command=self.update_record, width=15).pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="Видалити", command=self.delete_record, width=15).pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="Очистити форму", command=self.clear_form, width=15).pack(fill=tk.X, pady=3)

        # Статус-бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готово до роботи.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, message):
        self.status_var.set(message)

    def clear_form(self):
        self.id_var.set("")
        self.name_var.set("")
        self.category_var.set("")
        self.qty_var.set("")
        self.price_var.set("")
        self.location_var.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        for entry in self.entries.values():
            entry.state(['!invalid'])
        self.set_status("Форму очищено.")

    def validate_inputs(self):
        for entry in self.entries.values():
            entry.state(['!invalid'])

        name = self.name_var.get().strip()
        category = self.category_var.get().strip()
        qty_str = self.qty_var.get().strip()
        price_str = self.price_var.get().strip().replace(',', '.')
        location = self.location_var.get().strip()

        errors = []

        if not name:
            self.entries['name'].state(['invalid'])
            errors.append("Поле 'Назва' не може бути порожнім.")
        
        if not category:
            self.entries['category'].state(['invalid'])
            errors.append("Поле 'Категорія' не може бути порожнім.")

        try:
            quantity = int(qty_str)
            if quantity < 0:
                raise ValueError
        except ValueError:
            self.entries['quantity'].state(['invalid'])
            errors.append("Кількість має бути цілим числом >= 0.")

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError
        except ValueError:
            self.entries['price'].state(['invalid'])
            errors.append("Ціна має бути числом >= 0.")

        if errors:
            err_msg = " | ".join(errors)
            self.set_status(err_msg)
            messagebox.showerror("Помилка валідації", err_msg)
            return None

        return {
            'name': name,
            'category': category,
            'quantity': int(qty_str),
            'price': float(price_str),
            'location': location
        }

    def add_record(self):
        data = self.validate_inputs()
        if data:
            self.repo.add_item(data)
            self.refresh_table()
            self.clear_form()
            self.set_status("Товар успішно додано.")

    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Оберіть рядок у таблиці для оновлення!")
            return
        
        item_id = int(self.tree.item(selected[0])['values'][0])
        data = self.validate_inputs()
        if data:
            success = self.repo.update_item(item_id, data)
            if success:
                self.refresh_table()
                self.clear_form()
                self.set_status(f"Товар з ID {item_id} оновлено.")
            else:
                messagebox.showerror("Помилка", "Товар не знайдено в базі даних.")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Оберіть рядок у таблиці для видалення!")
            return

        item_id = int(self.tree.item(selected[0])['values'][0])
        confirmed = messagebox.askyesno("Підтвердження", f"Ви дійсно хочете видалити товар з ID {item_id}?")
        if confirmed:
            success = self.repo.delete_item(item_id)
            if success:
                self.refresh_table()
                self.clear_form()
                self.set_status(f"Товар з ID {item_id} видалено.")
            else:
                messagebox.showerror("Помилка", "Не вдалося видалити товар.")

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0])['values']
        self.id_var.set(item_values[0])
        self.name_var.set(item_values[1])
        self.category_var.set(item_values[2])
        self.qty_var.set(item_values[3])
        self.price_var.set(item_values[4])
        self.location_var.set(item_values[5])
        self.set_status(f"Обрано товар ID: {item_values[0]}")

    def refresh_table(self, items=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        display_items = items if items is not None else self.repo.get_all()
        for item in display_items:
            self.tree.insert("", tk.END, values=(
                item.get('id'),
                item.get('name'),
                item.get('category'),
                item.get('quantity'),
                item.get('price'),
                item.get('location', ''),
                item.get('created_at', '')
            ))

    def filter_data(self, *args):
        query = self.search_var.get().strip().lower()
        all_items = self.repo.get_all()
        if not query:
            self.refresh_table(all_items)
            return

        filtered = [
            item for item in all_items 
            if query in str(item.get('name', '')).lower() or query in str(item.get('category', '')).lower()
        ]
        self.refresh_table(filtered)

    def sort_column(self, col, reverse):
        items_list = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        try:
            if col in ('id', 'quantity'):
                items_list.sort(key=lambda x: int(x[0]), reverse=reverse)
            elif col == 'price':
                items_list.sort(key=lambda x: float(x[0]), reverse=reverse)
            else:
                items_list.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)
        except ValueError:
            items_list.sort(key=lambda x: str(x[0]), reverse=reverse)

        for index, (val, child) in enumerate(items_list):
            self.tree.move(child, '', index)

        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Відкрити файл CSV",
            filetypes=[("CSV файли", "*.csv"), ("Всі файли", "*.*")]
        )
        if filepath:
            try:
                self.repo.load_from_file(filepath)
                self.refresh_table()
                self.clear_form()
                self.set_status(f"Успішно завантажено дані з {filepath}")
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

    def save_file(self):
        try:
            self.repo.save_to_file()
            self.set_status("Дані успішно збережено.")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def save_as_file(self, filepath=None):
        if not filepath:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV файли", "*.csv"), ("Всі файли", "*.*")],
                title="Зберегти як..."
            )
        if filepath:
            try:
                self.repo.save_to_file(filepath)
                self.set_status(f"Дані збережено у {filepath}")
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()