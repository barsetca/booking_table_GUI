"""
GUI приложение для системы бронирования столов в ресторане.
Использует tkinter для создания интерфейса.
"""

import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional
from uuid import UUID

from backend import Backend
from models import User, Table, Booking


class BookingApp:
    """Главное приложение для работы с системой бронирования."""
    
    def __init__(self, root: tk.Tk):
        """Инициализация приложения."""
        self.root = root
        self.root.title("Система бронирования столов")
        self.root.geometry("1000x700")
        
        # Инициализация backend
        try:
            self.backend = Backend()
        except Exception as e:
            messagebox.showerror("Ошибка подключения", 
                                f"Не удалось подключиться к базе данных:\n{e}")
            root.destroy()
            return
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка начальных данных
        self.refresh_all()
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Создание виджетов интерфейса."""
        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка пользователей
        self.create_users_tab()
        
        # Вкладка столов
        self.create_tables_tab()
        
        # Вкладка бронирований
        self.create_bookings_tab()
    
    def create_users_tab(self):
        """Создание вкладки пользователей."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Пользователи")
        
        # Левая панель - форма
        left_frame = ttk.LabelFrame(frame, text="Форма пользователя", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Поля формы
        ttk.Label(left_frame, text="Имя:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.user_name_entry = ttk.Entry(left_frame, width=30)
        self.user_name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Телефон:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_phone_entry = ttk.Entry(left_frame, width=30)
        self.user_phone_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.user_email_entry = ttk.Entry(left_frame, width=30)
        self.user_email_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Кнопки
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Создать", command=self.create_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_user_form).pack(side=tk.LEFT, padx=5)
        
        # Правая панель - список
        right_frame = ttk.LabelFrame(frame, text="Список пользователей", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица пользователей
        columns = ("Имя", "Телефон", "Email", "Создан")
        self.users_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=150)
        
        self.users_tree.pack(fill=tk.BOTH, expand=True)
        self.users_tree.bind("<Double-1>", self.on_user_select)
        
        # Кнопки для списка
        list_btn_frame = ttk.Frame(right_frame)
        list_btn_frame.pack(pady=5)
        
        ttk.Button(list_btn_frame, text="Обновить", command=self.refresh_users).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_btn_frame, text="Удалить", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        
        self.selected_user_id = None
    
    def create_tables_tab(self):
        """Создание вкладки столов."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Столы")
        
        # Левая панель - форма
        left_frame = ttk.LabelFrame(frame, text="Форма стола", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Поля формы
        ttk.Label(left_frame, text="Номер:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.table_number_entry = ttk.Entry(left_frame, width=30)
        self.table_number_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Вместимость:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.table_capacity_entry = ttk.Entry(left_frame, width=30)
        self.table_capacity_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Локация:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.table_location_combo = ttk.Combobox(left_frame, values=["window", "corner", "center"], 
                                                 width=27, state="readonly")
        self.table_location_combo.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Доступен:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.table_available_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(left_frame, variable=self.table_available_var).grid(row=3, column=1, 
                                                                           sticky=tk.W, pady=5, padx=5)
        
        # Кнопки
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Создать", command=self.create_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_table_form).pack(side=tk.LEFT, padx=5)
        
        # Правая панель - список
        right_frame = ttk.LabelFrame(frame, text="Список столов", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица столов
        columns = ("Номер", "Вместимость", "Локация", "Доступен")
        self.tables_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tables_tree.heading(col, text=col)
            self.tables_tree.column(col, width=150)
        
        self.tables_tree.pack(fill=tk.BOTH, expand=True)
        self.tables_tree.bind("<Double-1>", self.on_table_select)
        
        # Кнопки для списка
        list_btn_frame = ttk.Frame(right_frame)
        list_btn_frame.pack(pady=5)
        
        ttk.Button(list_btn_frame, text="Обновить", command=self.refresh_tables).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_btn_frame, text="Удалить", command=self.delete_table).pack(side=tk.LEFT, padx=5)
        
        self.selected_table_id = None
    
    def create_bookings_tab(self):
        """Создание вкладки бронирований."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Бронирования")
        
        # Левая панель - форма
        left_frame = ttk.LabelFrame(frame, text="Форма бронирования", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Поля формы
        ttk.Label(left_frame, text="Пользователь:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.booking_user_combo = ttk.Combobox(left_frame, width=27, state="readonly")
        self.booking_user_combo.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Стол:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.booking_table_combo = ttk.Combobox(left_frame, width=27, state="readonly")
        self.booking_table_combo.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Дата и время:").grid(row=2, column=0, sticky=tk.W, pady=5)
        datetime_frame = ttk.Frame(left_frame)
        datetime_frame.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.booking_date_entry = ttk.Entry(datetime_frame, width=12)
        self.booking_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.booking_date_entry.pack(side=tk.LEFT, padx=2)
        
        self.booking_time_entry = ttk.Entry(datetime_frame, width=10)
        self.booking_time_entry.insert(0, (datetime.now() + timedelta(hours=1)).strftime("%H:%M"))
        self.booking_time_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(left_frame, text="Количество гостей:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.booking_guests_entry = ttk.Entry(left_frame, width=30)
        self.booking_guests_entry.grid(row=3, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Длительность (мин):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.booking_duration_entry = ttk.Entry(left_frame, width=30)
        self.booking_duration_entry.insert(0, "120")
        self.booking_duration_entry.grid(row=4, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Статус:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.booking_status_combo = ttk.Combobox(left_frame, values=["pending", "confirmed", "cancelled"], 
                                                 width=27, state="readonly")
        self.booking_status_combo.set("pending")
        self.booking_status_combo.grid(row=5, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Пожелания:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.booking_requests_text = scrolledtext.ScrolledText(left_frame, width=30, height=3)
        self.booking_requests_text.grid(row=6, column=1, pady=5, padx=5)
        
        # Кнопки
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Проверить доступность", 
                  command=self.check_availability).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Показать доступные столы", 
                  command=self.show_available_tables).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Создать", command=self.create_booking).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_booking).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_booking_form).pack(side=tk.LEFT, padx=5)
        
        # Правая панель - список
        right_frame = ttk.LabelFrame(frame, text="Список бронирований", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица бронирований
        columns = ("Стол", "Локация", "Пользователь", "Дата", "Гостей", "Статус")
        self.bookings_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.bookings_tree.heading(col, text=col)
            self.bookings_tree.column(col, width=120)
        
        self.bookings_tree.pack(fill=tk.BOTH, expand=True)
        self.bookings_tree.bind("<Double-1>", self.on_booking_select)
        
        # Кнопки для списка
        list_btn_frame = ttk.Frame(right_frame)
        list_btn_frame.pack(pady=5)
        
        ttk.Button(list_btn_frame, text="Обновить", command=self.refresh_bookings).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_btn_frame, text="Подтвердить", command=self.confirm_booking).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_btn_frame, text="Отменить", command=self.cancel_booking_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_btn_frame, text="Удалить", command=self.delete_booking).pack(side=tk.LEFT, padx=5)
        
        self.selected_booking_id = None
    
    # ==================== USER METHODS ====================
    
    def create_user(self):
        """Создание пользователя."""
        try:
            name = self.user_name_entry.get().strip()
            phone = self.user_phone_entry.get().strip()
            email = self.user_email_entry.get().strip()
            
            if not all([name, phone, email]):
                messagebox.showwarning("Предупреждение", "Заполните все поля")
                return
            
            user = self.backend.create_user(name, phone, email)
            messagebox.showinfo("Успех", f"Пользователь {user.name} создан")
            self.clear_user_form()
            self.refresh_users()
            self.load_booking_combos()  # Обновляем список пользователей в комбобоксе бронирований
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать пользователя:\n{e}")
    
    def update_user(self):
        """Обновление пользователя."""
        if not self.selected_user_id:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для обновления")
            return
        
        try:
            user = self.backend.get_user_by_id(self.selected_user_id)
            if not user:
                messagebox.showerror("Ошибка", "Пользователь не найден")
                return
            
            user.name = self.user_name_entry.get().strip()
            user.phone = self.user_phone_entry.get().strip()
            user.email = self.user_email_entry.get().strip()
            
            if not all([user.name, user.phone, user.email]):
                messagebox.showwarning("Предупреждение", "Заполните все поля")
                return
            
            self.backend.update_user(user)
            messagebox.showinfo("Успех", "Пользователь обновлен")
            self.clear_user_form()
            self.refresh_users()
            self.load_booking_combos()  # Обновляем список пользователей в комбобоксе бронирований
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить пользователя:\n{e}")
    
    def delete_user(self):
        """Удаление пользователя."""
        if not self.selected_user_id:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранного пользователя?"):
            try:
                self.backend.delete_user(self.selected_user_id)
                messagebox.showinfo("Успех", "Пользователь удален")
                self.clear_user_form()
                self.refresh_users()
                self.load_booking_combos()  # Обновляем список пользователей в комбобоксе бронирований
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить пользователя:\n{e}")
    
    def on_user_select(self, event):
        """Обработка выбора пользователя."""
        selection = self.users_tree.selection()
        if selection:
            item = self.users_tree.item(selection[0])
            user_name = item['values'][0]  # Первое значение - имя
            try:
                user = self.backend.get_user_by_name(user_name)
                if user:
                    self.selected_user_id = user.id
                    self.user_name_entry.delete(0, tk.END)
                    self.user_name_entry.insert(0, user.name)
                    self.user_phone_entry.delete(0, tk.END)
                    self.user_phone_entry.insert(0, user.phone)
                    self.user_email_entry.delete(0, tk.END)
                    self.user_email_entry.insert(0, user.email)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить пользователя:\n{e}")
    
    def clear_user_form(self):
        """Очистка формы пользователя."""
        self.user_name_entry.delete(0, tk.END)
        self.user_phone_entry.delete(0, tk.END)
        self.user_email_entry.delete(0, tk.END)
        self.selected_user_id = None
        self.users_tree.selection_remove(self.users_tree.selection())
    
    def refresh_users(self):
        """Обновление списка пользователей."""
        try:
            # Очистка таблицы
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            # Загрузка данных
            users = self.backend.get_all_users(order_by="name")
            for user in users:
                self.users_tree.insert("", tk.END, values=(
                    user.name,
                    user.phone,
                    user.email,
                    user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else ""
                ), tags=(str(user.id),))  # Сохраняем ID в тегах для доступа
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей:\n{e}")
    
    # ==================== TABLE METHODS ====================
    
    def create_table(self):
        """Создание стола."""
        try:
            number = int(self.table_number_entry.get().strip())
            capacity = int(self.table_capacity_entry.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Номер и вместимость должны быть числами")
            return
        
        try:
            location = self.table_location_combo.get()
            is_available = self.table_available_var.get()
            
            if not location:
                messagebox.showwarning("Предупреждение", "Выберите локацию")
                return
            
            table = self.backend.create_table(number, capacity, location, is_available)
            messagebox.showinfo("Успех", f"Стол №{table.number} создан")
            self.clear_table_form()
            self.refresh_tables()
            self.load_booking_combos()  # Обновляем список столов в комбобоксе бронирований
        except ValueError as e:
            # Ошибка от backend (например, дублирующийся номер)
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать стол:\n{e}")
    
    def update_table(self):
        """Обновление стола."""
        if not self.selected_table_id:
            messagebox.showwarning("Предупреждение", "Выберите стол для обновления")
            return
        
        try:
            table = self.backend.get_table_by_id(self.selected_table_id)
            if not table:
                messagebox.showerror("Ошибка", "Стол не найден")
                return
            
            try:
                table.number = int(self.table_number_entry.get().strip())
                table.capacity = int(self.table_capacity_entry.get().strip())
            except ValueError:
                messagebox.showerror("Ошибка", "Номер и вместимость должны быть числами")
                return
            
            table.location = self.table_location_combo.get()
            table.is_available = self.table_available_var.get()
            
            self.backend.update_table(table)
            messagebox.showinfo("Успех", "Стол обновлен")
            self.clear_table_form()
            self.refresh_tables()
            self.load_booking_combos()  # Обновляем список столов в комбобоксе бронирований
        except ValueError as e:
            # Ошибка от backend (например, дублирующийся номер)
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить стол:\n{e}")
    
    def delete_table(self):
        """Удаление стола."""
        if not self.selected_table_id:
            messagebox.showwarning("Предупреждение", "Выберите стол для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный стол?"):
            try:
                self.backend.delete_table(self.selected_table_id)
                messagebox.showinfo("Успех", "Стол удален")
                self.clear_table_form()
                self.refresh_tables()
                self.load_booking_combos()  # Обновляем список столов в комбобоксе бронирований
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить стол:\n{e}")
    
    def on_table_select(self, event):
        """Обработка выбора стола."""
        selection = self.tables_tree.selection()
        if selection:
            item = self.tables_tree.item(selection[0])
            table_number = int(item['values'][0])  # Первое значение - номер
            try:
                table = self.backend.get_table_by_number(table_number)
                if table:
                    self.selected_table_id = table.id
                    self.table_number_entry.delete(0, tk.END)
                    self.table_number_entry.insert(0, str(table.number))
                    self.table_capacity_entry.delete(0, tk.END)
                    self.table_capacity_entry.insert(0, str(table.capacity))
                    self.table_location_combo.set(table.location)
                    self.table_available_var.set(table.is_available)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить стол:\n{e}")
    
    def clear_table_form(self):
        """Очистка формы стола."""
        self.table_number_entry.delete(0, tk.END)
        self.table_capacity_entry.delete(0, tk.END)
        self.table_location_combo.set("")
        self.table_available_var.set(True)
        self.selected_table_id = None
        self.tables_tree.selection_remove(self.tables_tree.selection())
    
    def refresh_tables(self):
        """Обновление списка столов."""
        try:
            # Очистка таблицы
            for item in self.tables_tree.get_children():
                self.tables_tree.delete(item)
            
            # Загрузка данных
            tables = self.backend.get_all_tables(order_by="number")
            for table in tables:
                self.tables_tree.insert("", tk.END, values=(
                    table.number,
                    table.capacity,
                    table.location,
                    "Да" if table.is_available else "Нет"
                ), tags=(str(table.id),))  # Сохраняем ID в тегах для доступа
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить столы:\n{e}")
    
    # ==================== BOOKING METHODS ====================
    
    def check_availability(self):
        """Проверка доступности стола."""
        try:
            table_number_str = self.booking_table_combo.get().strip()
            if not table_number_str:
                messagebox.showwarning("Предупреждение", "Выберите стол")
                return
            
            # Находим стол по номеру
            try:
                table_number = int(table_number_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат номера стола")
                return
            
            table = self.backend.get_table_by_number(table_number)
            if not table:
                messagebox.showerror("Ошибка", f"Стол №{table_number} не найден")
                return
            
            table_id = table.id
            
            date_str = self.booking_date_entry.get().strip()
            time_str = self.booking_time_entry.get().strip()
            duration_str = self.booking_duration_entry.get().strip() or "120"
            
            booking_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            duration_minutes = int(duration_str)
            
            is_available, reason = self.backend.check_table_availability(
                table_id=table_id,
                booking_date=booking_date,
                duration_minutes=duration_minutes,
                exclude_booking_id=self.selected_booking_id
            )
            
            if is_available:
                messagebox.showinfo("Доступность", "Стол доступен на указанное время!")
            else:
                messagebox.showwarning("Недоступно", f"Стол недоступен:\n{reason}")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных:\n{e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось проверить доступность:\n{e}")
    
    def show_available_tables(self):
        """Показать доступные столы на указанное время."""
        try:
            date_str = self.booking_date_entry.get().strip()
            time_str = self.booking_time_entry.get().strip()
            duration_str = self.booking_duration_entry.get().strip() or "120"
            
            if not date_str or not time_str:
                messagebox.showwarning("Предупреждение", "Укажите дату и время для проверки доступности")
                return
            
            booking_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            duration_minutes = int(duration_str)
            
            # Получаем все столы
            all_tables = self.backend.get_all_tables(order_by="number")
            available_tables = []
            
            for table in all_tables:
                if not table.is_available:
                    continue
                
                # Проверяем доступность
                is_available, _ = self.backend.check_table_availability(
                    table_id=table.id,
                    booking_date=booking_date,
                    duration_minutes=duration_minutes
                )
                
                if is_available:
                    available_tables.append(table)
            
            # Создаем окно с результатами
            result_window = tk.Toplevel(self.root)
            result_window.title("Доступные столы")
            result_window.geometry("500x400")
            
            # Заголовок
            info_label = ttk.Label(result_window, 
                                  text=f"Доступные столы на {booking_date.strftime('%d.%m.%Y %H:%M')} "
                                       f"(длительность: {duration_minutes} мин)",
                                  font=("Arial", 10, "bold"))
            info_label.pack(pady=10)
            
            # Таблица с результатами
            columns = ("Номер", "Вместимость", "Локация")
            result_tree = ttk.Treeview(result_window, columns=columns, show="headings", height=15)
            
            for col in columns:
                result_tree.heading(col, text=col)
                result_tree.column(col, width=150)
            
            result_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Заполняем таблицу
            if available_tables:
                for table in available_tables:
                    result_tree.insert("", tk.END, values=(
                        table.number,
                        table.capacity,
                        table.location
                    ))
            else:
                result_tree.insert("", tk.END, values=("Нет доступных столов", "", ""))
            
            # Кнопка закрытия
            ttk.Button(result_window, text="Закрыть", command=result_window.destroy).pack(pady=10)
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных:\n{e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось показать доступные столы:\n{e}")
    
    def create_booking(self):
        """Создание бронирования."""
        try:
            user_name = self.booking_user_combo.get().strip()
            table_number_str = self.booking_table_combo.get().strip()
            
            if not user_name or not table_number_str:
                messagebox.showwarning("Предупреждение", "Выберите пользователя и стол")
                return
            
            # Находим пользователя по имени
            user = self.backend.get_user_by_name(user_name)
            if not user:
                messagebox.showerror("Ошибка", f"Пользователь '{user_name}' не найден")
                return
            
            # Находим стол по номеру
            try:
                table_number = int(table_number_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат номера стола")
                return
            
            table = self.backend.get_table_by_number(table_number)
            if not table:
                messagebox.showerror("Ошибка", f"Стол №{table_number} не найден")
                return
            
            user_id = user.id
            table_id = table.id
            
            date_str = self.booking_date_entry.get().strip()
            time_str = self.booking_time_entry.get().strip()
            booking_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            guest_count = int(self.booking_guests_entry.get().strip())
            duration_minutes = int(self.booking_duration_entry.get().strip() or "120")
            status = self.booking_status_combo.get()
            special_requests = self.booking_requests_text.get("1.0", tk.END).strip()
            
            booking = self.backend.create_booking(
                user_id=user_id,
                table_id=table_id,
                booking_date=booking_date,
                guest_count=guest_count,
                duration_minutes=duration_minutes,
                status=status,
                special_requests=special_requests
            )
            
            messagebox.showinfo("Успех", f"Бронирование создано (ID: {str(booking.id)[:8]})")
            self.clear_booking_form()
            self.refresh_bookings()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных:\n{e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать бронирование:\n{e}")
    
    def update_booking(self):
        """Обновление бронирования."""
        if not self.selected_booking_id:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для обновления")
            return
        
        try:
            booking = self.backend.get_booking_by_id(self.selected_booking_id)
            if not booking:
                messagebox.showerror("Ошибка", "Бронирование не найдено")
                return
            
            user_name = self.booking_user_combo.get().strip()
            table_number_str = self.booking_table_combo.get().strip()
            
            # Находим пользователя по имени
            user = self.backend.get_user_by_name(user_name)
            if not user:
                messagebox.showerror("Ошибка", f"Пользователь '{user_name}' не найден")
                return
            
            # Находим стол по номеру
            try:
                table_number = int(table_number_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат номера стола")
                return
            
            table = self.backend.get_table_by_number(table_number)
            if not table:
                messagebox.showerror("Ошибка", f"Стол №{table_number} не найден")
                return
            
            booking.user_id = user.id
            booking.table_id = table.id
            
            date_str = self.booking_date_entry.get().strip()
            time_str = self.booking_time_entry.get().strip()
            booking.booking_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            booking.guest_count = int(self.booking_guests_entry.get().strip())
            booking.duration_minutes = int(self.booking_duration_entry.get().strip() or "120")
            booking.status = self.booking_status_combo.get()
            booking.special_requests = self.booking_requests_text.get("1.0", tk.END).strip()
            
            self.backend.update_booking(booking)
            messagebox.showinfo("Успех", "Бронирование обновлено")
            self.clear_booking_form()
            self.refresh_bookings()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных:\n{e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить бронирование:\n{e}")
    
    def delete_booking(self):
        """Удаление бронирования."""
        if not self.selected_booking_id:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранное бронирование?"):
            try:
                self.backend.delete_booking(self.selected_booking_id)
                messagebox.showinfo("Успех", "Бронирование удалено")
                self.clear_booking_form()
                self.refresh_bookings()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить бронирование:\n{e}")
    
    def confirm_booking(self):
        """Подтверждение бронирования."""
        if not self.selected_booking_id:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для подтверждения")
            return
        
        try:
            booking = self.backend.confirm_booking(self.selected_booking_id)
            if booking:
                messagebox.showinfo("Успех", "Бронирование подтверждено")
                self.refresh_bookings()
            else:
                messagebox.showerror("Ошибка", "Бронирование не найдено")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подтвердить бронирование:\n{e}")
    
    def cancel_booking_ui(self):
        """Отмена бронирования."""
        if not self.selected_booking_id:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для отмены")
            return
        
        if messagebox.askyesno("Подтверждение", "Отменить выбранное бронирование?"):
            try:
                booking = self.backend.cancel_booking(self.selected_booking_id)
                if booking:
                    messagebox.showinfo("Успех", "Бронирование отменено")
                    self.refresh_bookings()
                else:
                    messagebox.showerror("Ошибка", "Бронирование не найдено")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось отменить бронирование:\n{e}")
    
    def on_booking_select(self, event):
        """Обработка выбора бронирования."""
        selection = self.bookings_tree.selection()
        if selection:
            item = self.bookings_tree.item(selection[0])
            # Получаем ID из тегов (первый тег)
            tags = item.get('tags', [])
            if tags:
                booking_id_str = tags[0]
            else:
                # Fallback: пытаемся найти по другим данным
                table_number_str = item['values'][0].replace("№", "")
                booking_date_str = item['values'][3]
                # Найдем бронирование по таблице и дате
                try:
                    table_number = int(table_number_str)
                    table = self.backend.get_table_by_number(table_number)
                    if table:
                        bookings = self.backend.get_bookings_by_table(table.id)
                        booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d %H:%M")
                        for b in bookings:
                            if b.booking_date == booking_date:
                                booking_id_str = str(b.id)
                                break
                        else:
                            messagebox.showerror("Ошибка", "Бронирование не найдено")
                            return
                    else:
                        messagebox.showerror("Ошибка", "Стол не найден")
                        return
                except:
                    messagebox.showerror("Ошибка", "Не удалось определить бронирование")
                    return
            
            try:
                self.selected_booking_id = UUID(booking_id_str)
                booking = self.backend.get_booking_by_id(self.selected_booking_id)
                if booking:
                    # Заполняем форму
                    user = self.backend.get_user_by_id(booking.user_id)
                    table = self.backend.get_table_by_id(booking.table_id)
                    
                    if user:
                        self.booking_user_combo.set(user.name)
                    if table:
                        self.booking_table_combo.set(str(table.number))
                    
                    self.booking_date_entry.delete(0, tk.END)
                    self.booking_date_entry.insert(0, booking.booking_date.strftime("%Y-%m-%d"))
                    self.booking_time_entry.delete(0, tk.END)
                    self.booking_time_entry.insert(0, booking.booking_date.strftime("%H:%M"))
                    
                    self.booking_guests_entry.delete(0, tk.END)
                    self.booking_guests_entry.insert(0, str(booking.guest_count))
                    self.booking_duration_entry.delete(0, tk.END)
                    self.booking_duration_entry.insert(0, str(booking.duration_minutes))
                    self.booking_status_combo.set(booking.status)
                    
                    self.booking_requests_text.delete("1.0", tk.END)
                    self.booking_requests_text.insert("1.0", booking.special_requests)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить бронирование:\n{e}")
    
    def clear_booking_form(self):
        """Очистка формы бронирования."""
        self.booking_user_combo.set("")
        self.booking_table_combo.set("")
        self.booking_date_entry.delete(0, tk.END)
        self.booking_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.booking_time_entry.delete(0, tk.END)
        self.booking_time_entry.insert(0, (datetime.now() + timedelta(hours=1)).strftime("%H:%M"))
        self.booking_guests_entry.delete(0, tk.END)
        self.booking_duration_entry.delete(0, tk.END)
        self.booking_duration_entry.insert(0, "120")
        self.booking_status_combo.set("pending")
        self.booking_requests_text.delete("1.0", tk.END)
        self.selected_booking_id = None
        self.bookings_tree.selection_remove(self.bookings_tree.selection())
    
    def refresh_bookings(self):
        """Обновление списка бронирований."""
        try:
            # Очистка таблицы
            for item in self.bookings_tree.get_children():
                self.bookings_tree.delete(item)
            
            # Загрузка данных
            bookings = self.backend.get_all_bookings(order_by="booking_date")
            for booking in bookings:
                user = self.backend.get_user_by_id(booking.user_id)
                table = self.backend.get_table_by_id(booking.table_id)
                
                user_name = user.name if user else "N/A"
                table_number = f"№{table.number}" if table else "N/A"
                table_location = table.location if table else "N/A"
                
                self.bookings_tree.insert("", tk.END, values=(
                    table_number,  # Стол - первая колонка
                    table_location,  # Локация - вторая колонка
                    user_name,  # Пользователь - третья колонка
                    booking.booking_date.strftime("%Y-%m-%d %H:%M"),
                    booking.guest_count,
                    booking.status
                ), tags=(str(booking.id),))  # Сохраняем ID в тегах
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить бронирования:\n{e}")
    
    def refresh_all(self):
        """Обновление всех списков."""
        self.refresh_users()
        self.refresh_tables()
        self.refresh_bookings()
        self.load_booking_combos()
    
    def load_booking_combos(self):
        """Загрузка данных в комбобоксы бронирований."""
        try:
            # Загрузка пользователей - показываем только имена
            users = self.backend.get_all_users(order_by="name")
            user_values = [user.name for user in users]
            self.booking_user_combo['values'] = user_values
            
            # Загрузка столов - показываем только номера
            tables = self.backend.get_all_tables(order_by="number")
            table_values = [str(table.number) for table in tables]
            self.booking_table_combo['values'] = table_values
        except Exception as e:
            print(f"Ошибка загрузки комбобоксов: {e}")
    
    def on_closing(self):
        """Обработка закрытия приложения."""
        if messagebox.askokcancel("Выход", "Закрыть приложение?"):
            if hasattr(self, 'backend'):
                self.backend.close()
            self.root.destroy()

