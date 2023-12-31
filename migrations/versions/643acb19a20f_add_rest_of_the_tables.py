"""add rest of the tables

Revision ID: 643acb19a20f
Revises: 4a7a714b2e4d
Create Date: 2023-07-05 14:57:11.847064

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "643acb19a20f"
down_revision = "4a7a714b2e4d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "projects",
        sa.Column("pid", sa.BIGINT(), nullable=False),
        sa.Column("created_by", sa.BIGINT(), nullable=True),
        sa.Column("name", sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.uid"],
        ),
        sa.PrimaryKeyConstraint("pid"),
    )
    with op.batch_alter_table("projects", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_projects_name"), ["name"], unique=True)

    op.create_table(
        "shared_with",
        sa.Column("uid", sa.BIGINT(), nullable=False),
        sa.Column("pid", sa.BIGINT(), nullable=False),
        sa.ForeignKeyConstraint(
            ["pid"],
            ["projects.pid"],
        ),
        sa.ForeignKeyConstraint(
            ["uid"],
            ["users.uid"],
        ),
        sa.PrimaryKeyConstraint("uid", "pid"),
    )
    op.create_table(
        "shifts",
        sa.Column("sid", sa.BIGINT(), nullable=False),
        sa.Column("pid", sa.BIGINT(), nullable=True),
        sa.Column("uid", sa.BIGINT(), nullable=True),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["pid"],
            ["projects.pid"],
        ),
        sa.ForeignKeyConstraint(
            ["uid"],
            ["users.uid"],
        ),
        sa.PrimaryKeyConstraint("sid"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("shifts")
    op.drop_table("shared_with")
    with op.batch_alter_table("projects", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_projects_name"))

    op.drop_table("projects")
    # ### end Alembic commands ###
