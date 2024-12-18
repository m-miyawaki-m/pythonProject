-- ユーザー情報を取得
SELECT u.id, u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active' AND o.amount > 100;

-- 新しい注文を挿入
INSERT INTO orders (user_id, total, amount)
VALUES (1, 250.00, 5);

-- 注文のステータスを更新
UPDATE orders
SET status = 'shipped'
WHERE id = 10;

-- 特定の注文を削除
DELETE FROM orders
WHERE id = 15;
