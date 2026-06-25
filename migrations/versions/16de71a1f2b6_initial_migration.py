"""Initial Migration

Revision ID: 16de71a1f2b6
Revises:
Create Date: 2026-06-26 03:46:47.523911

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "16de71a1f2b6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)

    op.create_table(
        "post",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("published_status", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_post_title"), "post", ["title"], unique=False)

    op.create_table(
        "tag",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tag_name"), "tag", ["name"], unique=True)

    op.create_table(
        "comment",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["post_id"], ["post.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "posttaglink",
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["post.id"]),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"]),
        sa.PrimaryKeyConstraint("post_id", "tag_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("posttaglink")
    op.drop_table("comment")
    op.drop_index(op.f("ix_tag_name"), table_name="tag")
    op.drop_table("tag")
    op.drop_index(op.f("ix_post_title"), table_name="post")
    op.drop_table("post")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_table("user")
