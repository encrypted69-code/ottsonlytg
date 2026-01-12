-- =====================================================
-- REFERRAL + ADMIN PANEL DATABASE SCHEMA
-- Production-ready PostgreSQL schema
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE: users
-- Stores all users (customers, referrers, admins)
-- =====================================================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    referred_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    referral_level INTEGER DEFAULT 0 CHECK (referral_level IN (0, 1, 2)),
    referral_code VARCHAR(50) UNIQUE NOT NULL,
    user_type VARCHAR(20) DEFAULT 'customer' CHECK (user_type IN ('customer', 'referrer', 'admin', 'super_admin')),
    is_active BOOLEAN DEFAULT true,
    is_blocked BOOLEAN DEFAULT false,
    is_suspicious BOOLEAN DEFAULT false,
    device_id VARCHAR(255),
    ip_address VARCHAR(45),
    total_spent DECIMAL(10, 2) DEFAULT 0.00,
    total_orders INTEGER DEFAULT 0,
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_referred_by ON users(referred_by);
CREATE INDEX idx_users_referral_code ON users(referral_code);
CREATE INDEX idx_users_join_date ON users(join_date);
CREATE INDEX idx_users_user_type ON users(user_type);

-- =====================================================
-- TABLE: referrals
-- Tracks referral relationships and clicks
-- =====================================================
CREATE TABLE referrals (
    id BIGSERIAL PRIMARY KEY,
    referrer_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    referral_code VARCHAR(50) NOT NULL,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    converted BOOLEAN DEFAULT false,
    converted_at TIMESTAMP,
    level INTEGER DEFAULT 1 CHECK (level IN (1, 2)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_referrals_referrer_id ON referrals(referrer_id);
CREATE INDEX idx_referrals_referred_user_id ON referrals(referred_user_id);
CREATE INDEX idx_referrals_referral_code ON referrals(referral_code);
CREATE INDEX idx_referrals_converted ON referrals(converted);

-- =====================================================
-- TABLE: orders
-- All purchase orders
-- =====================================================
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_name VARCHAR(255) NOT NULL DEFAULT 'Combo OTT Plan',
    selling_price DECIMAL(10, 2) NOT NULL DEFAULT 135.00,
    making_cost DECIMAL(10, 2) NOT NULL DEFAULT 42.00,
    profit DECIMAL(10, 2) NOT NULL DEFAULT 93.00,
    payment_method VARCHAR(50) DEFAULT 'upi' CHECK (payment_method IN ('upi', 'wallet', 'other')),
    payment_status VARCHAR(50) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'success', 'failed', 'refunded')),
    upi_id VARCHAR(255),
    transaction_id VARCHAR(255),
    referral_source BIGINT REFERENCES users(id) ON DELETE SET NULL,
    is_wallet_payment BOOLEAN DEFAULT false,
    commission_eligible BOOLEAN DEFAULT true,
    commission_processed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_referral_source ON orders(referral_source);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_commission_eligible ON orders(commission_eligible, commission_processed);

-- =====================================================
-- TABLE: wallets
-- User wallet balances
-- =====================================================
CREATE TABLE wallets (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_balance DECIMAL(10, 2) DEFAULT 0.00,
    withdrawable_balance DECIMAL(10, 2) DEFAULT 0.00,
    pending_balance DECIMAL(10, 2) DEFAULT 0.00,
    total_earned DECIMAL(10, 2) DEFAULT 0.00,
    total_withdrawn DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wallets_user_id ON wallets(user_id);

-- =====================================================
-- TABLE: wallet_transactions
-- All wallet credit/debit transactions
-- =====================================================
CREATE TABLE wallet_transactions (
    id BIGSERIAL PRIMARY KEY,
    wallet_id BIGINT NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id BIGINT REFERENCES orders(id) ON DELETE SET NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('commission_credit', 'withdrawal', 'refund', 'deduction', 'purchase')),
    amount DECIMAL(10, 2) NOT NULL,
    balance_before DECIMAL(10, 2) NOT NULL,
    balance_after DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled')),
    referral_level INTEGER CHECK (referral_level IN (1, 2)),
    description TEXT,
    credited_at TIMESTAMP,
    available_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wallet_transactions_wallet_id ON wallet_transactions(wallet_id);
CREATE INDEX idx_wallet_transactions_user_id ON wallet_transactions(user_id);
CREATE INDEX idx_wallet_transactions_order_id ON wallet_transactions(order_id);
CREATE INDEX idx_wallet_transactions_type ON wallet_transactions(transaction_type);
CREATE INDEX idx_wallet_transactions_status ON wallet_transactions(status);
CREATE INDEX idx_wallet_transactions_available_at ON wallet_transactions(available_at);

-- =====================================================
-- TABLE: withdrawals
-- Withdrawal requests and history
-- =====================================================
CREATE TABLE withdrawals (
    id BIGSERIAL PRIMARY KEY,
    withdrawal_id VARCHAR(100) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    wallet_id BIGINT NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    withdrawal_method VARCHAR(50) DEFAULT 'upi' CHECK (withdrawal_method IN ('upi', 'bank', 'paytm')),
    upi_id VARCHAR(255),
    bank_account VARCHAR(255),
    ifsc_code VARCHAR(20),
    account_holder_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'paid', 'cancelled')),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    approved_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    paid_at TIMESTAMP,
    payment_reference VARCHAR(255),
    rejection_reason TEXT,
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_withdrawals_user_id ON withdrawals(user_id);
CREATE INDEX idx_withdrawals_wallet_id ON withdrawals(wallet_id);
CREATE INDEX idx_withdrawals_status ON withdrawals(status);
CREATE INDEX idx_withdrawals_requested_at ON withdrawals(requested_at);

