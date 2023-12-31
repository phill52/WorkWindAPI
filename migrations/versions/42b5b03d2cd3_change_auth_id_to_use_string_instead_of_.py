"""change auth id to use string instead of int

Revision ID: 42b5b03d2cd3
Revises: 643acb19a20f
Create Date: 2023-08-01 23:48:04.370598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "42b5b03d2cd3"
down_revision = "643acb19a20f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "auth_id",
            existing_type=sa.INTEGER(),
            type_=sa.String(length=255),
            existing_nullable=True,
        )
        batch_op.create_unique_constraint(None, ["auth_id"])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="unique")
        batch_op.alter_column(
            "auth_id",
            existing_type=sa.String(length=255),
            type_=sa.INTEGER(),
            existing_nullable=True,
        )

    # ### end Alembic commands ###
