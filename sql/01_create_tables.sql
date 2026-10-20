-- PostgreSQL staging schema for the migration-quality portfolio project.

CREATE SCHEMA IF NOT EXISTS migration_demo;
SET search_path TO migration_demo;

CREATE TABLE legacy_customers (
    client_id       INTEGER PRIMARY KEY,
    client_name     TEXT NOT NULL,
    email           TEXT,
    phone           TEXT,
    country         TEXT,
    signup_date     DATE,
    segment_code    TEXT
);

CREATE TABLE legacy_orders (
    order_id        INTEGER PRIMARY KEY,
    client_id       INTEGER,
    order_date      DATE,
    amount          NUMERIC(14, 2),
    currency        CHAR(3),
    status          TEXT,
    channel         TEXT
);

CREATE TABLE target_customers (
    customer_id        INTEGER PRIMARY KEY,
    legacy_client_id   INTEGER,
    customer_full_name TEXT,
    email_address      TEXT,
    created_at         TIMESTAMP,
    phone_e164         TEXT,
    country_code       CHAR(2),
    customer_tier      TEXT
);

CREATE TABLE target_orders (
    order_key       INTEGER PRIMARY KEY,
    legacy_order_id INTEGER,
    ordered_at      TIMESTAMP,
    order_status    TEXT,
    sales_channel   TEXT,
    customer_id     INTEGER,
    amount_clp      NUMERIC(16, 2)
);

