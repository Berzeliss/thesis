SELECT
    SUM(l_extendedprice * l_discount) AS revenue
FROM
    lineitem
WHERE
    l_shipdate >= DATE '1995-01-01'
    AND l_shipdate < DATE '1995-01-01' + INTERVAL '18 month'
    AND l_discount BETWEEN 0.05 - 0.01 AND 0.05 + 0.01
    AND l_quantity < 24;