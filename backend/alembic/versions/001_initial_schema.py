"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-06-02 11:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. visitors table
    op.create_table(
        'visitors',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('track_id', sa.String(length=64), nullable=False, unique=True),
        sa.Column('first_seen', sa.DateTime(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('is_staff', sa.Boolean(), nullable=True),
        sa.Column('staff_confidence', sa.Float(), nullable=True),
        sa.Column('total_visits', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index(op.f('ix_visitors_track_id'), 'visitors', ['track_id'], unique=True)
    op.create_index(op.f('ix_visitors_first_seen'), 'visitors', ['first_seen'], unique=False)

    # 2. sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('entry_time', sa.DateTime(), nullable=False),
        sa.Column('exit_time', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('is_reentry', sa.Boolean(), nullable=True),
        sa.Column('zones_visited', sa.JSON(), nullable=True),
        sa.Column('max_dwell_zone', sa.String(length=128), nullable=True),
        sa.Column('max_dwell_seconds', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_sessions_visitor_id'), 'sessions', ['visitor_id'], unique=False)
    op.create_index(op.f('ix_sessions_entry_time'), 'sessions', ['entry_time'], unique=False)

    # 3. events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('visitor_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=32), nullable=False),
        sa.Column('zone_name', sa.String(length=128), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('bbox_x', sa.Float(), nullable=True),
        sa.Column('bbox_y', sa.Float(), nullable=True),
        sa.Column('bbox_w', sa.Float(), nullable=True),
        sa.Column('bbox_h', sa.Float(), nullable=True),
        sa.Column('frame_number', sa.Integer(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    op.create_index(op.f('ix_events_zone_name'), 'events', ['zone_name'], unique=False)
    op.create_index(op.f('ix_events_timestamp'), 'events', ['timestamp'], unique=False)

    # 4. transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('order_id', sa.String(length=64), nullable=False),
        sa.Column('invoice_number', sa.String(length=64), nullable=True),
        sa.Column('order_date', sa.Date(), nullable=False),
        sa.Column('order_time', sa.Time(), nullable=False),
        sa.Column('store_id', sa.String(length=32), nullable=True),
        sa.Column('store_name', sa.String(length=128), nullable=True),
        sa.Column('city', sa.String(length=64), nullable=True),
        sa.Column('customer_name', sa.String(length=256), nullable=True),
        sa.Column('customer_number', sa.String(length=32), nullable=True),
        sa.Column('sku', sa.String(length=64), nullable=True),
        sa.Column('product_name', sa.String(length=512), nullable=True),
        sa.Column('brand_name', sa.String(length=128), nullable=True),
        sa.Column('department', sa.String(length=64), nullable=True),
        sa.Column('sub_category', sa.String(length=128), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('gmv', sa.Float(), nullable=True),
        sa.Column('nmv', sa.Float(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=True),
        sa.Column('salesperson_name', sa.String(length=128), nullable=True),
        sa.Column('employee_code', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index(op.f('ix_transactions_order_id'), 'transactions', ['order_id'], unique=False)
    op.create_index(op.f('ix_transactions_order_date'), 'transactions', ['order_date'], unique=False)

    # 5. anomalies table
    op.create_table(
        'anomalies',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('anomaly_type', sa.String(length=64), nullable=False),
        sa.Column('severity', sa.String(length=16), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('suggested_action', sa.Text(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=True),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('zone_name', sa.String(length=128), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index(op.f('ix_anomalies_anomaly_type'), 'anomalies', ['anomaly_type'], unique=False)
    op.create_index(op.f('ix_anomalies_detected_at'), 'anomalies', ['detected_at'], unique=False)

    # 6. metrics_cache table
    op.create_table(
        'metrics_cache',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('metric_name', sa.String(length=128), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('metric_data', sa.JSON(), nullable=True),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('computed_at', sa.DateTime(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.UniqueConstraint('metric_name', 'period_start', name='uix_metric_name_period_start'),
    )
    op.create_index(op.f('ix_metrics_cache_metric_name'), 'metrics_cache', ['metric_name'], unique=False)
    op.create_index(op.f('ix_metrics_cache_period_start'), 'metrics_cache', ['period_start'], unique=False)


def downgrade() -> None:
    op.drop_table('metrics_cache')
    op.drop_table('anomalies')
    op.drop_table('transactions')
    op.drop_table('events')
    op.drop_table('sessions')
    op.drop_table('visitors')
