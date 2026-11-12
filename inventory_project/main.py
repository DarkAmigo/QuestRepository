
import tkinter as tk

from core import InventoryService
from adapters.csv_repository import CsvItemRepository
from adapters.tk_window import TkInventoryWindow


def main():
    repository = CsvItemRepository("stock.csv")

    service = InventoryService(repository)

    root = tk.Tk()

    app = TkInventoryWindow(root, service, repository)

    root.mainloop()


if __name__ == "__main__":
    main()
