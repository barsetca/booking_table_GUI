"""
Скрипт для инициализации таблиц в базе данных PostgreSQL.
Создает таблицы для всех сущностей системы бронирования столов.
"""

from postgres_driver import PostgresDriver
from models import User, Table, Booking


def init_database(drop_if_exists: bool = False):
    """
    Создание таблиц в базе данных.
    
    Args:
        drop_if_exists: Удалить существующие таблицы перед созданием
    """
    print("Инициализация базы данных...")
    
    try:
        # Инициализация драйвера
        db = PostgresDriver()
        print("✓ Подключение к базе данных установлено")
        
        # Создание таблицы User
        print("\nСоздание таблицы 'user'...")
        db.create_table_from_entity(User, table_name="user", drop_if_exists=drop_if_exists)
        print("✓ Таблица 'user' создана успешно")
        
        # Создание таблицы Table (используем имя "restaurant_table", т.к. "table" - зарезервированное слово)
        print("\nСоздание таблицы 'restaurant_table'...")
        db.create_table_from_entity(Table, table_name="restaurant_table", drop_if_exists=drop_if_exists)
        print("✓ Таблица 'restaurant_table' создана успешно")
        
        # Создание таблицы Booking
        print("\nСоздание таблицы 'booking'...")
        db.create_table_from_entity(Booking, table_name="booking", drop_if_exists=drop_if_exists)
        print("✓ Таблица 'booking' создана успешно")
        
        # Закрываем соединения
        db.close()
        
        print("\n" + "="*50)
        print("✓ Все таблицы успешно созданы!")
        print("="*50)
        
    except ConnectionError as e:
        print(f"\n✗ Ошибка подключения к базе данных: {e}")
        print("Проверьте настройки в файле .env")
        return False
    except Exception as e:
        print(f"\n✗ Ошибка при создании таблиц: {e}")
        return False
    
    return True


if __name__ == "__main__":
    import sys
    
    # Проверяем аргументы командной строки
    drop_if_exists = "--drop" in sys.argv or "-d" in sys.argv
    
    if drop_if_exists:
        print("⚠ ВНИМАНИЕ: Все существующие таблицы будут удалены!")
        response = input("Продолжить? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Отменено.")
            sys.exit(0)
    
    success = init_database(drop_if_exists=drop_if_exists)
    sys.exit(0 if success else 1)

