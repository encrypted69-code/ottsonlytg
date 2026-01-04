-- =====================================================
-- SUPABASE DATABASE SCHEMA FOR OTT BOT
-- =====================================================
-- Paste this entire file into Supabase SQL Editor
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. USERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    wallet INTEGER DEFAULT 0 CHECK (wallet >= 0),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    referred_by BIGINT,
    referrals BIGINT[] DEFAULT '{}',
    processed_payments TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast telegram_id lookups
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_referred_by ON users(referred_by);

-- =====================================================
-- 2. PLANS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS plans (
    id SERIAL PRIMARY KEY,
    plan_key TEXT UNIQUE NOT NULL,
    ott_name TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0),
    description TEXT DEFAULT '',
    stock INTEGER DEFAULT 0 CHECK (stock >= 0),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast plan_key lookups
CREATE INDEX IF NOT EXISTS idx_plans_plan_key ON plans(plan_key);
CREATE INDEX IF NOT EXISTS idx_plans_active ON plans(active);

-- =====================================================
-- 3. STOCKS TABLE (OTT Credentials Inventory)
-- =====================================================
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    plan_key TEXT NOT NULL,
    credential TEXT NOT NULL,
    is_used BOOLEAN DEFAULT false,
    used_by BIGINT,
    used_at TIMESTAMPTZ,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (plan_key) REFERENCES plans(plan_key) ON DELETE CASCADE,
    FOREIGN KEY (used_by) REFERENCES users(telegram_id) ON DELETE SET NULL
);

-- Indexes for stock management
CREATE INDEX IF NOT EXISTS idx_stocks_plan_key ON stocks(plan_key);
CREATE INDEX IF NOT EXISTS idx_stocks_is_used ON stocks(is_used);
CREATE INDEX IF NOT EXISTS idx_stocks_used_by ON stocks(used_by);

-- =====================================================
-- 4. SUBSCRIPTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    plan_key TEXT NOT NULL,
    credential TEXT,
    purchased_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_key) REFERENCES plans(plan_key) ON DELETE CASCADE
);

-- Indexes for subscription lookups
CREATE INDEX IF NOT EXISTS idx_subscriptions_telegram_id ON subscriptions(telegram_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_key ON subscriptions(plan_key);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

-- =====================================================
-- 5. TRANSACTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    description TEXT NOT NULL,
    amount INTEGER NOT NULL,
    transaction_type TEXT DEFAULT 'credit' CHECK (transaction_type IN ('credit', 'debit', 'purchase', 'refund', 'referral_bonus')),
    payment_id TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);

-- Indexes for transaction queries
CREATE INDEX IF NOT EXISTS idx_transactions_telegram_id ON transactions(telegram_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_payment_id ON transactions(payment_id);

-- =====================================================
-- 6. TRIGGER FOR UPDATED_AT TIMESTAMP
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to plans table
CREATE TRIGGER update_plans_updated_at
    BEFORE UPDATE ON plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 7. FUNCTION: GET AVAILABLE STOCK COUNT
-- =====================================================
CREATE OR REPLACE FUNCTION get_available_stock(p_plan_key TEXT)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM stocks
        WHERE plan_key = p_plan_key AND is_used = false
    );
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. FUNCTION: UPDATE PLAN STOCK COUNT
-- =====================================================
CREATE OR REPLACE FUNCTION update_plan_stock_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE plans
    SET stock = (
        SELECT COUNT(*)
        FROM stocks
        WHERE plan_key = NEW.plan_key AND is_used = false
    )
    WHERE plan_key = NEW.plan_key;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update plan stock when stocks change
CREATE TRIGGER update_plan_stock_on_insert
    AFTER INSERT ON stocks
    FOR EACH ROW
    EXECUTE FUNCTION update_plan_stock_count();

CREATE TRIGGER update_plan_stock_on_update
    AFTER UPDATE ON stocks
    FOR EACH ROW
    EXECUTE FUNCTION update_plan_stock_count();

-- =====================================================
-- SCHEMA COMPLETE
-- =====================================================
-- Now you can run the migration script to import JSON data
-- =====================================================
