-- src/db_setup.sql
CREATE TABLE Books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    isbn VARCHAR(13) UNIQUE,
    genre VARCHAR(50),
    publisher VARCHAR(100),
    year_published INTEGER,
    price REAL,
    quantity_in_stock INTEGER
);

CREATE TABLE Inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    location VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

CREATE TABLE Suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    contact_info VARCHAR(255)
);

CREATE TABLE Supplier_Book (
    supplier_book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER,
    book_id INTEGER,
    cost_price REAL,
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);