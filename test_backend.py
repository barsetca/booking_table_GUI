"""
Тестовый скрипт для проверки работы backend.py
"""

from datetime import datetime, timedelta
from backend import Backend


def test_backend():
    """Тестирование методов backend."""
    backend = Backend()
    
    try:
        print("="*60)
        print("ТЕСТИРОВАНИЕ BACKEND API")
        print("="*60)
        
        # Тест User CRUD
        print("\n1. ТЕСТ USER CRUD")
        print("-" * 60)
        
        # Create
        user = backend.create_user(
            name="Тестовый Пользователь",
            phone="+79999999999",
            email="test@example.com"
        )
        print(f"✓ Создан пользователь: {user.name} (ID: {user.id})")
        
        # Read by ID
        found_user = backend.get_user_by_id(user.id)
        print(f"✓ Найден пользователь по ID: {found_user.name if found_user else 'НЕ НАЙДЕН'}")
        
        # Read by email
        found_user_email = backend.get_user_by_email("test@example.com")
        print(f"✓ Найден пользователь по email: {found_user_email.name if found_user_email else 'НЕ НАЙДЕН'}")
        
        # Get all
        all_users = backend.get_all_users()
        print(f"✓ Всего пользователей: {len(all_users)}")
        
        # Update
        user.name = "Обновленный Пользователь"
        updated_user = backend.update_user(user, update_fields=["name"])
        print(f"✓ Обновлен пользователь: {updated_user.name}")
        
        # Тест Table CRUD
        print("\n2. ТЕСТ TABLE CRUD")
        print("-" * 60)
        
        # Create
        table = backend.create_table(
            number=10,
            capacity=4,
            location="window",
            is_available=True
        )
        print(f"✓ Создан стол №{table.number} (ID: {table.id})")
        
        # Read by ID
        found_table = backend.get_table_by_id(table.id)
        print(f"✓ Найден стол по ID: №{found_table.number if found_table else 'НЕ НАЙДЕН'}")
        
        # Get available tables
        available_tables = backend.get_available_tables(capacity=4)
        print(f"✓ Доступных столов (вместимость >= 4): {len(available_tables)}")
        
        # Get all
        all_tables = backend.get_all_tables()
        print(f"✓ Всего столов: {len(all_tables)}")
        
        # Update
        table.is_available = False
        updated_table = backend.update_table(table, update_fields=["is_available"])
        print(f"✓ Обновлен стол: доступен = {updated_table.is_available}")
        
        # Тест Booking CRUD
        print("\n3. ТЕСТ BOOKING CRUD")
        print("-" * 60)
        
        # Получаем первого пользователя и стол для бронирования
        users = backend.get_all_users()
        tables = backend.get_available_tables()
        
        if users and tables:
            # Create
            booking = backend.create_booking(
                user_id=users[0].id,
                table_id=tables[0].id,
                booking_date=datetime.now() + timedelta(days=5),
                guest_count=2,
                duration_minutes=120,
                status="pending",
                special_requests="Тестовое бронирование"
            )
            print(f"✓ Создано бронирование (ID: {booking.id})")
            
            # Read by ID
            found_booking = backend.get_booking_by_id(booking.id)
            print(f"✓ Найдено бронирование по ID: {'ДА' if found_booking else 'НЕТ'}")
            
            # Get bookings by user
            user_bookings = backend.get_bookings_by_user(users[0].id)
            print(f"✓ Бронирований пользователя: {len(user_bookings)}")
            
            # Get bookings by table
            table_bookings = backend.get_bookings_by_table(tables[0].id)
            print(f"✓ Бронирований стола: {len(table_bookings)}")
            
            # Update
            booking.status = "confirmed"
            updated_booking = backend.update_booking(booking, update_fields=["status"])
            print(f"✓ Обновлено бронирование: статус = {updated_booking.status}")
            
            # Confirm booking
            booking.status = "pending"
            backend.update_booking(booking, update_fields=["status"])
            confirmed_booking = backend.confirm_booking(booking.id)
            print(f"✓ Подтверждено бронирование: {confirmed_booking.status if confirmed_booking else 'ОШИБКА'}")
            
            # Get all
            all_bookings = backend.get_all_bookings(order_by="booking_date")
            print(f"✓ Всего бронирований: {len(all_bookings)}")
            
            # Cleanup - удаляем тестовые данные
            print("\n4. ОЧИСТКА ТЕСТОВЫХ ДАННЫХ")
            print("-" * 60)
            backend.delete_booking(booking.id)
            print(f"✓ Удалено тестовое бронирование")
        
        backend.delete_table(table.id)
        print(f"✓ Удален тестовый стол")
        
        backend.delete_user(user.id)
        print(f"✓ Удален тестовый пользователь")
        
        print("\n" + "="*60)
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    finally:
        backend.close()


if __name__ == "__main__":
    test_backend()

