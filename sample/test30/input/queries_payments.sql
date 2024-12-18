-- 特定の注文を削除
DELETE FROM orders
WHERE id = 15;

-- 支払い情報を取得
SELECT p.id, p.method, p.amount
FROM payments p
WHERE p.amount > 100;
