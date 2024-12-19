-- アクティブなユーザーの支払い情報を取得
SELECT up.user_id, up.order_id, up.payment_method, up.payment_amount
FROM user_order_payments_view up
WHERE up.payment_amount > 200;

-- ビューを使用した複雑なSELECT文
WITH high_value_payments AS (
    SELECT up.user_id, up.order_id, up.payment_method, up.payment_amount
    FROM user_order_payments_view up
    WHERE up.payment_amount > 500
)
SELECT hvp.user_id, hvp.order_id, hvp.payment_method, hvp.payment_amount
FROM high_value_payments hvp
JOIN users u ON hvp.user_id = u.id
WHERE u.status = 'active';
