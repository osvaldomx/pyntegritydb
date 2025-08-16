DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
    `id` INT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL
);

CREATE TABLE `orders` (
    `order_id` INT PRIMARY KEY,
    `user_id` INT,
    `product` VARCHAR(255),
    `customer_name` VARCHAR(255),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
);

SET FOREIGN_KEY_CHECKS=0;

INSERT INTO `users` (`id`, `name`) VALUES (1, 'Alice'), (2, 'Bob');
INSERT INTO `orders` (`order_id`, `user_id`, `product`, `customer_name`) VALUES 
(101, 1, 'Laptop', 'Alice'),
(102, 2, 'Mouse', 'Bob'),
(103, 1, 'Keyboard', 'Alicia'),
(104, 99, 'Monitor', 'Charlie');

SET FOREIGN_KEY_CHECKS=1;