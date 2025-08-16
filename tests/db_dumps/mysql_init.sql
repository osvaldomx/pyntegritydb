-- DUMP PARA MYSQL

-- Crear el esquema
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
    `id` INTEGER PRIMARY KEY,
    `name` TEXT NOT NULL
);

CREATE TABLE `orders` (
    `order_id` INTEGER PRIMARY KEY,
    `user_id` INTEGER,
    `product` TEXT,
    `customer_name` TEXT,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
);

-- Desactivar temporalmente las restricciones
SET FOREIGN_KEY_CHECKS=0;

-- Insertar datos
INSERT INTO `users` (`id`, `name`) VALUES (1, 'Alice'), (2, 'Bob');
INSERT INTO `orders` (`order_id`, `user_id`, `product`, `customer_name`) VALUES 
(101, 1, 'Laptop', 'Alice'),
(102, 2, 'Mouse', 'Bob'),
(103, 1, 'Keyboard', 'Alicia'), -- Fila inconsistente
(104, 99, 'Monitor', 'Charlie'); -- Fila huérfana

-- Reactivar las restricciones
SET FOREIGN_KEY_CHECKS=1;