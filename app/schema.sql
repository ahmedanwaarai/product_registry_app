-- MySQL schema for Secure Product Registration System
-- Compatible with MySQL 5.7+/8.0

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL,
  email VARCHAR(190) NOT NULL UNIQUE,
  mobile VARCHAR(30) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  cnic VARCHAR(20) NOT NULL,
  user_type ENUM('user','shopkeeper','admin') NOT NULL DEFAULT 'user',
  shop_name VARCHAR(150) DEFAULT NULL,
  shopkeeper_status ENUM('pending','approved') DEFAULT 'approved',
  created_at DATETIME NOT NULL,
  INDEX (user_type),
  INDEX (cnic)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS admin_roles (
  user_id INT PRIMARY KEY,
  access_level ENUM('full','limited') NOT NULL DEFAULT 'limited',
  CONSTRAINT fk_admin_roles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS brands (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  serial VARCHAR(100) NOT NULL UNIQUE,
  category_id INT NULL,
  brand_id INT NULL,
  status ENUM('for_sale','locked','stolen') NOT NULL DEFAULT 'for_sale',
  owner_user_id INT NOT NULL,
  registered_at DATETIME NOT NULL,
  last_status_change_at DATETIME NOT NULL,
  CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES product_categories(id) ON DELETE SET NULL,
  CONSTRAINT fk_products_brand FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL,
  CONSTRAINT fk_products_owner FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX (status),
  INDEX (owner_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_status_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  status ENUM('for_sale','locked','stolen') NOT NULL,
  changed_by_user_id INT NULL,
  changed_at DATETIME NOT NULL,
  note VARCHAR(255) NULL,
  CONSTRAINT fk_status_log_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  CONSTRAINT fk_status_log_user FOREIGN KEY (changed_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
  INDEX (product_id),
  INDEX (changed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_ownerships (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  user_id INT NOT NULL,
  acquired_at DATETIME NOT NULL,
  method VARCHAR(50) NOT NULL,
  CONSTRAINT fk_ownerships_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  CONSTRAINT fk_ownerships_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX (product_id),
  INDEX (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sale_deals (
  id INT AUTO_INCREMENT PRIMARY KEY,
  buyer_user_id INT NOT NULL,
  seller_user_id INT NOT NULL,
  seller_name VARCHAR(150) NOT NULL,
  seller_mobile VARCHAR(50) NOT NULL,
  seller_cnic VARCHAR(30) NOT NULL,
  seller_address VARCHAR(255) NOT NULL,
  status ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL,
  decided_at DATETIME NULL,
  CONSTRAINT fk_deals_buyer FOREIGN KEY (buyer_user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_deals_seller FOREIGN KEY (seller_user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS deal_products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  deal_id INT NOT NULL,
  product_id INT NOT NULL,
  product_serial VARCHAR(100) NOT NULL,
  product_name VARCHAR(150) NOT NULL,
  brand_name VARCHAR(120) NULL,
  category_name VARCHAR(120) NULL,
  CONSTRAINT fk_dp_deal FOREIGN KEY (deal_id) REFERENCES sale_deals(id) ON DELETE CASCADE,
  CONSTRAINT fk_dp_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  INDEX (deal_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Optional requests log table
CREATE TABLE IF NOT EXISTS shopkeeper_requests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  requested_at DATETIME NOT NULL,
  status ENUM('pending','approved') NOT NULL DEFAULT 'pending',
  note VARCHAR(255) NULL,
  CONSTRAINT fk_shopreq_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed minimal data
INSERT INTO product_categories (name) VALUES ('Phone'), ('Laptop'), ('Tablet') ON DUPLICATE KEY UPDATE name = VALUES(name);
INSERT INTO brands (name) VALUES ('Generic'), ('BrandX'), ('BrandY') ON DUPLICATE KEY UPDATE name = VALUES(name);