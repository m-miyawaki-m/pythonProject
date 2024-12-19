-- ユーザー情報を取得
SELECT u.id, u.name, u.email
FROM users u
WHERE u.status = 'active';
