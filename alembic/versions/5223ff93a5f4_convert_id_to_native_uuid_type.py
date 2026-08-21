"""convert id to native uuid type

Revision ID: 5223ff93a5f4
Revises: d54aff3c12e8
Create Date: 2026-08-21 12:23:27.504094

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5223ff93a5f4"
down_revision: Union[str, Sequence[str], None] = "d54aff3c12e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("notes_user_id_fkey", "notes", type_="foreignkey")

    op.alter_column(
        "users",
        "id",
        existing_type=sa.VARCHAR(length=36),
        type_=sa.Uuid(),
        existing_nullable=False,
        postgresql_using="id::uuid",
    )
    op.alter_column(
        "notes",
        "user_id",
        existing_type=sa.VARCHAR(length=36),
        type_=sa.Uuid(),
        existing_nullable=False,
        postgresql_using="user_id::uuid",
    )
    op.alter_column(
        "notes",
        "id",
        existing_type=sa.VARCHAR(length=36),
        type_=sa.Uuid(),
        existing_nullable=False,
        postgresql_using="id::uuid",
    )

    op.create_foreign_key(
        "notes_users_id_key", "notes", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("notes_users_id_key", "notes", type_="foreignkey")

    op.alter_column(
        "notes",
        "id",
        existing_type=sa.Uuid(),
        type_=sa.VARCHAR(length=36),
        existing_nullable=False,
        postgresql_using="id::text",
    )
    op.alter_column(
        "notes",
        "user_id",
        existing_type=sa.Uuid(),
        type_=sa.VARCHAR(length=36),
        existing_nullable=False,
        postgresql_using="user_id::text",
    )
    op.alter_column(
        "users",
        "id",
        existing_type=sa.Uuid(),
        type_=sa.VARCHAR(length=36),
        existing_nullable=False,
        postgresql_using="id::text",
    )

    op.create_foreign_key(
        "notes_user_id_fkey", "notes", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###
