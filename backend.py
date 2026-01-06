"""
Backend API для работы с сущностями системы бронирования столов.
Предоставляет CRUD операции для User, Table и Booking.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from postgres_driver import PostgresDriver
from models import User, Table, Booking


class Backend:
    """Backend класс для работы с сущностями системы бронирования."""
    
    def __init__(self):
        """Инициализация backend с подключением к базе данных."""
        self.db = PostgresDriver()
    
    def close(self):
        """Закрыть соединение с базой данных."""
        if self.db:
            self.db.close()
    
    # ==================== USER CRUD ====================
    
    def create_user(self, name: str, phone: str, email: str) -> User:
        """
        Создание нового пользователя.
        
        Args:
            name: Имя пользователя (должно быть уникальным)
            phone: Номер телефона
            email: Электронная почта
            
        Returns:
            Созданный объект User
            
        Raises:
            ValueError: Если пользователь с таким именем уже существует
        """
        # Проверка уникальности имени
        existing_user = self.get_user_by_name(name)
        if existing_user:
            raise ValueError(f"Пользователь с именем '{name}' уже существует")
        
        user = User(name=name, phone=phone, email=email)
        return self.db.create(user, table_name="user")
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Получение пользователя по ID.
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            Объект User или None, если не найден
        """
        return self.db.read_by_id(User, user_id, table_name="user")
    
    def get_all_users(self, filters: Optional[Dict] = None, 
                     order_by: Optional[str] = None) -> List[User]:
        """
        Получение всех пользователей.
        
        Args:
            filters: Словарь с условиями фильтрации {поле: значение}
            order_by: Поле для сортировки (например, "name", "created_at")
            
        Returns:
            Список объектов User
        """
        return self.db.read(User, table_name="user", filters=filters, order_by=order_by)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Получение пользователя по email.
        
        Args:
            email: Электронная почта
            
        Returns:
            Объект User или None, если не найден
        """
        users = self.db.read(User, table_name="user", filters={"email": email}, limit=1)
        return users[0] if users else None
    
    def get_user_by_name(self, name: str) -> Optional[User]:
        """
        Получение пользователя по имени.
        
        Args:
            name: Имя пользователя
            
        Returns:
            Объект User или None, если не найден
        """
        users = self.db.read(User, table_name="user", filters={"name": name}, limit=1)
        return users[0] if users else None
    
    def update_user(self, user: User, 
                   update_fields: Optional[List[str]] = None) -> User:
        """
        Обновление пользователя.
        
        Args:
            user: Объект User с обновленными данными
            update_fields: Список полей для обновления (если None, обновляются все кроме id и created_at)
            
        Returns:
            Обновленный объект User
            
        Raises:
            ValueError: Если пользователь с таким именем уже существует (при изменении имени)
        """
        # Проверка уникальности имени, если имя изменяется
        if update_fields is None or 'name' in update_fields:
            existing_user = self.get_user_by_name(user.name)
            if existing_user and existing_user.id != user.id:
                raise ValueError(f"Пользователь с именем '{user.name}' уже существует")
        
        return self.db.update(user, table_name="user", update_fields=update_fields)
    
    def delete_user(self, user_id: UUID) -> bool:
        """
        Удаление пользователя.
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            True если пользователь удален успешно
        """
        return self.db.delete(user_id, table_name="user")
    
    # ==================== TABLE CRUD ====================
    
    def create_table(self, number: int, capacity: int, 
                    location: str, is_available: bool = True) -> Table:
        """
        Создание нового стола.
        
        Args:
            number: Номер стола (должен быть уникальным)
            capacity: Вместимость стола
            location: Локация ("window", "corner", "center")
            is_available: Доступность стола
            
        Returns:
            Созданный объект Table
            
        Raises:
            ValueError: Если стол с таким номером уже существует
        """
        # Проверка уникальности номера стола
        existing_table = self.get_table_by_number(number)
        if existing_table:
            raise ValueError(f"Стол с номером {number} уже существует")
        
        table = Table(number=number, capacity=capacity, 
                     location=location, is_available=is_available)
        return self.db.create(table, table_name="restaurant_table")
    
    def get_table_by_id(self, table_id: UUID) -> Optional[Table]:
        """
        Получение стола по ID.
        
        Args:
            table_id: UUID стола
            
        Returns:
            Объект Table или None, если не найден
        """
        return self.db.read_by_id(Table, table_id, table_name="restaurant_table")
    
    def get_all_tables(self, filters: Optional[Dict] = None,
                      order_by: Optional[str] = None) -> List[Table]:
        """
        Получение всех столов.
        
        Args:
            filters: Словарь с условиями фильтрации {поле: значение}
            order_by: Поле для сортировки (например, "number", "capacity")
            
        Returns:
            Список объектов Table
        """
        return self.db.read(Table, table_name="restaurant_table", 
                          filters=filters, order_by=order_by)
    
    def get_table_by_number(self, number: int) -> Optional[Table]:
        """
        Получение стола по номеру.
        
        Args:
            number: Номер стола
            
        Returns:
            Объект Table или None, если не найден
        """
        tables = self.db.read(Table, table_name="restaurant_table", 
                            filters={"number": number}, limit=1)
        return tables[0] if tables else None
    
    def get_available_tables(self, capacity: Optional[int] = None,
                            location: Optional[str] = None) -> List[Table]:
        """
        Получение доступных столов с опциональной фильтрацией.
        
        Args:
            capacity: Минимальная вместимость стола
            location: Локация стола
            
        Returns:
            Список доступных объектов Table
        """
        filters = {"is_available": True}
        if location:
            filters["location"] = location
        
        tables = self.get_all_tables(filters=filters, order_by="number")
        
        # Фильтруем по вместимости, если указана
        if capacity:
            tables = [t for t in tables if t.capacity >= capacity]
        
        return tables
    
    def update_table(self, table: Table,
                    update_fields: Optional[List[str]] = None) -> Table:
        """
        Обновление стола.
        
        Args:
            table: Объект Table с обновленными данными
            update_fields: Список полей для обновления
            
        Returns:
            Обновленный объект Table
            
        Raises:
            ValueError: Если стол с таким номером уже существует (при изменении номера)
        """
        # Проверка уникальности номера, если номер изменяется
        if update_fields is None or 'number' in update_fields:
            existing_table = self.get_table_by_number(table.number)
            if existing_table and existing_table.id != table.id:
                raise ValueError(f"Стол с номером {table.number} уже существует")
        
        return self.db.update(table, table_name="restaurant_table", 
                            update_fields=update_fields)
    
    def delete_table(self, table_id: UUID) -> bool:
        """
        Удаление стола.
        
        Args:
            table_id: UUID стола
            
        Returns:
            True если стол удален успешно
        """
        return self.db.delete(table_id, table_name="restaurant_table")
    
    # ==================== BOOKING CRUD ====================
    
    def create_booking(self, user_id: UUID, table_id: UUID, 
                     booking_date: datetime, guest_count: int,
                     duration_minutes: int = 120,
                     status: str = "pending",
                     special_requests: str = "",
                     check_availability: bool = True) -> Booking:
        """
        Создание нового бронирования.
        
        Args:
            user_id: UUID пользователя
            table_id: UUID стола
            booking_date: Дата и время бронирования
            guest_count: Количество гостей
            duration_minutes: Длительность бронирования в минутах
            status: Статус бронирования ("pending", "confirmed", "cancelled")
            special_requests: Пожелания клиента
            check_availability: Проверять доступность стола перед созданием
            
        Returns:
            Созданный объект Booking
            
        Raises:
            ValueError: Если стол недоступен на указанное время
        """
        # Проверяем доступность стола
        if check_availability:
            is_available, reason = self.check_table_availability(
                table_id=table_id,
                booking_date=booking_date,
                duration_minutes=duration_minutes
            )
            if not is_available:
                raise ValueError(f"Невозможно создать бронирование: {reason}")
        
        booking = Booking(
            user_id=user_id,
            table_id=table_id,
            booking_date=booking_date,
            guest_count=guest_count,
            duration_minutes=duration_minutes,
            status=status,
            special_requests=special_requests
        )
        return self.db.create(booking, table_name="booking")
    
    def get_booking_by_id(self, booking_id: UUID) -> Optional[Booking]:
        """
        Получение бронирования по ID.
        
        Args:
            booking_id: UUID бронирования
            
        Returns:
            Объект Booking или None, если не найдено
        """
        return self.db.read_by_id(Booking, booking_id, table_name="booking")
    
    def get_all_bookings(self, filters: Optional[Dict] = None,
                        order_by: Optional[str] = None) -> List[Booking]:
        """
        Получение всех бронирований.
        
        Args:
            filters: Словарь с условиями фильтрации {поле: значение}
            order_by: Поле для сортировки (например, "booking_date", "created_at")
            
        Returns:
            Список объектов Booking
        """
        return self.db.read(Booking, table_name="booking", 
                          filters=filters, order_by=order_by)
    
    def get_bookings_by_user(self, user_id: UUID) -> List[Booking]:
        """
        Получение всех бронирований пользователя.
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            Список объектов Booking пользователя, отсортированных по дате
        """
        return self.get_all_bookings(filters={"user_id": user_id}, 
                                    order_by="booking_date")
    
    def get_bookings_by_table(self, table_id: UUID) -> List[Booking]:
        """
        Получение всех бронирований стола.
        
        Args:
            table_id: UUID стола
            
        Returns:
            Список объектов Booking стола, отсортированных по дате
        """
        return self.get_all_bookings(filters={"table_id": table_id}, 
                                    order_by="booking_date")
    
    def get_bookings_by_date_range(self, start_date: datetime, 
                                  end_date: datetime) -> List[Booking]:
        """
        Получение бронирований в указанном диапазоне дат.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Список объектов Booking в указанном диапазоне
        """
        # Используем прямой SQL запрос для диапазона дат
        query = """
            SELECT * FROM "booking"
            WHERE booking_date >= %s AND booking_date <= %s
            ORDER BY booking_date;
        """
        results = self.db.execute_query(query, params=(start_date, end_date))
        
        # Преобразуем результаты в объекты Booking
        bookings = []
        for row in results:
            booking = Booking(
                user_id=UUID(row['user_id']),
                table_id=UUID(row['table_id']),
                booking_date=row['booking_date'],
                guest_count=row['guest_count'],
                id=UUID(row['id']),
                duration_minutes=row.get('duration_minutes', 120),
                status=row.get('status', 'pending'),
                special_requests=row.get('special_requests', ''),
                created_at=row.get('created_at'),
                updated_at=row.get('updated_at')
            )
            bookings.append(booking)
        
        return bookings
    
    def update_booking(self, booking: Booking,
                      update_fields: Optional[List[str]] = None,
                      check_availability: bool = True) -> Booking:
        """
        Обновление бронирования.
        
        Args:
            booking: Объект Booking с обновленными данными
            update_fields: Список полей для обновления (если None, обновляются все кроме id и created_at)
            check_availability: Проверять доступность стола при изменении времени или стола
            
        Returns:
            Обновленный объект Booking
            
        Raises:
            ValueError: Если стол недоступен на указанное время
        """
        # Проверяем доступность, если изменяются время или стол
        if check_availability and booking.id:
            # Проверяем, изменяются ли время или стол
            existing_booking = self.get_booking_by_id(booking.id)
            if existing_booking:
                time_changed = (
                    existing_booking.booking_date != booking.booking_date or
                    existing_booking.duration_minutes != booking.duration_minutes
                )
                table_changed = existing_booking.table_id != booking.table_id
                
                if time_changed or table_changed:
                    is_available, reason = self.check_table_availability(
                        table_id=booking.table_id,
                        booking_date=booking.booking_date,
                        duration_minutes=booking.duration_minutes,
                        exclude_booking_id=booking.id
                    )
                    if not is_available:
                        raise ValueError(f"Невозможно обновить бронирование: {reason}")
        
        # Автоматически обновляем updated_at
        booking.updated_at = datetime.now()
        
        # Добавляем updated_at к списку полей для обновления
        if update_fields is None:
            # Если не указаны поля, обновляем все кроме id и created_at
            update_fields = None  # db.update сам определит поля
        else:
            # Если указаны поля, добавляем updated_at если его нет
            if 'updated_at' not in update_fields:
                update_fields = update_fields.copy()
                update_fields.append('updated_at')
        
        return self.db.update(booking, table_name="booking", 
                            update_fields=update_fields)
    
    def delete_booking(self, booking_id: UUID) -> bool:
        """
        Удаление бронирования.
        
        Args:
            booking_id: UUID бронирования
            
        Returns:
            True если бронирование удалено успешно
        """
        return self.db.delete(booking_id, table_name="booking")
    
    def confirm_booking(self, booking_id: UUID) -> Optional[Booking]:
        """
        Подтверждение бронирования.
        
        Args:
            booking_id: UUID бронирования
            
        Returns:
            Обновленный объект Booking или None, если не найдено
        """
        booking = self.get_booking_by_id(booking_id)
        if booking:
            booking.status = "confirmed"
            return self.update_booking(booking, update_fields=["status"])
        return None
    
    def cancel_booking(self, booking_id: UUID) -> Optional[Booking]:
        """
        Отмена бронирования.
        
        Args:
            booking_id: UUID бронирования
            
        Returns:
            Обновленный объект Booking или None, если не найдено
        """
        booking = self.get_booking_by_id(booking_id)
        if booking:
            booking.status = "cancelled"
            return self.update_booking(booking, update_fields=["status"])
        return None
    
    def check_table_availability(self, table_id: UUID, booking_date: datetime,
                                duration_minutes: int, exclude_booking_id: Optional[UUID] = None) -> Tuple[bool, Optional[str]]:
        """
        Проверка доступности стола на указанное время.
        Запрещает пересекающиеся бронирования по одному столу.
        
        Args:
            table_id: UUID стола для проверки
            booking_date: Дата и время начала бронирования
            duration_minutes: Длительность бронирования в минутах
            exclude_booking_id: UUID бронирования, которое исключается из проверки 
                              (используется при обновлении существующего бронирования)
        
        Returns:
            Кортеж (is_available: bool, reason: Optional[str])
            - is_available: True если стол доступен, False если занят
            - reason: Причина недоступности (если is_available == False)
        """
        from datetime import timedelta
        
        # Проверяем существование стола
        table = self.get_table_by_id(table_id)
        if not table:
            return False, "Стол не найден"
        
        # Проверяем общую доступность стола
        if not table.is_available:
            return False, "Стол недоступен для бронирования"
        
        # Вычисляем время окончания бронирования
        booking_end = booking_date + timedelta(minutes=duration_minutes)
        
        # Получаем все активные бронирования для этого стола
        # Исключаем отмененные бронирования
        all_bookings = self.get_bookings_by_table(table_id)
        active_bookings = [
            b for b in all_bookings 
            if b.status in ("pending", "confirmed") and b.id != exclude_booking_id
        ]
        
        # Проверяем пересечения с существующими бронированиями
        for existing_booking in active_bookings:
            existing_start = existing_booking.booking_date
            existing_end = existing_booking.booking_date + timedelta(
                minutes=existing_booking.duration_minutes
            )
            
            # Проверка пересечения временных интервалов
            # Два интервала пересекаются, если:
            # start_new < end_existing AND start_existing < end_new
            if booking_date < existing_end and existing_start < booking_end:
                # Найдено пересечение
                existing_start_str = existing_start.strftime("%d.%m.%Y %H:%M")
                existing_end_str = existing_end.strftime("%H:%M")
                reason = (
                    f"Стол уже забронирован с {existing_start_str} до {existing_end_str} "
                    f"(бронирование #{existing_booking.id.hex[:8]}, статус: {existing_booking.status})"
                )
                return False, reason
        
        # Стол доступен
        return True, None

