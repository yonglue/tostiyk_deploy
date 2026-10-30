"""cleanup orphans and narrow nullable

Revision ID: cleanup_orphans_01
Revises: 4f7b4846ede7
Create Date: 2026-10-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cleanup_orphans_01"
down_revision: Union[str, Sequence[str], None] = "4f7b4846ede7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 1) 删孤儿表 inventory_adjustment
    if insp.has_table("inventory_adjustment"):
        for ix in (
            "ix_inventory_adjustment_adjust_no",
            "ix_inventory_adjustment_part_id",
            "ix_inventory_adjustment_request_id",
        ):
            try:
                op.drop_index(ix, table_name="inventory_adjustment")
            except Exception:
                pass
        op.drop_table("inventory_adjustment")

    # 2) 删 client.price_tier
    cols = {c["name"] for c in insp.get_columns("client")}
    if "price_tier" in cols:
        with op.batch_alter_table("client") as batch_op:
            batch_op.drop_column("price_tier")

    # 3) autopart vip 列收紧为 NOT NULL
    with op.batch_alter_table("autopart") as batch_op:
        batch_op.alter_column(
            "vip2_price",
            existing_type=sa.Float(),
            nullable=False,
            existing_server_default="0.0",
            server_default="0.0",
        )
        batch_op.alter_column(
            "vip3_price",
            existing_type=sa.Float(),
            nullable=False,
            existing_server_default="0.0",
            server_default="0.0",
        )


def downgrade() -> None:
    with op.batch_alter_table("autopart") as batch_op:
        batch_op.alter_column(
            "vip2_price",
            existing_type=sa.Float(),
            nullable=True,
            existing_server_default="0.0",
            server_default="0.0",
        )
        batch_op.alter_column(
            "vip3_price",
            existing_type=sa.Float(),
            nullable=True,
            existing_server_default="0.0",
            server_default="0.0",
        )

    with op.batch_alter_table("client") as batch_op:
        batch_op.add_column(sa.Column("price_tier", sa.String(), nullable=True))
