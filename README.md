# TradeTree

*Даталогическая схема базы данных*

![Даталогическая схема базы данных](https://raw.githubusercontent.com/asm4yar/trade-tree/main/docs/db/schema1.png)
![Даталогическая схема базы данных](https://raw.githubusercontent.com/asm4yar/trade-tree/main/docs/db/schema2.png)


```sql
-- Запрос на получение информации о сумме товаров заказанных под каждого приента 
-- (Наименование клиента, сумма)

select
	cs.name,
	sum(oi.unit_price * oi.qty ) as total_amount
from
	orders o
join order_items oi on
	o.id = oi.order_id
join customers cs on
	o.customer_id = cs.id
group by
	o.customer_id,
	cs.name
order by
	total_amount desc

```

```sql
-- Возвращает число дочерних категорий для категорий первого уровня.
-- (id, категория, кол-во дочерних)
-- 

select
	c.id,
	c.name,
	COUNT(child.id) as children_count
from
	categories c
join categories parent on
	parent.id = c.parent_id
left join categories child on
	child.parent_id = c.id
where
	parent.parent_id is null
group by
	c.id,
	c.name
order by
	c.name;

```

```sql
-- "Топ-5 самых покупаемых товаров за последний месяц"

CREATE OR REPLACE VIEW v_top5_products_last_30_days as 
with recursive sales as (
select
	oi.product_id,
	SUM(oi.qty) as sold_qty
from
	order_items oi
join orders o on
	o.id = oi.order_id
where
	o.created_at >= now() - interval '30 days'
group by
	oi.product_id
),
start_cats as (
select
	distinct p.category_id
from
	products p
join sales s on
	s.product_id = p.id
),
cat_up as (
select
	sc.category_id as start_cat_id,
	c.id as cur_cat_id,
	c.parent_id,
	c.name
from
	start_cats sc
join categories c on
	c.id = sc.category_id
union all
select
	cu.start_cat_id,
	p.id as cur_cat_id,
	p.parent_id,
	p.name
from
	cat_up cu
join categories p on
	p.id = cu.parent_id
),
root_cat as (
select
	start_cat_id,
	cur_cat_id as root_category_id,
	name as root_category_name
from
	cat_up
where
	parent_id is null
)
select
	p.name as product_name,
	rc.root_category_name as category_level1,
	s.sold_qty as total_sold_qty
from
	sales s
join products p on
	p.id = s.product_id
join root_cat rc on
	rc.start_cat_id = p.category_id
order by
	s.sold_qty desc,
	p.name
limit 5;

```