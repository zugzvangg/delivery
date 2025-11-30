# src/delivery/infrastructure/persistence/sqlite/database.py
import json
import sqlite3
from typing import Any, Dict, Optional

from loguru import logger


class Database:
    """Менеджер подключения к SQLite базе"""
    
    def __init__(self, db_path: str = "delivery.db"):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Инициализация базы данных и создание двух таблиц"""
        conn = self._get_connection()
        try:
            # Таблица заказов
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    location TEXT NOT NULL, -- JSON Location
                    volume INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    courier_id TEXT
                )
            """)
            
            # Таблица курьеров (включая места хранения как JSON)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS couriers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    speed INTEGER NOT NULL,
                    location TEXT NOT NULL,
                    storage_places TEXT NOT NULL -- JSON массив StoragePlace
                )
            """)
                        
            conn.commit()
            logger.info(f"База данных инициализирована: {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации базы: {e}")
            raise
    
    def _get_connection(self) -> sqlite3.Connection:
        """Получить подключение к базе"""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30.0  # Таймаут для избежания блокировок
            )
            
            # Включение возврата результатов в виде dict
            self._connection.row_factory = sqlite3.Row
            
        return self._connection
    
    def get_cursor(self) -> sqlite3.Cursor:
        """Получить курсор для выполнения запросов"""
        return self._get_connection().cursor()
    
    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Выполнить SQL запрос и вернуть курсор"""
        cursor = self.get_cursor()
        cursor.execute(query, params)
        return cursor
    
    def execute_many(self, query: str, params_list: list):
        """Выполнить массовую вставку/обновление"""
        cursor = self.get_cursor()
        cursor.executemany(query, params_list)
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Выполнить запрос и вернуть одну строку как словарь"""
        cursor = self.execute_query(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = ()) -> list[Dict[str, Any]]:
        """Выполнить запрос и вернуть все строки как список словарей"""
        cursor = self.execute_query(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def commit(self):
        """Подтвердить транзакцию"""
        if self._connection:
            try:
                self._connection.commit()
            except sqlite3.Error as e:
                logger.error(f"Ошибка коммита: {e}")
                raise
    
    def rollback(self):
        """Откатить транзакцию"""
        if self._connection:
            try:
                self._connection.rollback()
            except sqlite3.Error as e:
                logger.error(f"Ошибка отката: {e}")
                raise
    
    def close(self):
        """Закрыть подключение"""
        if self._connection:
            try:
                self._connection.close()
                self._connection = None
                logger.info("Подключение к базе закрыто")
            except sqlite3.Error as e:
                logger.error(f"Ошибка закрытия подключения: {e}")
    
    def get_table_info(self) -> Dict[str, int]:
        """Получить информацию о количестве записей в таблицах (для отладки)"""
        try:
            orders_count = self.fetch_one("SELECT COUNT(*) as count FROM orders")['count']
            couriers_count = self.fetch_one("SELECT COUNT(*) as count FROM couriers")['count']
            
            return {
                'orders': orders_count,
                'couriers': couriers_count
            }
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения информации о таблицах: {e}")
            return {'orders': 0, 'couriers': 0}
    
    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие при выходе из контекста"""
        if exc_type is not None:
            self.rollback()
        self.close()


