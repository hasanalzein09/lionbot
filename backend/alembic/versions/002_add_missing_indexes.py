"""Add missing database indexes

Revision ID: 002_add_indexes
Revises: 001_float_to_decimal
Create Date: 2026-01-16

This migration adds missing indexes for:
- Foreign key columns (improves JOIN performance)
- Composite indexes for common query patterns
- Role and status columns for filtering
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '002_add_indexes'
down_revision = '001_float_to_decimal'
branch_labels = None
depends_on = None


def upgrade():
    """Add missing indexes for performance optimization."""

    # Menu table - restaurant_id FK
    op.create_index('ix_menu_restaurant_id', 'menu', ['restaurant_id'])

    # Category table - menu_id FK
    op.create_index('ix_category_menu_id', 'category', ['menu_id'])

    # MenuItem table - category_id FK
    op.create_index('ix_menuitem_category_id', 'menuitem', ['category_id'])

    # OrderItem table - menu_item_id FK
    op.create_index('ix_orderitem_menu_item_id', 'orderitem', ['menu_item_id'])

    # User table - additional indexes
    op.create_index('ix_user_is_active', 'user', ['is_active'])
    op.create_index('ix_user_role', 'user', ['role'])
    op.create_index('ix_user_restaurant_id', 'user', ['restaurant_id'])

    # Order table - composite indexes for common queries
    op.create_index('ix_order_restaurant_status', 'order', ['restaurant_id', 'status'])
    op.create_index('ix_order_user_created', 'order', ['user_id', 'created_at'])
    op.create_index('ix_order_driver_status', 'order', ['driver_id', 'status'])


def downgrade():
    """Remove added indexes."""

    # Order composite indexes
    op.drop_index('ix_order_driver_status', 'order')
    op.drop_index('ix_order_user_created', 'order')
    op.drop_index('ix_order_restaurant_status', 'order')

    # User indexes
    op.drop_index('ix_user_restaurant_id', 'user')
    op.drop_index('ix_user_role', 'user')
    op.drop_index('ix_user_is_active', 'user')

    # FK indexes
    op.drop_index('ix_orderitem_menu_item_id', 'orderitem')
    op.drop_index('ix_menuitem_category_id', 'menuitem')
    op.drop_index('ix_category_menu_id', 'category')
    op.drop_index('ix_menu_restaurant_id', 'menu')
