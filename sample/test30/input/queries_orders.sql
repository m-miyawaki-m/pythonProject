-- 新しい注文を挿入
INSERT INTO orders (user_id, amount, status)
VALUES (1, 250.00, 'pending');

-- 注文のステータスを更新
UPDATE orders
SET status = 'shipped'
WHERE id = 10;
