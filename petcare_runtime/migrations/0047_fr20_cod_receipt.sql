-- 0047 · FR-20 cash on delivery with digital receipting (MVC-BUILD-RUNNER-001 U14)
--
-- Ratified AC-FR-20-01/02. Prices are a tenant's append-only price history (latest wins), never sent
-- by the client. An order records its payment method (COD) and priced lines. Delivery writes the
-- collection confirmation and the receipt in ONE transaction; an order is paid only with a
-- confirmation of its exact total (CHECK against the stored total). Insert-only. Additive only.

CREATE TABLE IF NOT EXISTS tenant_price (
    price_id TEXT PRIMARY KEY,
    -- Insertion order: two prices set in the same instant resolve to the later write.
    seq BIGSERIAL NOT NULL,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    product_id TEXT NOT NULL CHECK (length(TRIM(product_id)) > 0),
    unit_price_halalas INTEGER NOT NULL CHECK (unit_price_halalas > 0),
    set_by_actor_id TEXT NOT NULL,
    set_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tenant_price ON tenant_price (tenant_id, product_id, set_at, seq);

CREATE TABLE IF NOT EXISTS customer_order (
    order_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    owner_id TEXT NOT NULL REFERENCES user_identity(user_id),
    payment_method TEXT NOT NULL CHECK (payment_method IN ('COD')),
    total_halalas INTEGER NOT NULL CHECK (total_halalas > 0),
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_customer_order_tenant ON customer_order (tenant_id, owner_id, created_at);

CREATE TABLE IF NOT EXISTS customer_order_line (
    order_id TEXT NOT NULL REFERENCES customer_order(order_id),
    line_no INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_halalas INTEGER NOT NULL CHECK (unit_price_halalas > 0),
    PRIMARY KEY (order_id, line_no)
);

CREATE TABLE IF NOT EXISTS order_collection (
    order_id TEXT PRIMARY KEY REFERENCES customer_order(order_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    amount_halalas INTEGER NOT NULL CHECK (amount_halalas > 0),
    reference TEXT NOT NULL CHECK (length(TRIM(reference)) > 0),
    source TEXT NOT NULL CHECK (source IN ('STAFF', 'PARTNER')),
    confirmed_by TEXT NOT NULL CHECK (length(TRIM(confirmed_by)) > 0),
    confirmed_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS order_receipt (
    receipt_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE REFERENCES order_collection(order_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    owner_id TEXT NOT NULL REFERENCES user_identity(user_id),
    language TEXT NOT NULL CHECK (language IN ('ar', 'en')),
    rendered TEXT NOT NULL CHECK (length(TRIM(rendered)) > 0),
    total_halalas INTEGER NOT NULL,
    issued_at TIMESTAMP NOT NULL
);
