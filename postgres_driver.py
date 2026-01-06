"""
Универсальный менеджер для работы с PostgreSQL.
Поддерживает создание таблиц из dataclass, выполнение запросов и CRUD операции.
"""

import os
from dataclasses import fields, is_dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, get_args, get_origin
from uuid import UUID

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor, register_uuid
from psycopg2.pool import SimpleConnectionPool

# Загружаем переменные окружения
load_dotenv()

T = TypeVar('T')


class PostgresDriver:
    """Универсальный менеджер для работы с PostgreSQL."""
    
    def __init__(self, minconn: int = 1, maxconn: int = 10):
        """
        Инициализация драйвера с настройками из .env файла.
        
        Args:
            minconn: Минимальное количество соединений в пуле
            maxconn: Максимальное количество соединений в пуле
        """
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        
        # Создаем пул соединений
        try:
            self.pool = SimpleConnectionPool(
                minconn=minconn,
                maxconn=maxconn,
                **self.db_config
            )
            # Регистрируем поддержку UUID
            register_uuid()
        except Exception as e:
            raise ConnectionError(f"Не удалось подключиться к базе данных: {e}")
    
    def _get_connection(self):
        """Получить соединение из пула."""
        if self.pool:
            return self.pool.getconn()
        raise ConnectionError("Пул соединений не инициализирован")
    
    def _return_connection(self, conn):
        """Вернуть соединение в пул."""
        if self.pool:
            self.pool.putconn(conn)
    
    def _python_type_to_postgres(self, field_type: Type) -> str:
        """
        Преобразование типа Python в тип PostgreSQL.
        
        Args:
            field_type: Тип поля из dataclass
            
        Returns:
            Строка с типом PostgreSQL
        """
        # Обработка Optional и Union
        origin = get_origin(field_type)
        if origin is not None:
            # Для Optional[Type] или Union[Type, None]
            args = get_args(field_type)
            if len(args) > 0 and type(None) not in args:
                field_type = args[0]
            elif len(args) > 0:
                # Optional[Type] -> берем первый не-None тип
                field_type = next((arg for arg in args if arg is not type(None)), args[0])
        
        # Базовые типы
        if field_type == UUID:
            return "UUID"
        elif field_type == str:
            return "VARCHAR(255)"
        elif field_type == int:
            return "INTEGER"
        elif field_type == bool:
            return "BOOLEAN"
        elif field_type == datetime:
            return "TIMESTAMP"
        elif field_type == float:
            return "REAL"
        else:
            # Для Literal и других типов используем VARCHAR
            return "VARCHAR(255)"
    
    def create_table_from_entity(self, entity_class: Type, table_name: Optional[str] = None, 
                                 drop_if_exists: bool = False) -> bool:
        """
        Создание таблицы из dataclass сущности.
        
        Args:
            entity_class: Класс dataclass для создания таблицы
            table_name: Имя таблицы (по умолчанию имя класса в нижнем регистре)
            drop_if_exists: Удалить таблицу, если она существует
            
        Returns:
            True если таблица создана успешно
        """
        if not is_dataclass(entity_class):
            raise ValueError(f"Класс {entity_class.__name__} не является dataclass")
        
        if table_name is None:
            table_name = entity_class.__name__.lower()
        
        conn = None
        cursor = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Удаляем таблицу, если нужно
            if drop_if_exists:
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
            
            # Получаем поля dataclass
            entity_fields = fields(entity_class)
            
            # Формируем SQL для создания таблицы
            columns = []
            primary_key = None
            
            for field in entity_fields:
                field_name = field.name
                field_type = field.type
                
                # Определяем тип PostgreSQL
                pg_type = self._python_type_to_postgres(field_type)
                
                # Проверяем, является ли поле первичным ключом (обычно это 'id')
                is_primary_key = field_name == 'id'
                
                # Проверяем, есть ли значение по умолчанию
                has_default = field.default is not None or field.default_factory is not None
                
                # Формируем определение колонки
                column_def = f"{field_name} {pg_type}"
                
                if is_primary_key:
                    column_def += " PRIMARY KEY"
                    primary_key = field_name
                elif not has_default:
                    column_def += " NOT NULL"
                
                columns.append(column_def)
            
            # Создаем SQL запрос (используем кавычки для имени таблицы)
            create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    {', '.join(columns)}
                );
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Ошибка при создании таблицы {table_name}: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._return_connection(conn)
    
    def execute_query(self, query: str, params: Optional[tuple] = None, 
                     fetch: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Выполнение произвольного SQL запроса.
        
        Args:
            query: SQL запрос
            params: Параметры для запроса (кортеж)
            fetch: Нужно ли получать результаты (для SELECT)
            
        Returns:
            Список словарей с результатами или None
        """
        conn = None
        cursor = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return None
                
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Ошибка при выполнении запроса: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._return_connection(conn)
    
    def create(self, entity: Any, table_name: Optional[str] = None) -> Any:
        """
        Создание записи в таблице (INSERT).
        
        Args:
            entity: Экземпляр dataclass для вставки
            table_name: Имя таблицы (по умолчанию имя класса в нижнем регистре)
            
        Returns:
            Созданная сущность с обновленным id
        """
        if not is_dataclass(entity):
            raise ValueError("Сущность должна быть dataclass")
        
        if table_name is None:
            table_name = entity.__class__.__name__.lower()
        
        conn = None
        cursor = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Получаем поля и значения
            entity_fields = fields(entity)
            field_names = [f.name for f in entity_fields]
            values = [getattr(entity, name) for name in field_names]
            
            # Формируем SQL запрос
            placeholders = ', '.join(['%s'] * len(field_names))
            columns = ', '.join(field_names)
            
            insert_sql = f"""
                INSERT INTO "{table_name}" ({columns})
                VALUES ({placeholders})
                RETURNING *;
            """
            
            cursor.execute(insert_sql, values)
            result = cursor.fetchone()
            conn.commit()
            
            # Обновляем entity с данными из БД
            result_dict = dict(result)
            for field in entity_fields:
                value = result_dict.get(field.name)
                # Преобразуем строку UUID в UUID объект, если нужно
                if field.type == UUID and isinstance(value, str):
                    value = UUID(value)
                setattr(entity, field.name, value)
            
            return entity
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Ошибка при создании записи: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._return_connection(conn)
    
    def read(self, entity_class: Type[T], table_name: Optional[str] = None,
             filters: Optional[Dict[str, Any]] = None, 
             limit: Optional[int] = None,
             order_by: Optional[str] = None) -> List[T]:
        """
        Чтение записей из таблицы (SELECT).
        
        Args:
            entity_class: Класс dataclass для создания объектов
            table_name: Имя таблицы (по умолчанию имя класса в нижнем регистре)
            filters: Словарь с условиями фильтрации {поле: значение}
            limit: Ограничение количества записей
            order_by: Поле для сортировки
            
        Returns:
            Список экземпляров entity_class
        """
        if not is_dataclass(entity_class):
            raise ValueError(f"Класс {entity_class.__name__} не является dataclass")
        
        if table_name is None:
            table_name = entity_class.__name__.lower()
        
        conn = None
        cursor = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Формируем SQL запрос
            select_sql = f'SELECT * FROM "{table_name}"'
            params = []
            
            # Добавляем условия WHERE
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(f"{key} = %s")
                    params.append(value)
                select_sql += " WHERE " + " AND ".join(conditions)
            
            # Добавляем сортировку
            if order_by:
                select_sql += f" ORDER BY {order_by}"
            
            # Добавляем лимит
            if limit:
                select_sql += f" LIMIT {limit}"
            
            cursor.execute(select_sql, tuple(params) if params else None)
            results = cursor.fetchall()
            
            # Преобразуем результаты в объекты
            entities = []
            entity_fields = {f.name: f for f in fields(entity_class)}
            
            for row in results:
                row_dict = dict(row)
                # Создаем экземпляр класса
                kwargs = {}
                for field_name, field in entity_fields.items():
                    value = row_dict.get(field_name)
                    # Преобразуем типы, если нужно
                    if value is not None:
                        # UUID
                        if field.type == UUID and isinstance(value, str):
                            value = UUID(value)
                        # datetime уже должен быть datetime объектом из psycopg2
                    kwargs[field_name] = value
                
                entity = entity_class(**kwargs)
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            raise Exception(f"Ошибка при чтении записей: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._return_connection(conn)
    
    def read_by_id(self, entity_class: Type[T], entity_id: Any, 
                   table_name: Optional[str] = None) -> Optional[T]:
        """
        Чтение записи по ID.
        
        Args:
            entity_class: Класс dataclass
            entity_id: ID записи
            table_name: Имя таблицы
            
        Returns:
            Экземпляр entity_class или None
        """
        results = self.read(entity_class, table_name, filters={'id': entity_id}, limit=1)
        return results[0] if results else None
    
    def update(self, entity: Any, table_name: Optional[str] = None,
               update_fields: Optional[List[str]] = None) -> Any:
        """
        Обновление записи в таблице (UPDATE).
        
        Args:
            entity: Экземпляр dataclass для обновления
            table_name: Имя таблицы
            update_fields: Список полей для обновления (если None, обновляются все поля кроме id)
            
        Returns:
            Обновленная сущность
        """
        if not is_dataclass(entity):
            raise ValueError("Сущность должна быть dataclass")
        
        if table_name is None:
            table_name = entity.__class__.__name__.lower()
        
        # Получаем id
        entity_id = getattr(entity, 'id', None)
        if entity_id is None:
            raise ValueError("Сущность должна иметь поле 'id' для обновления")
        
        conn = None
        cursor = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Получаем поля для обновления
            entity_fields = fields(entity)
            
            if update_fields is None:
                # Обновляем все поля кроме id и created_at (обычно не обновляется)
                update_fields = [f.name for f in entity_fields 
                               if f.name not in ('id', 'created_at')]
            
            # Формируем SQL запрос
            set_clauses = []
            values = []
            
            for field_name in update_fields:
                set_clauses.append(f"{field_name} = %s")
                values.append(getattr(entity, field_name))
            
            values.append(entity_id)  # Для WHERE условия
            
            update_sql = f"""
                UPDATE "{table_name}"
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING *;
            """
            
            cursor.execute(update_sql, values)
            result = cursor.fetchone()
            conn.commit()
            
            # Обновляем entity
            result_dict = dict(result)
            for field in entity_fields:
                value = result_dict.get(field.name)
                # Преобразуем строку UUID в UUID объект, если нужно
                if field.type == UUID and isinstance(value, str):
                    value = UUID(value)
                setattr(entity, field.name, value)
            
            return entity
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Ошибка при обновлении записи: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._return_connection(conn)
    
    def delete(self, entity_id: Any, table_name: str) -> bool:
        """
        Удаление записи из таблицы (DELETE).
        
        Args:
            entity_id: ID записи для удаления
            table_name: Имя таблицы
            
        Returns:
            True если запись удалена успешно
        """
        conn = None
        cursor = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            delete_sql = f'DELETE FROM "{table_name}" WHERE id = %s;'
            cursor.execute(delete_sql, (entity_id,))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Ошибка при удалении записи: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._return_connection(conn)
    
    def close(self):
        """Закрыть пул соединений."""
        if self.pool:
            self.pool.closeall()

