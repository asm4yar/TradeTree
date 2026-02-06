from fastapi import APIRouter, Depends, HTTPException
from app.api.catalog.schemas import AddItemRequest, AddItemResponse, clientStatistics
from app.db import get_db
from app.models import Order, Product, OrderItem
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

router = APIRouter(prefix="/orders", tags=["Catalog / Orders"])

SQL_CLIENT_STATISTICS = text(
    """
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

"""
)


@router.get("/clients/statistics", response_model=list[clientStatistics])
def client_statistics(db: Session = Depends(get_db)):
    res = db.execute(SQL_CLIENT_STATISTICS)
    rows = res.mappings().all()
    return rows


@router.post("/{order_id}/items", response_model=AddItemResponse)
def add_item_to_order(
    order_id: int, payload: AddItemRequest, db: Session = Depends(get_db)
):
    """
    Добавить товары в заказ:
    - если позиция уже есть, увеличить qty
    - если не хватает остатков, вернуть 409
    """

    order_exists = db.execute(
        select(Order.id).where(Order.id == order_id)
    ).scalar_one_or_none()
    if order_exists is None:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        with db.begin():
            product: Product | None = db.execute(
                select(Product)
                .where(Product.id == payload.product_id)
                .with_for_update()
            ).scalar_one_or_none()

            if product is None:
                raise HTTPException(status_code=404, detail="Product not found")

            if product.stock_qty < payload.quantity:
                raise HTTPException(status_code=409, detail="Not enough stock")

            # списываем остаток
            product.stock_qty -= payload.quantity

            # upset в order_items
            stmt = (
                pg_insert(OrderItem)
                .values(
                    order_id=order_id,
                    product_id=payload.product_id,
                    qty=payload.quantity,
                    unit_price=product.price,
                )
                .on_conflict_do_update(
                    index_elements=[OrderItem.order_id, OrderItem.product_id],
                    set_={
                        OrderItem.qty: OrderItem.qty + payload.quantity,
                        OrderItem.unit_price: OrderItem.unit_price,
                    },
                )
                .returning(OrderItem.qty)
            )

            new_qty = db.execute(stmt).scalar_one()

            db.flush()

            return AddItemResponse(
                order_id=order_id,
                product_id=payload.product_id,
                new_qty=int(new_qty),
                remaining_stock=int(product.stock_qty),
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internet server error")
