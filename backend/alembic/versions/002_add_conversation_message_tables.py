"""Add Conversation and Message tables for Phase 3.

Revision ID: 002
Revises: 001
Create Date: 2026-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversation table
    op.create_table(
        'conversation',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_conversation_user_id'), 'conversation', ['user_id'], unique=False)
    # Composite index for recent conversations query
    op.create_index(
        'ix_conversation_user_updated',
        'conversation',
        ['user_id', sa.text('updated_at DESC')],
        unique=False
    )

    # Create message table
    op.create_table(
        'message',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('conversation_id', sa.Uuid(), nullable=False),
        sa.Column(
            'role',
            sa.Enum('user', 'assistant', name='messagerole'),
            nullable=False
        ),
        sa.Column('content', sqlmodel.sql.sqltypes.AutoString(length=10000), nullable=False),
        sa.Column('tool_calls', sqlmodel.sql.sqltypes.AutoString(length=5000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("LENGTH(content) > 0", name='ck_message_content_not_empty'),
    )
    op.create_index(op.f('ix_message_user_id'), 'message', ['user_id'], unique=False)
    op.create_index(op.f('ix_message_conversation_id'), 'message', ['conversation_id'], unique=False)
    # Composite index for message history query (chronological order)
    op.create_index(
        'ix_message_conversation_created',
        'message',
        ['conversation_id', 'created_at'],
        unique=False
    )


def downgrade() -> None:
    # Drop message table first (foreign key dependency)
    op.drop_index('ix_message_conversation_created', table_name='message')
    op.drop_index(op.f('ix_message_conversation_id'), table_name='message')
    op.drop_index(op.f('ix_message_user_id'), table_name='message')
    op.drop_table('message')

    # Drop messagerole enum type
    op.execute('DROP TYPE IF EXISTS messagerole')

    # Drop conversation table
    op.drop_index('ix_conversation_user_updated', table_name='conversation')
    op.drop_index(op.f('ix_conversation_user_id'), table_name='conversation')
    op.drop_table('conversation')
