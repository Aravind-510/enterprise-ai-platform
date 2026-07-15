CREATE TABLE roles (

    id SERIAL PRIMARY KEY,

    role_name VARCHAR(50) UNIQUE NOT NULL

);

CREATE TABLE users (

    id SERIAL PRIMARY KEY,

    name VARCHAR(100),

    email VARCHAR(120) UNIQUE,

    password_hash TEXT,

    role_id INTEGER REFERENCES roles(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE permissions (

    id SERIAL PRIMARY KEY,

    permission_name VARCHAR(100),

    module VARCHAR(100)

);

CREATE TABLE audit_logs (

    id SERIAL PRIMARY KEY,

    user_id INTEGER REFERENCES users(id),

    action TEXT,

    endpoint TEXT,

    ip_address VARCHAR(50),

    status VARCHAR(20),

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);