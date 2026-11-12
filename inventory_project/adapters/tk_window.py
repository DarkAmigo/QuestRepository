
import tkinter as tk

from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from core import InventoryService, ValidationError


class TkInventoryWindow:

    def __init__(self, root, service, repository):
        self.root = root
        self.service = service
        self.repository = repository

        self.current_path = Path("stock.csv")
        self.is_modified = False

        self.root.title("Inventory Manager")
        self.root.geometry("1150x700")
        self.root.minsize(900, 550)

        self.setup_styles()
        self.create_menu()
        self.create_widgets()

        self.refresh_table()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            rowheight=30,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

        style.configure(
            "TButton",
            font=("Arial", 10),
            padding=6
        )

        style.configure(
            "TLabel",
            font=("Arial", 10)
        )

        style.configure(
            "Invalid.TEntry",
            fieldbackground="#ffdede"
        )

    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)

        file_menu.add_command(
            label="Відкрити...",
            command=self.open_file
        )

        file_menu.add_command(
            label="Зберегти",
            command=self.save_file
        )

        file_menu.add_command(
            label="Зберегти як...",
            command=self.save_as
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Вийти",
            command=self.on_close
        )

        menubar.add_cascade(
            label="Файл",
            menu=file_menu
        )

        self.root.config(menu=menubar)

    def create_widgets(self):
        self.sort_column = None
        self.sort_reverse = False

        container = ttk.Frame(
            self.root,
            padding=12
        )
        container.pack(fill="both", expand=True)

        title = ttk.Label(
            container,
            text="Облік товарів",
            font=("Arial", 20, "bold")
        )
        title.pack(anchor="w", pady=(0, 15))

        search_frame = ttk.Frame(container)
        search_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        ttk.Label(
            search_frame,
            text="Пошук:"
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.search_var = tk.StringVar()

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=40
        )
        search_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.search_var.trace_add(
            "write",
            lambda *_: self.refresh_table()
        )

        content = ttk.Frame(container)
        content.pack(
            fill="both",
            expand=True
        )

        form_frame = ttk.LabelFrame(
            content,
            text="Інформація про товар",
            padding=12
        )

        form_frame.pack(
            side="left",
            fill="y",
            padx=(0, 12)
        )

        self.form_vars = {}
        self.fields = {}

        field_names = {
            "name": "Назва",
            "category": "Категорія",
            "quantity": "Кількість",
            "price": "Ціна",
            "location": "Місце зберігання"
        }

        for row, (key, label) in enumerate(field_names.items()):

            ttk.Label(
                form_frame,
                text=label
            ).grid(
                row=row,
                column=0,
                sticky="w",
                pady=6
            )

            var = tk.StringVar()
            self.form_vars[key] = var

            entry = ttk.Entry(
                form_frame,
                textvariable=var,
                width=25
            )

            entry.grid(
                row=row,
                column=1,
                pady=6,
                padx=(8, 0)
            )

            self.fields[key] = entry

            entry.bind(
                "<KeyRelease>",
                lambda event, field=key:
                    self.fields[field].configure(
                        style="TEntry"
                    )
            )

        buttons = ttk.Frame(form_frame)

        buttons.grid(
            row=len(field_names),
            column=0,
            columnspan=2,
            pady=15
        )

        ttk.Button(
            buttons,
            text="Додати",
            command=self.add_item
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Оновити",
            command=self.update_item
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Видалити",
            command=self.delete_item
        ).pack(fill="x", pady=3)

        ttk.Button(
            buttons,
            text="Очистити форму",
            command=self.clear_form
        ).pack(fill="x", pady=3)

        # Таблиця товарів
        table_frame = ttk.LabelFrame(
            content,
            text="Список товарів",
            padding=8
        )

        table_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        columns = (
            "id",
            "name",
            "category",
            "quantity",
            "price",
            "location",
            "created_at"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "name": "Назва",
            "category": "Категорія",
            "quantity": "Кількість",
            "price": "Ціна",
            "location": "Місце",
            "created_at": "Дата створення"
        }

        widths = {
            "id": 45,
            "name": 120,
            "category": 100,
            "quantity": 75,
            "price": 85,
            "location": 100,
            "created_at": 145
        }

        for column in columns:

            self.tree.heading(
                column,
                text=headings[column],
                command=lambda col=column:
                    self.sort_by(col)
            )

            self.tree.column(
                column,
                width=widths[column],
                minwidth=40,
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.load_selected
        )

        # Рядок стану
        self.status_var = tk.StringVar(
            value="Готово до роботи"
        )

        status = ttk.Label(
            container,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
            padding=5
        )

        status.pack(
            fill="x",
            side="bottom",
            pady=(10, 0)
        )

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = self.search_var.get()

        items = self.service.search_items(query)

        if self.sort_column:
            items.sort(
                key=lambda item: getattr(
                    item,
                    self.sort_column
                ),
                reverse=self.sort_reverse
            )

        for item in items:
            self.tree.insert(
                "",
                "end",
                iid=str(item.id),
                values=(
                    item.id,
                    item.name,
                    item.category,
                    item.quantity,
                    f"{item.price:.2f}",
                    item.location,
                    item.created_at.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                )
            )

        self.status_var.set(
            f"Знайдено товарів: {len(items)}"
        )

    def sort_by(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        self.refresh_table()

    def get_form_data(self):
        return {
            key: var.get()
            for key, var in self.form_vars.items()
        }

    def show_validation_error(self, error):
        if isinstance(error, ValidationError):
            field = error.field

            if field in self.fields:
                self.fields[field].configure(
                    style="Invalid.TEntry"
                )

                self.fields[field].focus_set()

        self.status_var.set(str(error))

        messagebox.showerror(
            "Помилка",
            str(error)
        )

    def add_item(self):
        try:
            item = self.service.add_item(
                self.get_form_data()
            )

            self.is_modified = True

            self.refresh_table()
            self.clear_form()

            self.status_var.set(
                f"Товар '{item.name}' успішно додано. "
                "Є незбережені зміни."
            )

        except (ValidationError, ValueError) as error:
            self.show_validation_error(error)

    def load_selected(self, event=None):
        selected = self.tree.selection()

        if not selected:
            return

        item_id = int(selected[0])
        item = self.service.get_item(item_id)

        if item is None:
            return

        values = {
            "name": item.name,
            "category": item.category,
            "quantity": str(item.quantity),
            "price": str(item.price),
            "location": item.location
        }

        for key, value in values.items():
            self.form_vars[key].set(value)

            self.fields[key].configure(
                style="TEntry"
            )

        self.status_var.set(
            f"Вибрано товар ID: {item.id}"
        )

    def update_item(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Увага",
                "Спочатку виберіть товар у таблиці"
            )
            return

        item_id = int(selected[0])

        try:
            item = self.service.update_item(
                item_id,
                self.get_form_data()
            )

            self.is_modified = True

            self.refresh_table()
            self.clear_form()

            self.status_var.set(
                f"Товар '{item.name}' оновлено. "
                "Є незбережені зміни."
            )

        except (ValidationError, ValueError) as error:
            self.show_validation_error(error)

    def delete_item(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Увага",
                "Спочатку виберіть товар"
            )
            return

        item_id = int(selected[0])

        answer = messagebox.askyesno(
            "Підтвердження",
            "Ви дійсно хочете видалити цей товар?"
        )

        if not answer:
            return

        try:
            self.service.delete_item(item_id)

            self.is_modified = True

            self.refresh_table()
            self.clear_form()

            self.status_var.set(
                f"Товар ID {item_id} видалено. "
                "Є незбережені зміни."
            )

        except (ValidationError, ValueError) as error:
            self.show_validation_error(error)

    def clear_form(self):
        for var in self.form_vars.values():
            var.set("")

        for field in self.fields.values():
            field.configure(style="TEntry")

        self.tree.selection_remove(
            self.tree.selection()
        )

        self.status_var.set("Форму очищено")

    def save_file(self):
        if self.current_path is None:
            return self.save_as()

        try:
            self.repository.save(self.current_path)

            self.is_modified = False

            self.status_var.set(
                f"Дані збережено: {self.current_path}"
            )

            messagebox.showinfo(
                "Успіх",
                "Дані успішно збережено!"
            )

            return True

        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Помилка збереження",
                str(error)
            )

            return False

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV файли", "*.csv"),
                ("Усі файли", "*.*")
            ]
        )

        if not path:
            return False

        self.current_path = Path(path)

        return self.save_file()

    def open_file(self):
        if not self.confirm_unsaved():
            return

        path = filedialog.askopenfilename(
            filetypes=[
                ("CSV файли", "*.csv"),
                ("Усі файли", "*.*")
            ]
        )

        if not path:
            return

        try:
            self.repository.load(path)

            self.current_path = Path(path)
            self.is_modified = False

            self.refresh_table()

            self.status_var.set(
                f"Файл відкрито: {self.current_path}"
            )

        except (OSError, ValueError, TypeError, KeyError) as error:
            messagebox.showerror(
                "Помилка відкриття",
                str(error)
            )

    def confirm_unsaved(self):
        if not self.is_modified:
            return True

        answer = messagebox.askyesnocancel(
            "Незбережені зміни",
            "У вас є незбережені зміни. Зберегти їх?"
        )

        if answer is None:
            return False

        if answer:
            return self.save_file()

        return True

    def on_close(self):
        if self.confirm_unsaved():
            self.root.destroy()
