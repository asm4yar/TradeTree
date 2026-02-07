```sql
EXPLAIN (ANALYZE, BUFFERS)
select * from v_top5_products_last_30_days
```

```text
Limit  (cost=11854.89..11854.90 rows=5 width=54) (actual time=121.170..121.182 rows=5 loops=1)
  Buffers: shared hit=6906, temp read=1671 written=1671
  CTE sales
    ->  HashAggregate  (cost=45.32..57.38 rows=1206 width=16) (actual time=1.127..1.386 rows=1206 loops=1)
          Group Key: oi.product_id
          Batches: 1  Memory Usage: 193kB
          Buffers: shared hit=15
          ->  Hash Join  (cost=12.00..39.28 rows=1207 width=12) (actual time=0.208..0.700 rows=1207 loops=1)
                Hash Cond: (oi.order_id = o.id)
                Buffers: shared hit=15
                ->  Seq Scan on order_items oi  (cost=0.00..24.07 rows=1207 width=20) (actual time=0.006..0.117 rows=1207 loops=1)
                      Buffers: shared hit=12
                ->  Hash  (cost=8.25..8.25 rows=300 width=8) (actual time=0.196..0.196 rows=300 loops=1)
                      Buckets: 1024  Batches: 1  Memory Usage: 20kB
                      Buffers: shared hit=3
                      ->  Seq Scan on orders o  (cost=0.00..8.25 rows=300 width=8) (actual time=0.010..0.135 rows=300 loops=1)
                            Filter: (created_at >= (now() - '30 days'::interval))
                            Buffers: shared hit=3
  CTE cat_up
    ->  Recursive Union  (cost=6559.59..6852.04 rows=707 width=56) (actual time=5.014..5.084 rows=20 loops=1)
          Buffers: shared hit=4829
          ->  Hash Join  (cost=6559.59..6581.84 rows=7 width=56) (actual time=5.013..5.020 rows=7 loops=1)
                Hash Cond: (c.id = p_1.category_id)
                Buffers: shared hit=4825
                ->  Seq Scan on categories c  (cost=0.00..19.70 rows=970 width=48) (actual time=0.003..0.004 rows=13 loops=1)
                      Buffers: shared hit=1
                ->  Hash  (cost=6559.50..6559.50 rows=7 width=8) (actual time=5.000..5.002 rows=7 loops=1)
                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                      Buffers: shared hit=4824
                      ->  Unique  (cost=6553.47..6559.50 rows=7 width=8) (actual time=4.834..4.996 rows=7 loops=1)
                            Buffers: shared hit=4824
                            ->  Sort  (cost=6553.47..6556.48 rows=1206 width=8) (actual time=4.833..4.910 rows=1206 loops=1)
                                  Sort Key: p_1.category_id
                                  Sort Method: quicksort  Memory: 49kB
                                  Buffers: shared hit=4824
                                  ->  Nested Loop  (cost=0.42..6491.75 rows=1206 width=8) (actual time=0.016..4.677 rows=1206 loops=1)
                                        Buffers: shared hit=4824
                                        ->  CTE Scan on sales s_1  (cost=0.00..24.12 rows=1206 width=8) (actual time=0.000..0.663 rows=1206 loops=1)
                                        ->  Index Scan using products_pkey on products p_1  (cost=0.42..5.36 rows=1 width=16) (actual time=0.003..0.003 rows=1 loops=1206)
                                              Index Cond: (id = s_1.product_id)
                                              Buffers: shared hit=4824
          ->  Hash Join  (cost=2.28..26.31 rows=70 width=56) (actual time=0.007..0.010 rows=3 loops=5)
                Hash Cond: (p_2.id = cu.parent_id)
                Buffers: shared hit=4
                ->  Seq Scan on categories p_2  (cost=0.00..19.70 rows=970 width=48) (actual time=0.002..0.003 rows=13 loops=4)
                      Buffers: shared hit=4
                ->  Hash  (cost=1.40..1.40 rows=70 width=16) (actual time=0.003..0.003 rows=3 loops=5)
                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                      ->  WorkTable Scan on cat_up cu  (cost=0.00..1.40 rows=70 width=16) (actual time=0.001..0.001 rows=4 loops=5)
  ->  Sort  (cost=4945.47..4945.53 rows=24 width=54) (actual time=121.168..121.171 rows=5 loops=1)
        Sort Key: s.sold_qty DESC, p.name
        Sort Method: top-N heapsort  Memory: 26kB
        Buffers: shared hit=6906, temp read=1671 written=1671
        ->  Hash Join  (cost=4916.19..4945.07 rows=24 width=54) (actual time=101.634..120.878 rows=1206 loops=1)
              Hash Cond: (s.product_id = p.id)
              Buffers: shared hit=6906, temp read=1671 written=1671
              ->  CTE Scan on sales s  (cost=0.00..24.12 rows=1206 width=16) (actual time=1.129..1.224 rows=1206 loops=1)
                    Buffers: shared hit=15
              ->  Hash  (cost=4866.19..4866.19 rows=4000 width=54) (actual time=100.438..100.440 rows=200000 loops=1)
                    Buckets: 131072 (originally 4096)  Batches: 4 (originally 1)  Memory Usage: 7169kB
                    Buffers: shared hit=6891, temp written=1281
                    ->  Hash Join  (cost=14.19..4866.19 rows=4000 width=54) (actual time=5.113..55.144 rows=200000 loops=1)
                          Hash Cond: (p.category_id = cat_up.start_cat_id)
                          Buffers: shared hit=6891
                          ->  Seq Scan on products p  (cost=0.00..4062.00 rows=200000 width=30) (actual time=0.004..11.334 rows=200000 loops=1)
                                Buffers: shared hit=2062
                          ->  Hash  (cost=14.14..14.14 rows=4 width=40) (actual time=5.098..5.099 rows=7 loops=1)
                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                Buffers: shared hit=4829
                                ->  CTE Scan on cat_up  (cost=0.00..14.14 rows=4 width=40) (actual time=5.048..5.091 rows=7 loops=1)
                                      Filter: (parent_id IS NULL)
                                      Rows Removed by Filter: 13
                                      Buffers: shared hit=4829
Planning:
  Buffers: shared hit=121
Planning Time: 1.180 ms
Execution Time: 121.296 ms
```