from app.db import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Category, Product, Customer, Order, OrderItem
import random

COUNT_SEED_PRODUCTS = 200_000


def create_categories(db: Session, items, parent_id=None, leaf_ids=None):
    if leaf_ids is None:
        leaf_ids = []

    for item in items:
        cat = Category(name=item["name"], parent_id=parent_id)
        db.add(cat)
        db.commit()
        db.flush()

        children = item.get("children")
        if children:
            create_categories(db, children, cat.id, leaf_ids)
        else:
            leaf_ids.append(cat.id)

    return leaf_ids


def run():

    with SessionLocal() as db:
        try:
            has_any = db.execute(select(Category.id).limit(1)).scalar_one_or_none()
            if has_any:
                print("DB already seeded, skipping")
                return

            categories = [
                {
                    "name": "Бытовая техника",
                    "children": [
                        {"name": "Стиральные машины"},
                        {
                            "name": "Холодильники",
                            "children": [
                                {"name": "Однокамерные"},
                                {
                                    "name": "Двухкамерные",
                                    "children": [
                                        {
                                            "name": "Инверторные",
                                            "children": [{"name": "Встраиваемые"}],
                                        }
                                    ],
                                },
                            ],
                        },
                        {"name": "Телевизоры"},
                    ],
                },
                {
                    "name": "Компьютеры",
                    "children": [
                        {
                            "name": "Ноутбуки",
                            "children": [
                                {"name": '17"'},
                                {"name": '19"'},
                            ],
                        },
                        {"name": "Моноблоки"},
                    ],
                },
            ]

            leaf_cats = create_categories(db, categories)
            db.commit()

            customers = [
                Customer(name="ООО Ромашка", address="Москва, Твердская 1"),
                Customer(name="ИП Иванов", address="СПб, Невский 10"),
                Customer(name="ЗАО Тест", address="Казань, Кремль 3"),
            ]

            db.add_all(customers)
            db.flush()

            all_products = []
            for i in range(COUNT_SEED_PRODUCTS):
                cat_id = random.choice(leaf_cats)
                price = random.randint(10_000, 120_000)
                stock = random.randint(10, 100)
                all_products.append(
                    Product(
                        name=f"Product {i}",
                        price=price,
                        category_id=cat_id,
                        stock_qty=stock,
                    )
                )

            db.add_all(all_products)
            db.flush()

            for _ in range(300):
                cust = random.choice(customers)
                o = Order(customer_id=cust.id, status="submitted")
                db.add(o)
                db.flush()

                picks = random.sample(all_products, k=random.randint(1, 7))
                for p in picks:
                    qty = random.randint(1, 5)
                    db.add(
                        OrderItem(
                            order_id=o.id, product_id=p.id, qty=qty, unit_price=p.price
                        )
                    )

            db.commit()

            print("Seed done.")

        except Exception as e:
            print(e)


if "__main__" == __name__:
    run()
