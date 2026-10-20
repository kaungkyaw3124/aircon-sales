"""initial schema (docs/schema.md), written by hand

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TIMESTAMP

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

TZ = TIMESTAMP(timezone=True)


def pk():
    return sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True)


def fk(name, target, nullable=False):
    return sa.Column(name, sa.BigInteger, sa.ForeignKey(target, ondelete="RESTRICT"), nullable=nullable)


def upgrade() -> None:
    op.execute("CREATE SEQUENCE invoice_no_seq")

    op.create_table(
        "users",
        pk(),
        sa.Column("username", sa.Text, nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("full_name", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("username"),
        sa.CheckConstraint("role IN ('owner','sales')", name="role"),
    )

    op.create_table(
        "customers",
        pk(),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("phone", sa.Text),
        sa.Column("address", sa.Text),
        sa.Column("created_at", TZ, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_customers_phone", "customers", ["phone"])

    op.create_table(
        "products",
        pk(),
        sa.Column("sku", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("category", sa.Text, nullable=False),
        sa.Column("brand", sa.Text),
        sa.Column("model", sa.Text),
        sa.Column("capacity_hp", sa.Numeric(3, 1)),
        sa.Column("is_inverter", sa.Boolean),
        sa.Column("price", sa.BigInteger, nullable=False),
        sa.Column("warranty_months", sa.Integer),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("sku"),
        sa.CheckConstraint("category IN ('aircon','accessory','service')", name="category"),
        sa.CheckConstraint("price >= 0", name="price"),
        sa.CheckConstraint("warranty_months > 0", name="warranty_months"),
        sa.CheckConstraint(
            "category = 'aircon' OR (capacity_hp IS NULL AND is_inverter IS NULL AND warranty_months IS NULL)",
            name="aircon_fields",
        ),
    )

    op.create_table(
        "sales",
        pk(),
        sa.Column("invoice_no", sa.Text, nullable=False),
        fk("customer_id", "customers.id", nullable=True),
        fk("user_id", "users.id"),
        sa.Column("sold_at", TZ, nullable=False),
        sa.Column("total_amount", sa.BigInteger, nullable=False),
        sa.Column("payment_status", sa.Text, nullable=False),
        sa.Column("payment_method", sa.Text),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'completed'")),
        sa.Column("voided_at", TZ),
        sa.Column("void_reason", sa.Text),
        sa.Column("note", sa.Text),
        sa.Column("created_at", TZ, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("invoice_no"),
        sa.CheckConstraint("invoice_no ~ '^INV-[0-9]{6,}$'", name="invoice_no"),
        sa.CheckConstraint("total_amount >= 0", name="total_amount"),
        sa.CheckConstraint("payment_status IN ('paid','partial','unpaid')", name="payment_status"),
        sa.CheckConstraint("payment_method IN ('cash','bank','kbzpay','wavepay','other')", name="payment_method"),
        sa.CheckConstraint("status IN ('completed','void')", name="status"),
        sa.CheckConstraint("payment_status = 'unpaid' OR payment_method IS NOT NULL", name="payment_method_required"),
        sa.CheckConstraint(
            "(status = 'completed' AND voided_at IS NULL AND void_reason IS NULL)"
            " OR (status = 'void' AND voided_at IS NOT NULL AND void_reason IS NOT NULL)",
            name="void_fields",
        ),
    )
    op.create_index("ix_sales_sold_at", "sales", ["sold_at"])
    op.create_index("ix_sales_user_id_sold_at", "sales", ["user_id", "sold_at"])
    op.create_index("ix_sales_customer_id", "sales", ["customer_id"])

    op.create_table(
        "sale_items",
        pk(),
        fk("sale_id", "sales.id"),
        fk("product_id", "products.id"),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("unit_price", sa.BigInteger, nullable=False),
        sa.Column("line_total", sa.BigInteger, nullable=False),
        sa.CheckConstraint("quantity > 0", name="quantity"),
        sa.CheckConstraint("unit_price >= 0", name="unit_price"),
        sa.CheckConstraint("line_total = quantity * unit_price", name="line_total"),
    )
    op.create_index("ix_sale_items_sale_id", "sale_items", ["sale_id"])
    op.create_index("ix_sale_items_product_id", "sale_items", ["product_id"])

    op.create_table(
        "sale_item_serials",
        pk(),
        fk("sale_item_id", "sale_items.id"),
        sa.Column("serial_no", sa.Text, nullable=False),
        sa.Column("warranty_until", sa.Date),
        sa.UniqueConstraint("serial_no"),
    )
    op.create_index("ix_sale_item_serials_sale_item_id", "sale_item_serials", ["sale_item_id"])

    op.create_table(
        "voided_sale_serials",
        pk(),
        fk("original_sale_item_id", "sale_items.id"),
        sa.Column("serial_no", sa.Text, nullable=False),
        sa.Column("warranty_until", sa.Date),
        sa.Column("voided_at", TZ, nullable=False),
    )
    op.create_index("ix_voided_sale_serials_original_sale_item_id", "voided_sale_serials", ["original_sale_item_id"])
    op.create_index("ix_voided_sale_serials_serial_no", "voided_sale_serials", ["serial_no"])


def downgrade() -> None:
    for table in ("voided_sale_serials", "sale_item_serials", "sale_items", "sales", "products", "customers", "users"):
        op.drop_table(table)
    op.execute("DROP SEQUENCE invoice_no_seq")
