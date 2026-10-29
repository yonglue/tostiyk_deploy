"""stub placeholder for missing revision 2a213f4f4a7e

该迁移文件在仓库中丢失（git 历史也无记录），但当前生产 DB 与后续迁移
（4f7b4846ede7）均已完成。此 stub 仅用于恢复 alembic 链条完整性，
保证 alembic upgrade head 不再因 missing revision 中断。

Revision ID: 2a213f4f4a7e
Revises: 6e5a743c6889
Create Date: 2026-10-28
"""
from typing import Sequence, Union

revision: str = '2a213f4f4a7e'
down_revision: Union[str, Sequence[str], None] = '6e5a743c6889'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 原迁移内容已丢失；当前 DB 已越过此版本，无需执行任何操作。
    pass


def downgrade() -> None:
    pass