-- =====================================================
-- TABLE: admin_logs
-- Audit trail for all admin actions
-- =====================================================
CREATE TABLE admin_logs (
    id BIGSERIAL PRIMARY KEY,
    admin_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),
    target_id BIGINT,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_logs_admin_id ON admin_logs(admin_id);
CREATE INDEX idx_admin_logs_action_type ON admin_logs(action_type);
CREATE INDEX idx_admin_logs_created_at ON admin_logs(created_at);

-- =====================================================
-- TABLE: fraud_flags
-- Track suspicious activity
-- =====================================================
CREATE TABLE fraud_flags (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    flag_type VARCHAR(100) NOT NULL CHECK (flag_type IN ('duplicate_upi', 'duplicate_device', 'duplicate_ip', 'high_referral_low_conversion', 'suspicious_pattern', 'manual_flag')),
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    metadata JSONB,
    auto_detected BOOLEAN DEFAULT true,
    flagged_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    resolved_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fraud_flags_user_id ON fraud_flags(user_id);
CREATE INDEX idx_fraud_flags_flag_type ON fraud_flags(flag_type);
CREATE INDEX idx_fraud_flags_resolved ON fraud_flags(resolved);
CREATE INDEX idx_fraud_flags_severity ON fraud_flags(severity);

-- =====================================================
-- TABLE: system_settings
-- Configurable system parameters
-- =====================================================
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(50) DEFAULT 'string' CHECK (setting_type IN ('string', 'number', 'boolean', 'json')),
    description TEXT,
    updated_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
    ('combo_selling_price', '135.00', 'number', 'Selling price of Combo OTT Plan'),
    ('combo_making_cost', '42.00', 'number', 'Making cost of Combo OTT Plan'),
    ('combo_profit', '93.00', 'number', 'Profit per sale'),
    ('level1_commission_percent', '30', 'number', 'Level 1 referral commission percentage'),
    ('level2_commission_percent', '10', 'number', 'Level 2 referral commission percentage'),
    ('level1_commission_amount', '28.00', 'number', 'Level 1 commission amount in rupees'),
    ('level2_commission_amount', '9.00', 'number', 'Level 2 commission amount in rupees'),
    ('commission_hold_hours', '24', 'number', 'Hours to hold commission before making withdrawable'),
    ('min_withdrawal_amount', '500.00', 'number', 'Minimum withdrawal amount'),
    ('referral_enabled', 'true', 'boolean', 'Enable/disable referral system'),
    ('withdrawal_enabled', 'true', 'boolean', 'Enable/disable withdrawals');

-- =====================================================
-- TABLE: referral_stats
-- Materialized view for referral performance
-- =====================================================
CREATE TABLE referral_stats (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_clicks INTEGER DEFAULT 0,
    total_referrals INTEGER DEFAULT 0,
    level1_referrals INTEGER DEFAULT 0,
    level2_referrals INTEGER DEFAULT 0,
    total_buyers INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5, 2) DEFAULT 0.00,
    total_commission_earned DECIMAL(10, 2) DEFAULT 0.00,
    total_commission_paid DECIMAL(10, 2) DEFAULT 0.00,
    pending_commission DECIMAL(10, 2) DEFAULT 0.00,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_referral_stats_user_id ON referral_stats(user_id);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wallets_updated_at BEFORE UPDATE ON wallets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_withdrawals_updated_at BEFORE UPDATE ON withdrawals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS FOR REPORTING
-- =====================================================

-- Daily dashboard stats
CREATE OR REPLACE VIEW daily_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(DISTINCT CASE WHEN DATE(join_date) = DATE(created_at) THEN id END) as new_users,
    COUNT(DISTINCT CASE WHEN total_orders > 0 AND DATE(join_date) = DATE(created_at) THEN id END) as buyers_today,
    0 as revenue_today,
    0 as profit_today,
    0 as referral_payout_today,
    COUNT(DISTINCT CASE WHEN referral_code IS NOT NULL THEN id END) as active_referrers
FROM users
GROUP BY DATE(created_at);

-- Top referrers leaderboard
CREATE OR REPLACE VIEW top_referrers AS
SELECT 
    u.id,
    u.telegram_id,
    u.username,
    u.first_name,
    rs.total_clicks,
    rs.total_buyers,
    rs.conversion_rate,
    rs.total_commission_earned,
    rs.total_commission_paid,
    rs.pending_commission
FROM users u
JOIN referral_stats rs ON u.id = rs.user_id
WHERE u.user_type IN ('referrer', 'admin')
ORDER BY rs.total_commission_earned DESC;

-- =====================================================
-- FUNCTIONS FOR BUSINESS LOGIC
-- =====================================================

-- Generate unique referral code
CREATE OR REPLACE FUNCTION generate_referral_code(p_user_id BIGINT)
RETURNS VARCHAR(50) AS $$
DECLARE
    v_code VARCHAR(50);
    v_exists BOOLEAN;
BEGIN
    LOOP
        v_code := 'REF' || LPAD(p_user_id::TEXT, 6, '0') || UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 4));
        SELECT EXISTS(SELECT 1 FROM users WHERE referral_code = v_code) INTO v_exists;
        EXIT WHEN NOT v_exists;
    END LOOP;
    RETURN v_code;
