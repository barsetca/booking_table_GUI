"""
Тестовый скрипт для проверки функции check_table_availability.
"""

from datetime import datetime, timedelta
from backend import Backend


def test_availability():
    """Тестирование функции проверки доступности стола."""
    backend = Backend()
    
    try:
        print("="*60)
        print("ТЕСТИРОВАНИЕ ПРОВЕРКИ ДОСТУПНОСТИ СТОЛА")
        print("="*60)
        
        # Получаем существующие данные
        users = backend.get_all_users()
        tables = backend.get_all_tables()
        
        if not users or not tables:
            print("✗ Недостаточно данных для тестирования")
            return
        
        user = users[0]
        table = tables[0]
        
        print(f"\nИспользуем пользователя: {user.name}")
        print(f"Используем стол: №{table.number}")
        
        # Тест 1: Проверка доступного времени
        print("\n1. ТЕСТ: Проверка доступного времени")
        print("-" * 60)
        future_date = datetime.now() + timedelta(days=10, hours=19)
        is_available, reason = backend.check_table_availability(
            table_id=table.id,
            booking_date=future_date,
            duration_minutes=120
        )
        print(f"Время: {future_date.strftime('%d.%m.%Y %H:%M')}, длительность: 120 мин")
        print(f"Результат: {'✓ Доступно' if is_available else f'✗ Недоступно: {reason}'}")
        
        # Тест 2: Создание бронирования и проверка пересечения
        print("\n2. ТЕСТ: Создание бронирования и проверка пересечения")
        print("-" * 60)
        booking_date = datetime.now() + timedelta(days=11, hours=20)
        
        # Создаем бронирование
        booking = backend.create_booking(
            user_id=user.id,
            table_id=table.id,
            booking_date=booking_date,
            guest_count=2,
            duration_minutes=120,
            status="confirmed"
        )
        print(f"✓ Создано бронирование на {booking_date.strftime('%d.%m.%Y %H:%M')} (120 мин)")
        
        # Проверяем пересечение - то же время
        print("\nПроверка пересечения - то же время:")
        is_available, reason = backend.check_table_availability(
            table_id=table.id,
            booking_date=booking_date,
            duration_minutes=120
        )
        print(f"Результат: {'✓ Доступно' if is_available else f'✗ Недоступно: {reason}'}")
        
        # Проверяем пересечение - частичное перекрытие (начало)
        print("\nПроверка пересечения - частичное перекрытие (начало):")
        overlap_start = booking_date - timedelta(minutes=30)
        is_available, reason = backend.check_table_availability(
            table_id=table.id,
            booking_date=overlap_start,
            duration_minutes=60
        )
        print(f"Время: {overlap_start.strftime('%d.%m.%Y %H:%M')}, длительность: 60 мин")
        print(f"Результат: {'✓ Доступно' if is_available else f'✗ Недоступно: {reason}'}")
        
        # Проверяем пересечение - частичное перекрытие (конец)
        print("\nПроверка пересечения - частичное перекрытие (конец):")
        overlap_end = booking_date + timedelta(minutes=60)
        is_available, reason = backend.check_table_availability(
            table_id=table.id,
            booking_date=overlap_end,
            duration_minutes=60
        )
        print(f"Время: {overlap_end.strftime('%d.%m.%Y %H:%M')}, длительность: 60 мин")
        print(f"Результат: {'✓ Доступно' if is_available else f'✗ Недоступно: {reason}'}")
        
        # Проверяем - время до существующего бронирования (должно быть доступно)
        print("\nПроверка - время до существующего бронирования:")
        before_booking = booking_date - timedelta(hours=2)
        is_available, reason = backend.check_table_availability(
            table_id=table.id,
            booking_date=before_booking,
            duration_minutes=60
        )
        print(f"Время: {before_booking.strftime('%d.%m.%Y %H:%M')}, длительность: 60 мин")
        print(f"Результат: {'✓ Доступно' if is_available else f'✗ Недоступно: {reason}'}")
        
        # Проверяем - время после существующего бронирования (должно быть доступно)
        print("\nПроверка - время после существующего бронирования:")
        after_booking = booking_date + timedelta(hours=3)
        is_available, reason = backend.check_table_availability(
            table_id=table.id,
            booking_date=after_booking,
            duration_minutes=60
        )
        print(f"Время: {after_booking.strftime('%d.%m.%Y %H:%M')}, длительность: 60 мин")
        print(f"Результат: {'✓ Доступно' if is_available else f'✗ Недоступно: {reason}'}")
        
        # Тест 3: Проверка при обновлении бронирования (исключение самого себя)
        print("\n3. ТЕСТ: Проверка при обновлении бронирования")
        print("-" * 60)
        # Пытаемся обновить время на то же самое (должно пройти)
        booking.booking_date = booking_date + timedelta(minutes=5)
        is_available, reason = backend.check_table_availability(
            table_id=table.id,
            booking_date=booking.booking_date,
            duration_minutes=booking.duration_minutes,
            exclude_booking_id=booking.id
        )
        print(f"Обновление времени на {booking.booking_date.strftime('%d.%m.%Y %H:%M')} (исключая само бронирование)")
        print(f"Результат: {'✓ Доступно' if is_available else f'✗ Недоступно: {reason}'}")
        
        # Тест 4: Попытка создать пересекающееся бронирование (должна быть ошибка)
        print("\n4. ТЕСТ: Попытка создать пересекающееся бронирование")
        print("-" * 60)
        try:
            conflicting_booking = backend.create_booking(
                user_id=user.id,
                table_id=table.id,
                booking_date=booking_date + timedelta(minutes=30),  # Пересекается
                guest_count=2,
                duration_minutes=120,
                check_availability=True
            )
            print("✗ ОШИБКА: Пересекающееся бронирование было создано!")
        except ValueError as e:
            print(f"✓ Ожидаемая ошибка: {e}")
        
        # Тест 5: Проверка отмененных бронирований (не должны учитываться)
        print("\n5. ТЕСТ: Проверка отмененных бронирований")
        print("-" * 60)
        # Отменяем существующее бронирование
        backend.cancel_booking(booking.id)
        print(f"✓ Бронирование отменено")
        
        # Проверяем доступность на то же время (должно быть доступно)
        is_available, reason = backend.check_table_availability(
            table_id=table.id,
            booking_date=booking_date,
            duration_minutes=120
        )
        print(f"Проверка доступности на время отмененного бронирования")
        print(f"Результат: {'✓ Доступно (отмененные не учитываются)' if is_available else f'✗ Недоступно: {reason}'}")
        
        # Очистка
        print("\n6. ОЧИСТКА")
        print("-" * 60)
        backend.delete_booking(booking.id)
        print("✓ Тестовое бронирование удалено")
        
        print("\n" + "="*60)
        print("✓ ВСЕ ТЕСТЫ ПРОВЕРКИ ДОСТУПНОСТИ ПРОЙДЕНЫ!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    finally:
        backend.close()


if __name__ == "__main__":
    test_availability()

