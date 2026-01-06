"""
Скрипт для проверки структуры созданных таблиц.
"""

from postgres_driver import PostgresDriver


def check_tables():
    """Проверка структуры таблиц в базе данных."""
    try:
        db = PostgresDriver()
        
        tables = ['user', 'restaurant_table', 'booking']
        
        for table_name in tables:
            print(f"\n{'='*60}")
            print(f"Структура таблицы: {table_name}")
            print('='*60)
            
            # Получаем структуру таблицы
            query = f"""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """
            
            result = db.execute_query(query)
            
            if result:
                print(f"{'Колонка':<20} {'Тип':<20} {'NULL':<10} {'По умолчанию':<20}")
                print("-" * 70)
                for row in result:
                    col_name = row.get('column_name', '')
                    data_type = row.get('data_type', '')
                    is_nullable = row.get('is_nullable', '')
                    default = row.get('column_default', '') or ''
                    print(f"{col_name:<20} {data_type:<20} {is_nullable:<10} {default[:20]:<20}")
            else:
                print("Таблица не найдена или пуста")
        
        db.close()
        
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    check_tables()

