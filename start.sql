# как настроить контейнер postgres
CREATE ROLE username WITH LOGIN PASSWORD 'secret';
CREATE DATABASE delivery OWNER username;
GRANT ALL PRIVILEGES ON DATABASE delivery TO username;

# как в него попасть 
docker exec -it delivery-postgres-1 psql -U postgres -d delivery

# запросы в базу
-- Выборки
SELECT * FROM public.couriers;
SELECT * FROM public.storage_places;
SELECT * FROM public.orders;
SELECT * FROM public.outbox;

-- Очистка БД (все кроме справочников)
DELETE FROM public.couriers;
DELETE FROM public.storage_places;
DELETE FROM public.orders;
DELETE FROM public.outbox;

-- Добавить курьеров

-- Пеший
INSERT INTO public.couriers(
    id, name, speed, location_x, location_y, created_at, updated_at)
VALUES ('bf79a004-56d7-4e5f-a21c-0a9e5e08d10d', 'Пеший', 1, 1, 1, now(), now());

INSERT INTO storage_places (id, name, order_id, total_volume, courier_id)
VALUES
    ('ed58fa74-b8fb-4a8c-a84b-e5c29ca9b0c6', 'Сумка', NULL, 10, 'bf79a004-56d7-4e5f-a21c-0a9e5e08d10d');

-- Вело
INSERT INTO public.couriers(
    id, name, speed, location_x, location_y, created_at, updated_at)
VALUES ('db18375d-59a7-49d1-bd96-a1738adcee93', 'Вело', 2, 2, 2, now(), now());

INSERT INTO storage_places (id, name, order_id, total_volume, courier_id, created_at, updated_at)
VALUES
    ('b96a9d83-aefa-4d06-99fb-e630d17c3868', 'Вело-Сумка', NULL, 10, 'db18375d-59a7-49d1-bd96-a1738adcee93', now(), now()),
    ('838ac7aa-3f39-4b8a-b2be-f75fc3e35d34', 'Вело-Багажник', NULL, 30, 'db18375d-59a7-49d1-bd96-a1738adcee93', now(), now());

-- Авто
INSERT INTO public.couriers(
    id, name, speed, location_x, location_y, created_at, updated_at)
VALUES ('0f860f2c-d76a-4140-99b3-fcc63f27a826', 'Авто', 3, 3, 3, now(), now());

INSERT INTO storage_places (id, name, order_id, total_volume, courier_id, created_at, updated_at)
VALUES
    ('f15b0f8c-dd93-4be6-a95a-3afd3a9f199e', 'Авто-Сумка', NULL, 10, '0f860f2c-d76a-4140-99b3-fcc63f27a826', now(), now()),
    ('84e1ccae-555d-439c-8c87-dae080c82d29', 'Авто-Багажник', NULL, 50, '0f860f2c-d76a-4140-99b3-fcc63f27a826', now(), now()),
    ('11fc6c0a-fc58-4718-b32d-8ce82e002201', 'Авто-Прицеп', NULL, 100, '0f860f2c-d76a-4140-99b3-fcc63f27a826', now(), now());
