-- active_users_view の定義
CREATE VIEW active_users_view AS
SELECT id, name, email
FROM users
WHERE status = 'active';
