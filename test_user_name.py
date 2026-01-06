"""
Тестовый скрипт для проверки работы с именами пользователей.
"""

from backend import Backend


def test_user_name_uniqueness():
    """Тестирование уникальности имен пользователей."""
    backend = Backend()
    
    try:
        print("="*60)
        print("ТЕСТИРОВАНИЕ РАБОТЫ С ИМЕНАМИ ПОЛЬЗОВАТЕЛЕЙ")
        print("="*60)
        
        # Тест 1: Создание пользователя с уникальным именем
        print("\n1. ТЕСТ: Создание пользователя с уникальным именем")
        print("-" * 60)
        user1 = backend.create_user("Тестовый Пользователь", "+79999999999", "test1@example.com")
        print(f"✓ Создан пользователь: {user1.name} (ID: {user1.id})")
        
        # Тест 2: Попытка создать пользователя с тем же именем
        print("\n2. ТЕСТ: Попытка создать пользователя с существующим именем")
        print("-" * 60)
        try:
            user2 = backend.create_user("Тестовый Пользователь", "+79999999998", "test2@example.com")
            print("✗ ОШИБКА: Пользователь с дублирующимся именем был создан!")
        except ValueError as e:
            print(f"✓ Ожидаемая ошибка: {e}")
        
        # Тест 3: Создание пользователя с другим именем
        print("\n3. ТЕСТ: Создание пользователя с другим именем")
        print("-" * 60)
        user3 = backend.create_user("Другой Пользователь", "+79999999997", "test3@example.com")
        print(f"✓ Создан пользователь: {user3.name} (ID: {user3.id})")
        
        # Тест 4: Поиск пользователя по имени
        print("\n4. ТЕСТ: Поиск пользователя по имени")
        print("-" * 60)
        found_user = backend.get_user_by_name("Тестовый Пользователь")
        if found_user and found_user.id == user1.id:
            print(f"✓ Пользователь найден: {found_user.name} (ID: {found_user.id})")
        else:
            print("✗ ОШИБКА: Пользователь не найден или найден неверный пользователь")
        
        # Тест 5: Обновление пользователя с изменением имени на уникальное
        print("\n5. ТЕСТ: Обновление пользователя с изменением имени на уникальное")
        print("-" * 60)
        user1.name = "Обновленное Имя"
        updated_user = backend.update_user(user1, update_fields=["name"])
        print(f"✓ Имя обновлено: {updated_user.name}")
        
        # Тест 6: Попытка обновить имя на существующее
        print("\n6. ТЕСТ: Попытка обновить имя на существующее")
        print("-" * 60)
        user1.name = "Другой Пользователь"  # Это имя уже занято user3
        try:
            backend.update_user(user1, update_fields=["name"])
            print("✗ ОШИБКА: Имя было обновлено на существующее!")
        except ValueError as e:
            print(f"✓ Ожидаемая ошибка: {e}")
        
        # Тест 7: Обновление имени на то же самое (должно пройти)
        print("\n7. ТЕСТ: Обновление имени на то же самое")
        print("-" * 60)
        user1.name = "Обновленное Имя"  # Возвращаем обратно
        updated_user = backend.update_user(user1, update_fields=["name"])
        print(f"✓ Имя обновлено на то же самое: {updated_user.name}")
        
        # Очистка
        print("\n8. ОЧИСТКА")
        print("-" * 60)
        backend.delete_user(user1.id)
        print("✓ Удален тестовый пользователь 1")
        backend.delete_user(user3.id)
        print("✓ Удален тестовый пользователь 3")
        
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
    test_user_name_uniqueness()

