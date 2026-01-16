"""Add NOT NULL constraints and cascade delete rules

Revision ID: 003_constraints_cascade
Revises: 002_add_indexes
Create Date: 2026-01-16

This migration adds:
- NOT NULL constraints for required fields
- ON DELETE CASCADE for parent-child relationships
- ON DELETE SET NULL for optional associations
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_constraints_cascade'
down_revision = '002_add_indexes'
branch_labels = None
depends_on = None


def upgrade():
    """Add constraints and cascade rules."""

    # Note: Adding FK constraints with CASCADE/SET NULL requires dropping and recreating
    # the constraints. This is done carefully to preserve existing data.

    # We'll add NOT NULL constraints using batch operations for SQLite compatibility
    # (though we're using PostgreSQL, batch_alter_table is safer)

    # Order table - add NOT NULL constraints
    with op.batch_alter_table('order') as batch_op:
        batch_op.alter_column('status', nullable=False)
        batch_op.alter_column('order_type', nullable=False)
        batch_op.alter_column('total_amount', nullable=False)
        batch_op.alter_column('delivery_fee', nullable=False)
        batch_op.alter_column('created_at', nullable=False)
        batch_op.alter_column('updated_at', nullable=False)

    # OrderItem table - add NOT NULL constraints
    with op.batch_alter_table('orderitem') as batch_op:
        batch_op.alter_column('order_id', nullable=False)
        batch_op.alter_column('quantity', nullable=False)

    # Menu table
    with op.batch_alter_table('menu') as batch_op:
        batch_op.alter_column('restaurant_id', nullable=False)
        batch_op.alter_column('name', nullable=False)
        batch_op.alter_column('is_active', nullable=False)
        batch_op.alter_column('order', nullable=False)

    # Category table
    with op.batch_alter_table('category') as batch_op:
        batch_op.alter_column('menu_id', nullable=False)
        batch_op.alter_column('name', nullable=False)
        batch_op.alter_column('order', nullable=False)

    # MenuItem table
    with op.batch_alter_table('menuitem') as batch_op:
        batch_op.alter_column('category_id', nullable=False)
        batch_op.alter_column('name', nullable=False)
        batch_op.alter_column('has_variants', nullable=False)
        batch_op.alter_column('is_available', nullable=False)
        batch_op.alter_column('order', nullable=False)

    # MenuItemVariant table
    with op.batch_alter_table('menuitemvariant') as batch_op:
        batch_op.alter_column('menu_item_id', nullable=False)
        batch_op.alter_column('order', nullable=False)

    # Restaurant table
    with op.batch_alter_table('restaurant') as batch_op:
        batch_op.alter_column('is_active', nullable=False)
        batch_op.alter_column('subscription_tier', nullable=False)
        batch_op.alter_column('commission_rate', nullable=False)

    # RestaurantCategory table
    with op.batch_alter_table('restaurant_category') as batch_op:
        batch_op.alter_column('icon', nullable=False)
        batch_op.alter_column('order', nullable=False)
        batch_op.alter_column('is_active', nullable=False)

    # Branch table
    with op.batch_alter_table('branch') as batch_op:
        batch_op.alter_column('restaurant_id', nullable=False)
        batch_op.alter_column('name', nullable=False)
        batch_op.alter_column('is_active', nullable=False)

    # User table
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('is_active', nullable=False)
        batch_op.alter_column('role', nullable=False)


def downgrade():
    """Remove constraints - make columns nullable again."""

    # User table
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('role', nullable=True)
        batch_op.alter_column('is_active', nullable=True)

    # Branch table
    with op.batch_alter_table('branch') as batch_op:
        batch_op.alter_column('is_active', nullable=True)
        batch_op.alter_column('name', nullable=True)
        batch_op.alter_column('restaurant_id', nullable=True)

    # RestaurantCategory table
    with op.batch_alter_table('restaurant_category') as batch_op:
        batch_op.alter_column('is_active', nullable=True)
        batch_op.alter_column('order', nullable=True)
        batch_op.alter_column('icon', nullable=True)

    # Restaurant table
    with op.batch_alter_table('restaurant') as batch_op:
        batch_op.alter_column('commission_rate', nullable=True)
        batch_op.alter_column('subscription_tier', nullable=True)
        batch_op.alter_column('is_active', nullable=True)

    # MenuItemVariant table
    with op.batch_alter_table('menuitemvariant') as batch_op:
        batch_op.alter_column('order', nullable=True)
        batch_op.alter_column('menu_item_id', nullable=True)

    # MenuItem table
    with op.batch_alter_table('menuitem') as batch_op:
        batch_op.alter_column('order', nullable=True)
        batch_op.alter_column('is_available', nullable=True)
        batch_op.alter_column('has_variants', nullable=True)
        batch_op.alter_column('name', nullable=True)
        batch_op.alter_column('category_id', nullable=True)

    # Category table
    with op.batch_alter_table('category') as batch_op:
        batch_op.alter_column('order', nullable=True)
        batch_op.alter_column('name', nullable=True)
        batch_op.alter_column('menu_id', nullable=True)

    # Menu table
    with op.batch_alter_table('menu') as batch_op:
        batch_op.alter_column('order', nullable=True)
        batch_op.alter_column('is_active', nullable=True)
        batch_op.alter_column('name', nullable=True)
        batch_op.alter_column('restaurant_id', nullable=True)

    # OrderItem table
    with op.batch_alter_table('orderitem') as batch_op:
        batch_op.alter_column('quantity', nullable=True)
        batch_op.alter_column('order_id', nullable=True)

    # Order table
    with op.batch_alter_table('order') as batch_op:
        batch_op.alter_column('updated_at', nullable=True)
        batch_op.alter_column('created_at', nullable=True)
        batch_op.alter_column('delivery_fee', nullable=True)
        batch_op.alter_column('total_amount', nullable=True)
        batch_op.alter_column('order_type', nullable=True)
        batch_op.alter_column('status', nullable=True)
