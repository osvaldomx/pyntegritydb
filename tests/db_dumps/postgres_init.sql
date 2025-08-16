-- Conéctate a la base de datos correcta primero
\c testdb;

-- Ahora, ejecuta los comandos de esquema y datos
DROP TABLE IF EXISTS "orders";
DROP TABLE IF EXISTS "users";

CREATE TABLE "users" (
    "id" INTEGER PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL
);

CREATE TABLE "orders" (
    "order_id" INTEGER PRIMARY KEY,
    "user_id" INTEGER,
    "product" VARCHAR(255),
    "customer_name" VARCHAR(255),
    FOREIGN KEY ("user_id") REFERENCES "users" ("id")
);

ALTER TABLE "orders" DISABLE TRIGGER ALL;

INSERT INTO "users" ("id", "name") VALUES (1, 'Alice'), (2, 'Bob');
INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES 
(101, 1, 'Laptop', 'Alice'),
(102, 2, 'Mouse', 'Bob'),
(103, 1, 'Keyboard', 'Alicia'),
(104, 99, 'Monitor', 'Charlie');

ALTER TABLE "orders" ENABLE TRIGGER ALL;