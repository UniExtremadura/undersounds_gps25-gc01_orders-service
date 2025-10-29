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

-- Datos de prueba mínimos
INSERT IGNORE INTO orders (public_id, made_by_username, status, total) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'usuario_prueba', 'PENDING', 29.97);

INSERT IGNORE INTO order_items (order_id, product_public_id, product_name, seller_username, quantity, price, total) VALUES
(1, 'prod-001', 'Producto Prueba', 'vendedor_prueba', 2, 14.985, 29.97);