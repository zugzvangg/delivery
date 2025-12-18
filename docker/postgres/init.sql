-- настройка postgres при старте
-- Создать роль, если не существует
DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_roles WHERE rolname = 'username'
   ) THEN
      CREATE ROLE username WITH LOGIN PASSWORD 'secret';
   END IF;
END
$$;

-- Создать БД, если не существует (psql-магия)
SELECT 'CREATE DATABASE delivery OWNER username'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'delivery'
)\gexec

-- Права (на всякий)
GRANT ALL PRIVILEGES ON DATABASE delivery TO username;
