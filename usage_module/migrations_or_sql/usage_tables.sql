-- 用户级大模型用量 / 限免额度 — 表结构
-- 在接入方数据库中执行此脚本后，挂载 usage 模块路由并设置 USAGE_DATABASE_URL 即可使用。
-- 若接入方已有 users 表且含 ai_platform_tokens_used / ai_platform_tokens_limit 列，
-- 可仅建 usage_records 表用于明细与计费，额度读写改走接入方 User 表（需在接入层自行对接）。

-- 每用户用量与额度（聚合）
CREATE TABLE IF NOT EXISTS user_llm_usage (
    user_id UUID PRIMARY KEY,
    tokens_used BIGINT NOT NULL DEFAULT 0,
    tokens_limit BIGINT,
    subscription_tier VARCHAR(20) NOT NULL DEFAULT 'free',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE user_llm_usage IS '每用户 LLM token 已用量与额度上限';
COMMENT ON COLUMN user_llm_usage.tokens_limit IS 'NULL 时使用配置默认 DEFAULT_TOKEN_LIMIT';

-- 用量明细（可选，用于计费/对账；需在配置中开启 ENABLE_USAGE_RECORDS）
CREATE TABLE IF NOT EXISTS usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tokens INTEGER NOT NULL,
    model_id VARCHAR(100),
    cost_cent INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usage_records_user_id ON usage_records (user_id);
CREATE INDEX IF NOT EXISTS idx_usage_records_created_at ON usage_records (created_at);

COMMENT ON TABLE usage_records IS '每次调用的 token 与可选费用记录，便于对账与计费';
