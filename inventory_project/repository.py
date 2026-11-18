from datetime import datetime
import os
import csv

class InventoryRepository:
    """Клас-сховище для управління даними товарів та їх збереження у CSV."""
    def __init__(self, filepath="inventory.csv"):
        self.filepath = filepath
        self.items = []
        self.load_from_file()

    def load_from_file(self, filepath=None):
        if filepath:
            self.filepath = filepath
        
        if not os.path.exists(self.filepath):
            self.items = []
            return

        try:
            with open(self.filepath, mode='r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                self.items = []
                for row in reader:
                    try:
                        row['id'] = int(row['id'])
                    except ValueError:
                        row['id'] = 0
                    try:
                        row['quantity'] = int(row['quantity'])
                    except ValueError:
                        row['quantity'] = 0
                    try:
                        row['price'] = float(row['price'])
                    except ValueError:
                        row['price'] = 0.0
                    self.items.append(row)
        except Exception as e:
            raise IOError(f"Помилка читання файлу: {e}")

    def save_to_file(self, filepath=None):
        if filepath:
            self.filepath = filepath

        fieldnames = ['id', 'name', 'category', 'quantity', 'price', 'location', 'created_at']
        try:
            with open(self.filepath, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item in self.items:
                    writer.writerow(item)
        except Exception as e:
            raise IOError(f"Помилка збереження файлу: {e}")

    def get_all(self):
        return self.items

    def generate_id(self):
        if not self.items:
            return 1
        return max(item['id'] for item in self.items) + 1

    def add_item(self, data):
        data['id'] = self.generate_id()
        data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.items.append(data)
        self.save_to_file()

    def update_item(self, item_id, data):
        for item in self.items:
            if item['id'] == item_id:
                item.update(data)
                self.save_to_file()
                return True
        return False

    def delete_item(self, item_id):
        initial_length = len(self.items)
        self.items = [item for item in self.items if item['id'] != item_id]
        if len(self.items) < initial_length:
            self.save_to_file()
            return True
        return False