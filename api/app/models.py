"""SQLAlchemy models. Must match docs/schema.md and the hand-written migration in alembic/versions."""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Date, ForeignKey, Identity, Index, Integer, MetaData,
    Numeric, Sequence, Text, func, text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

TZ = TIMESTAMP(timezone=True)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_N_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s",
        "pk": "pk_%(table_name)s",
    })


def pk() -> Mapped[int]:
    return mapped_column(BigInteger, Identity(always=True), primary_key=True)


def fk(target: str, nullable: bool = False) -> Mapped[int]:
    return mapped_column(BigInteger, ForeignKey(target, ondelete="RESTRICT"), nullable=nullable)


invoice_no_seq = Sequence("invoice_no_seq", metadata=Base.metadata)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = pk()
    username: Mapped[str] = mapped_column(Text, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    __table_args__ = (CheckConstraint("role IN ('owner','sales')", name="role"),)


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = pk()
    name: Mapped[str] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(Text, index=True)
    address: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TZ, server_default=func.now())


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = pk()
    sku: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text)
    brand: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(Text)
    capacity_hp: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    is_inverter: Mapped[bool | None] = mapped_column(Boolean)
    price: Mapped[int] = mapped_column(BigInteger)
    warranty_months: Mapped[int | None] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    __table_args__ = (
        CheckConstraint("category IN ('aircon','accessory','service')", name="category"),
        CheckConstraint("price >= 0", name="price"),
        CheckConstraint("warranty_months > 0", name="warranty_months"),
        CheckConstraint(
            "category = 'aircon' OR (capacity_hp IS NULL AND is_inverter IS NULL AND warranty_months IS NULL)",
            name="aircon_fields",
        ),
    )


class Sale(Base):
    __tablename__ = "sales"
    id: Mapped[int] = pk()
    invoice_no: Mapped[str] = mapped_column(Text, unique=True)
    customer_id: Mapped[int | None] = fk("customers.id", nullable=True)
    user_id: Mapped[int] = fk("users.id")
    sold_at: Mapped[datetime] = mapped_column(TZ)
    total_amount: Mapped[int] = mapped_column(BigInteger)
    payment_status: Mapped[str] = mapped_column(Text)
    payment_method: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, server_default=text("'completed'"))
    voided_at: Mapped[datetime | None] = mapped_column(TZ)
    void_reason: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TZ, server_default=func.now())
    __table_args__ = (
        CheckConstraint("invoice_no ~ '^INV-[0-9]{6,}$'", name="invoice_no"),
        CheckConstraint("total_amount >= 0", name="total_amount"),
        CheckConstraint("payment_status IN ('paid','partial','unpaid')", name="payment_status"),
        CheckConstraint("payment_method IN ('cash','bank','kbzpay','wavepay','other')", name="payment_method"),
        CheckConstraint("status IN ('completed','void')", name="status"),
        CheckConstraint("payment_status = 'unpaid' OR payment_method IS NOT NULL", name="payment_method_required"),
        CheckConstraint(
            "(status = 'completed' AND voided_at IS NULL AND void_reason IS NULL)"
            " OR (status = 'void' AND voided_at IS NOT NULL AND void_reason IS NOT NULL)",
            name="void_fields",
        ),
        Index(None, "sold_at"),
        Index(None, "user_id", "sold_at"),
        Index(None, "customer_id"),
    )


class SaleItem(Base):
    __tablename__ = "sale_items"
    id: Mapped[int] = pk()
    sale_id: Mapped[int] = fk("sales.id")
    product_id: Mapped[int] = fk("products.id")
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[int] = mapped_column(BigInteger)
    line_total: Mapped[int] = mapped_column(BigInteger)
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity"),
        CheckConstraint("unit_price >= 0", name="unit_price"),
        CheckConstraint("line_total = quantity * unit_price", name="line_total"),
        Index(None, "sale_id"),
        Index(None, "product_id"),
    )


class SaleItemSerial(Base):
    __tablename__ = "sale_item_serials"
    id: Mapped[int] = pk()
    sale_item_id: Mapped[int] = fk("sale_items.id")
    serial_no: Mapped[str] = mapped_column(Text, unique=True)
    warranty_until: Mapped[date | None] = mapped_column(Date)
    __table_args__ = (Index(None, "sale_item_id"),)


class VoidedSaleSerial(Base):
    __tablename__ = "voided_sale_serials"
    id: Mapped[int] = pk()
    original_sale_item_id: Mapped[int] = fk("sale_items.id")
    serial_no: Mapped[str] = mapped_column(Text)
    warranty_until: Mapped[date | None] = mapped_column(Date)
    voided_at: Mapped[datetime] = mapped_column(TZ)
    __table_args__ = (Index(None, "original_sale_item_id"), Index(None, "serial_no"))
