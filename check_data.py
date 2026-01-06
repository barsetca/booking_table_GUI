"""
Скрипт для проверки данных в базе данных.
"""

from postgres_driver import PostgresDriver
from models import User, Table, Booking


def check_data():
    """Проверка данных в базе данных."""
    try:
        db = PostgresDriver()
        
        # Получаем пользователей
        users = db.read(User, table_name="user")
        print(f"\n{'='*60}")
        print(f"Пользователи ({len(users)}):")
        print('='*60)
        for user in users:
            print(f"  - {user.name} | {user.phone} | {user.email}")
        
        # Получаем столы
        tables = db.read(Table, table_name="restaurant_table")
        print(f"\n{'='*60}")
        print(f"Столы ({len(tables)}):")
        print('='*60)
        for table in tables:
            status = "✓ Доступен" if table.is_available else "✗ Недоступен"
            print(f"  - Стол №{table.number} | Вместимость: {table.capacity} | "
                  f"Локация: {table.location} | {status}")
        
        # Получаем бронирования
        bookings = db.read(Booking, table_name="booking", order_by="booking_date")
        print(f"\n{'='*60}")
        print(f"Бронирования ({len(bookings)}):")
        print('='*60)
        
        for booking in bookings:
            # Получаем пользователя и стол
            user = db.read_by_id(User, booking.user_id, table_name="user")
            table = db.read_by_id(Table, booking.table_id, table_name="restaurant_table")
            
            booking_date_str = booking.booking_date.strftime("%d.%m.%Y %H:%M")
            print(f"  - {user.name if user else 'N/A'} → Стол №{table.number if table else 'N/A'}")
            print(f"    Дата: {booking_date_str} | Гостей: {booking.guest_count} | "
                  f"Длительность: {booking.duration_minutes} мин | Статус: {booking.status}")
            if booking.special_requests:
                print(f"    Пожелания: {booking.special_requests}")
        
        db.close()
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_data()

