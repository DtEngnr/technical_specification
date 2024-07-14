CREATE TABLE sales (
    date Date,
    article_id UInt32,
    is_pb Bool,
    quantity UInt16
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, article_id);

CREATE TABLE temp_mv
(
	date Date,
	rows_count UInt32,
    article_id_count UInt32,
    pb_sales UInt64,
    atd_sales UInt64,
    s_sales UInt64
) ENGINE = MergeTree()
ORDER BY date;

CREATE MATERIALIZED VIEW temp_view TO temp_mv
AS SELECT
    date,
    count() AS rows_count,
    uniq(article_id) AS article_id_count,
    sumIf(quantity, is_pb = 1) AS pb_sales,
    sumIf(quantity, is_pb = 0) AS atd_sales,
    sum(quantity) AS s_sales
FROM sales
GROUP BY date;

CREATE TABLE sales_mv
(
	date Date,
	rows_count UInt32,
    article_id_count UInt32,
    pb_sales UInt64,
    atd_sales UInt64,
    s_sales UInt64
) ENGINE = MergeTree()
ORDER BY date;

CREATE MATERIALIZED VIEW sales_view TO sales_mv
AS SELECT
    date,
    sum(rows_count) AS rows_count,
    MAX(article_id_count) AS article_id_count,
    sum(pb_sales) AS pb_sales,
    sum(atd_sales) AS atd_sales,
    sum(s_sales) AS s_sales
FROM temp_mv
GROUP BY date;

insert into sales 
select 
toDate('2024-01-01') date,
1000000 + rand() % 100  article_id , 
article_id % 2 is_pb,
rand() % 1000 as quantity 
from numbers(6000000);

insert into sales 
select 
toDate('2024-01-02') date,
1000000 + rand() % 100  article_id , 
article_id % 2 is_pb,
rand() % 1000 as quantity 
from numbers(6000000);

insert into sales 
select 
toDate('2024-01-03') date,
1000000 + rand() % 100  article_id , 
article_id % 2 is_pb,
rand() % 1000 as quantity 
from numbers(6000000);