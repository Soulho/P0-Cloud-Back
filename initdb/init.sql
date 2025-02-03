DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'tareasdb') THEN
        CREATE DATABASE tareasdb;
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'fastapi_user') THEN
        CREATE USER fastapi_user WITH ENCRYPTED PASSWORD 'password';
    END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE tareasdb TO fastapi_user;


