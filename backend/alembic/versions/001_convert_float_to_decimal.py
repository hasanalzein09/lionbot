"""Convert Float to DECIMAL for financial fields

Revision ID: 001_float_to_decimal
Revises:
Create Date: 2026-01-16

This migration converts all financial fields from Float to DECIMAL(10,2)
for proper monetary precision. Float types can cause rounding errors
in financial calculations.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_float_to_decimal'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Convert Float columns to DECIMAL(10,2) for financial precision."""

    # Order table
    with op.batch_alter_table('order') as batch_op:
        batch_op.alter_column('total_amount',
                              existing_type=sa.Float(),
                              type_=sa.Numeric(10, 2),
                              existing_nullable=True)
        batch_op.alter_column('delivery_fee',
                              existing_type=sa.Float(),
                              type_=sa.Numeric(10, 2),
                              existing_nullable=True)

    # OrderItem table
    with op.batch_alter_table('orderitem') as batch_op:
        batch_op.alter_column('unit_price',
                              existing_type=sa.Float(),
                              type_=sa.Numeric(10, 2),
                              existing_nullable=False)
        batch_op.alter_column('total_price',
                              existing_type=sa.Float(),
                              type_=sa.Numeric(10, 2),
                              existing_nullable=False)

    # MenuItem table
    with op.batch_alter_table('menuitem') as batch_op:
        batch_op.alter_column('price',
                              existing_type=sa.Float(),
                              type_=sa.Numeric(10, 2),
                              existing_nullable=True)
        batch_op.alter_column('price_min',
                              existing_type=sa.Float(),
                              type_=sa.Numeric(10, 2),
                              existing_nullable=True)
        batch_op.alter_column('price_max',
                              existing_type=sa.Float(),
                              type_=sa.Numeric(10, 2),
                              existing_nullable=True)

    # MenuItemVariant table
    with op.batch_alter_table('menuitemvariant') as batch_op:
        batch_op.alter_column('price',
                              existing_type=sa.Float(),
                              type_=sa.Numeric(10, 2),
                              existing_nullable=False)

    # Restaurant table - commission_rate
    with op.batch_alter_table('restaurant') as batch_op:
        batch_op.alter_column('commission_rate',
                              existing_type=sa.Float(),
                              type_=sa.Numeric(5, 2),
                              existing_nullable=True)


def downgrade():
    """Revert DECIMAL columns back to Float."""

    # Order table
    with op.batch_alter_table('order') as batch_op:
        batch_op.alter_column('total_amount',
                              existing_type=sa.Numeric(10, 2),
                              type_=sa.Float(),
                              existing_nullable=True)
        batch_op.alter_column('delivery_fee',
                              existing_type=sa.Numeric(10, 2),
                              type_=sa.Float(),
                              existing_nullable=True)

    # OrderItem table
    with op.batch_alter_table('orderitem') as batch_op:
        batch_op.alter_column('unit_price',
                              existing_type=sa.Numeric(10, 2),
                              type_=sa.Float(),
                              existing_nullable=False)
        batch_op.alter_column('total_price',
                              existing_type=sa.Numeric(10, 2),
                              type_=sa.Float(),
                              existing_nullable=False)

    # MenuItem table
    with op.batch_alter_table('menuitem') as batch_op:
        batch_op.alter_column('price',
                              existing_type=sa.Numeric(10, 2),
                              type_=sa.Float(),
                              existing_nullable=True)
        batch_op.alter_column('price_min',
                              existing_type=sa.Numeric(10, 2),
                              type_=sa.Float(),
                              existing_nullable=True)
        batch_op.alter_column('price_max',
                              existing_type=sa.Numeric(10, 2),
                              type_=sa.Float(),
                              existing_nullable=True)

    # MenuItemVariant table
    with op.batch_alter_table('menuitemvariant') as batch_op:
        batch_op.alter_column('price',
                              existing_type=sa.Numeric(10, 2),
                              type_=sa.Float(),
                              existing_nullable=False)

    # Restaurant table
    with op.batch_alter_table('restaurant') as batch_op:
        batch_op.alter_column('commission_rate',
                              existing_type=sa.Numeric(5, 2),
                              type_=sa.Float(),
                              existing_nullable=True)
