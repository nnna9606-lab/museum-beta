"""Ավելացնել ArtifactImage աղյուսակ նմուշային նկարների համար

Revision ID: 003
Revises: 
Create Date: 2026-02-18 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = '003'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ստեղծել ArtifactImage աղյուսակ
    op.create_table(
        'artifact_image',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('artifact_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=200), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['artifact_id'], ['artifact.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Ջնջել ArtifactImage աղյուսակ
    op.drop_table('artifact_image')