END;
$$ LANGUAGE plpgsql;

-- Update referral stats
CREATE OR REPLACE FUNCTION update_referral_stats(p_user_id BIGINT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO referral_stats (
        user_id,
        total_clicks,
        total_referrals,
        level1_referrals,
        level2_referrals,
        total_buyers,
        conversion_rate,
        total_commission_earned,
        total_commission_paid,
        pending_commission,
        last_updated
    )
    SELECT
        p_user_id,
        COALESCE((SELECT COUNT(*) FROM referrals WHERE referrer_id = p_user_id), 0),
        COALESCE((SELECT COUNT(DISTINCT referred_user_id) FROM referrals WHERE referrer_id = p_user_id), 0),
        COALESCE((SELECT COUNT(*) FROM users WHERE referred_by = p_user_id AND referral_level = 1), 0),
        COALESCE((SELECT COUNT(*) FROM users WHERE referred_by = p_user_id AND referral_level = 2), 0),
        COALESCE((SELECT COUNT(*) FROM referrals WHERE referrer_id = p_user_id AND converted = true), 0),
        CASE 
            WHEN COALESCE((SELECT COUNT(*) FROM referrals WHERE referrer_id = p_user_id), 0) > 0 
            THEN (COALESCE((SELECT COUNT(*) FROM referrals WHERE referrer_id = p_user_id AND converted = true), 0)::DECIMAL / 
                  COALESCE((SELECT COUNT(*) FROM referrals WHERE referrer_id = p_user_id), 1)) * 100
            ELSE 0
        END,
        COALESCE((SELECT SUM(amount) FROM wallet_transactions WHERE user_id = p_user_id AND transaction_type = 'commission_credit' AND status = 'completed'), 0),
        COALESCE((SELECT total_withdrawn FROM wallets WHERE user_id = p_user_id), 0),
        COALESCE((SELECT pending_balance FROM wallets WHERE user_id = p_user_id), 0),
        CURRENT_TIMESTAMP
    ON CONFLICT (user_id) DO UPDATE SET
        total_clicks = EXCLUDED.total_clicks,
        total_referrals = EXCLUDED.total_referrals,
        level1_referrals = EXCLUDED.level1_referrals,
        level2_referrals = EXCLUDED.level2_referrals,
        total_buyers = EXCLUDED.total_buyers,
        conversion_rate = EXCLUDED.conversion_rate,
        total_commission_earned = EXCLUDED.total_commission_earned,
        total_commission_paid = EXCLUDED.total_commission_paid,
        pending_commission = EXCLUDED.pending_commission,
        last_updated = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================
COMMENT ON TABLE users IS 'All users including customers, referrers, admins';
COMMENT ON TABLE referrals IS 'Tracks referral clicks and conversions';
COMMENT ON TABLE orders IS 'Purchase orders with commission eligibility';
COMMENT ON TABLE wallets IS 'User wallet balances';
COMMENT ON TABLE wallet_transactions IS 'All wallet transactions with 24h hold logic';
COMMENT ON TABLE withdrawals IS 'Withdrawal requests and approvals';
COMMENT ON TABLE admin_logs IS 'Audit trail for compliance';
COMMENT ON TABLE fraud_flags IS 'Fraud detection and prevention';
COMMENT ON TABLE system_settings IS 'Dynamic configuration management';
COMMENT ON TABLE referral_stats IS 'Cached referral performance metrics';
