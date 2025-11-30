USE orders_db;

-- Tablas básicas para empezar
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    public_id VARCHAR(36) UNIQUE NOT NULL,
    made_by_username VARCHAR(100) NOT NULL,
    status ENUM('PENDING', 'PAID', 'SHIPPED', 'CANCELLED') DEFAULT 'PENDING',
    total FLOAT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_public_id VARCHAR(36) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_image_src VARCHAR(500),             
    product_description TEXT,                    
    seller_username VARCHAR(100) NOT NULL,
    seller_name VARCHAR(200) NOT NULL,           
    seller_pfp VARCHAR(500),                     
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    total FLOAT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- Datos de prueba
INSERT IGNORE INTO orders (public_id, made_by_username, status, total) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'usuario_prueba', 'PENDING', 29.97);

INSERT IGNORE INTO order_items (order_id, product_public_id, product_name, seller_username, quantity, price, total) VALUES
(1, 'prod-001', 'Producto Prueba', 'vendedor_prueba', 2, 14.985, 29.97);

INSERT IGNORE INTO orders (public_id, made_by_username, status, total) VALUES
('770e8400-e29b-41d4-a716-446655440001', 'alvaro', 'PENDING', 29.97);

INSERT IGNORE INTO order_items (order_id, product_public_id, product_name, seller_username, quantity, price, total) VALUES
(2, 'prod-004', 'Camiseta', 'adam', 1, 11, 11);

-- Más pedidos
INSERT IGNORE INTO orders (public_id, made_by_username, status, total) VALUES
('880e8400-e29b-41d4-a716-446655440002', 'maria', 'PAID', 59.95),
('990e8400-e29b-41d4-a716-446655440003', 'juan', 'SHIPPED', 120.50),
('aa0e8400-e29b-41d4-a716-446655440004', 'lucia', 'CANCELLED', 75.00),
('bb0e8400-e29b-41d4-a716-446655440005', 'pepe', 'PENDING', 34.99);

INSERT IGNORE INTO order_items (order_id, product_public_id, product_name, seller_username, seller_name, quantity, price, total) VALUES
(3, 'prod-002', 'Auriculares Bluetooth', 'soundstore', 'SoundStore', 1, 29.95, 29.95),
(3, 'prod-003', 'Cargador USB-C', 'techmart', 'TechMart', 1, 30.00, 30.00);

INSERT IGNORE INTO order_items (order_id, product_public_id, product_name, seller_username, seller_name, quantity, price, total) VALUES
(4, 'prod-005', 'Monitor 24"', 'monitorex', 'MonitorEx', 1, 100.50, 100.50),
(4, 'prod-006', 'Teclado mecánico', 'keyshop', 'KeyShop', 1, 20.00, 20.00);

INSERT IGNORE INTO order_items (order_id, product_public_id, product_name, seller_username, seller_name, quantity, price, total) VALUES
(5, 'prod-007', 'Bolso de piel', 'fashionhub', 'FashionHub', 1, 50.00, 50.00),
(5, 'prod-008', 'Bufanda', 'fashionhub', 'FashionHub', 1, 25.00, 25.00);

INSERT IGNORE INTO order_items (order_id, product_public_id, product_name, seller_username, seller_name, quantity, price, total) VALUES
(6, 'prod-009', 'Libro "Aprendiendo SQL"', 'bookstore', 'BookStore', 1, 34.99, 34.99);