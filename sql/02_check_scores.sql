-- After running src/score_customers.py:
-- how many customers were scored, and how many are above the 0.5 line?
SELECT COUNT(*) AS scored,
       SUM(CASE WHEN score > 0.5 THEN 1 ELSE 0 END) AS flagged
FROM customer_scores;

-- The call list: top 100 customers with their details
SELECT c.first_name, c.last_name, c.province, c.loyalty_tier, s.score
FROM customer_scores s
JOIN customers c ON c.customer_id = s.customer_id
ORDER BY s.score DESC
LIMIT 100;
