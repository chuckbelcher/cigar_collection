CREATE TABLE cigars (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    purchase_location VARCHAR(200),
    purchase_date DATE,
    quantity INTEGER DEFAULT 0,
    rating INTEGER DEFAULT 0,
    archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
