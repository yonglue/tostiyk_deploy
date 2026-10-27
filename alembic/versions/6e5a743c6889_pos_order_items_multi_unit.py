"""pos_order_items_multi_unit

Revision ID: 6e5a743c6889
Revises: f32ccd095e90
Create Date: 2026-10-27 18:13:47.385551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e5a743c6889'
down_revision: Union[str, Sequence[str], None] = 'f32ccd095e90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 🌟 大段3.A：加多单位支持列
    op.add_column('order_items', sa.Column('unit_code', sa.String(length=32), nullable=True))
    op.add_column(
        'order_items',
        sa.Column('base_quantity', sa.Integer(), nullable=False, server_default='0'),
    )
    # 回填老订单：历史数据里 quantity 就是 base 数量
    op.execute("UPDATE order_items SET base_quantity = quantity")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('order_items', 'base_quantity')
    op.drop_column('order_items', 'unit_code')
