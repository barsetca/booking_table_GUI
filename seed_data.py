"""
Скрипт для заполнения базы данных тестовыми данными.
Создает 4 пользователя, 5 столов и 3 бронирования.
"""

from datetime import datetime, timedelta
from postgres_driver import PostgresDriver
from models import User, Table, Booking


def seed_database(clear_existing: bool = False):
    """
    Заполнение базы данных тестовыми данными.
    
    Args:
        clear_existing: Очистить существующие данные перед заполнением
    """
    print("Заполнение базы данных тестовыми данными...")
    
    try:
        db = PostgresDriver()
        print("✓ Подключение к базе данных установлено")
        
        # Очистка существующих данных, если нужно
        if clear_existing:
            print("\nОчистка существующих данных...")
            db.execute_query('DELETE FROM "booking";', fetch=False)
            db.execute_query('DELETE FROM "restaurant_table";', fetch=False)
            db.execute_query('DELETE FROM "user";', fetch=False)
            print("✓ Данные очищены")
        
        # Создание пользователей
        print("\n" + "="*50)
        print("Создание пользователей...")
        print("="*50)
        
        users_data = [
            {"name": "Иван Петров", "phone": "+79001234567", "email": "ivan.petrov@example.com"},
            {"name": "Мария Сидорова", "phone": "+79007654321", "email": "maria.sidorova@example.com"},
            {"name": "Алексей Иванов", "phone": "+79005555555", "email": "alexey.ivanov@example.com"},
            {"name": "Елена Козлова", "phone": "+79008888888", "email": "elena.kozlova@example.com"},
        ]
        
        users = []
        for user_data in users_data:
            user = User(**user_data)
            user = db.create(user, table_name="user")
            users.append(user)
            print(f"✓ Создан пользователь: {user.name} (ID: {user.id})")
        
        # Создание столов
        print("\n" + "="*50)
        print("Создание столов...")
        print("="*50)
        
        tables_data = [
            {"number": 1, "capacity": 2, "location": "window", "is_available": True},
            {"number": 2, "capacity": 4, "location": "window", "is_available": True},
            {"number": 3, "capacity": 6, "location": "center", "is_available": False},
            {"number": 4, "capacity": 2, "location": "corner", "is_available": True},
            {"number": 5, "capacity": 8, "location": "center", "is_available": True},
        ]
        
        tables = []
        for table_data in tables_data:
            table = Table(**table_data)
            table = db.create(table, table_name="restaurant_table")
            tables.append(table)
            status = "доступен" if table.is_available else "недоступен"
            print(f"✓ Создан стол №{table.number} (вместимость: {table.capacity}, локация: {table.location}, {status})")
        
        # Создание бронирований
        print("\n" + "="*50)
        print("Создание бронирований...")
        print("="*50)
        
        # Получаем текущую дату и время
        now = datetime.now()
        
        bookings_data = [
            {
                "user_id": users[0].id,
                "table_id": tables[0].id,
                "booking_date": now + timedelta(days=1, hours=19),  # Завтра в 19:00
                "guest_count": 2,
                "duration_minutes": 120,
                "status": "confirmed",
                "special_requests": "Стол у окна, пожалуйста"
            },
            {
                "user_id": users[1].id,
                "table_id": tables[1].id,
                "booking_date": now + timedelta(days=2, hours=20),  # Послезавтра в 20:00
                "guest_count": 4,
                "duration_minutes": 90,
                "status": "pending",
                "special_requests": ""
            },
            {
                "user_id": users[2].id,
                "table_id": tables[4].id,
                "booking_date": now + timedelta(days=3, hours=18, minutes=30),  # Через 3 дня в 18:30
                "guest_count": 6,
                "duration_minutes": 150,
                "status": "confirmed",
                "special_requests": "День рождения, нужен торт"
            },
        ]
        
        bookings = []
        for booking_data in bookings_data:
            booking = Booking(**booking_data)
            booking = db.create(booking, table_name="booking")
            bookings.append(booking)
            
            # Находим пользователя и стол для вывода
            user = next(u for u in users if u.id == booking.user_id)
            table = next(t for t in tables if t.id == booking.table_id)
            
            booking_date_str = booking.booking_date.strftime("%d.%m.%Y %H:%M")
            print(f"✓ Создано бронирование: {user.name} → Стол №{table.number} на {booking_date_str} "
                  f"({booking.guest_count} гостей, статус: {booking.status})")
        
        # Закрываем соединения
        db.close()
        
        print("\n" + "="*50)
        print("✓ База данных успешно заполнена тестовыми данными!")
        print("="*50)
        print(f"\nИтого создано:")
        print(f"  - Пользователей: {len(users)}")
        print(f"  - Столов: {len(tables)}")
        print(f"  - Бронирований: {len(bookings)}")
        
        return True
        
    except ConnectionError as e:
        print(f"\n✗ Ошибка подключения к базе данных: {e}")
        print("Проверьте настройки в файле .env")
        return False
    except Exception as e:
        print(f"\n✗ Ошибка при заполнении базы данных: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    
    # Проверяем аргументы командной строки
    clear_existing = "--clear" in sys.argv or "-c" in sys.argv
    
    if clear_existing:
        print("⚠ ВНИМАНИЕ: Все существующие данные будут удалены!")
        response = input("Продолжить? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Отменено.")
            sys.exit(0)
    
    success = seed_database(clear_existing=clear_existing)
    sys.exit(0 if success else 1)

