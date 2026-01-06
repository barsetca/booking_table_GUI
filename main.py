"""
Главный файл для запуска GUI приложения системы бронирования столов.
"""

import tkinter as tk
from frontend_gui import BookingApp


def main():
    """Запуск приложения."""
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

