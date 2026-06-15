"""initial schema: users, profils, share_tokens

Revision ID: 3a6b8675a66a
Revises: 
Create Date: 2026-06-15 16:39:25.593904
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '3a6b8675a66a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('nom', sa.String(100), nullable=False),
        sa.Column('date_naissance', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        'profils',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('prenom', sa.String(100), nullable=False),
        sa.Column('nom_famille', sa.String(100), nullable=False),
        sa.Column('date_naissance', sa.Date(), nullable=False),
        sa.Column('heure_naissance', sa.Time(), nullable=True),
        sa.Column('lieu_naissance', sa.String(200), nullable=True),
        sa.Column('numerologie', sa.JSON(), nullable=False),
        sa.Column('profil_cognitif', sa.JSON(), nullable=False),
        sa.Column('human_design', sa.JSON(), nullable=False),
        sa.Column('synthese_ia', sa.Text(), nullable=True),
        sa.Column('statut', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        'share_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('profil_id', sa.Integer(), sa.ForeignKey('profils.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(64), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('share_tokens')
    op.drop_table('profils')
    op.drop_table('users')
