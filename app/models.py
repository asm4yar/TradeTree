"""ORM-модели предметной области каталога и заказов."""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    BigInteger,
    Text,
    Integer,
    Numeric,
    ForeignKey,
    DateTime,
    func,
    Index,
    DECIMAL,
)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей приложения."""

    pass


class Category(Base):
    """Категория товаров с поддержкой иерархии через parent_id."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("ix_categories_parent_id", parent_id),)


class Product(Base):
    """Товар, принадлежащий категории и имеющий складской остаток."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    stock_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[DECIMAL] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    __table_args__ = (Index("idx_products_category_id", category_id),)


class Customer(Base):
    """Покупатель, размещающий заказы в системе."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Order(Base):
    """Заказ покупателя со статусом жизненного цикла."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_orders_customer_id", customer_id),
        Index("ix_orders_created_at", created_at),
        Index("ix_orders_status", status),
    )


class OrderItem(Base):
    """Позиция заказа с количеством и зафиксированной ценой единицы товара."""

    __tablename__ = "order_items"
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id", ondelete="RESTRICT"), primary_key=True
    )
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[DECIMAL] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_order_items_product_id", product_id),)
