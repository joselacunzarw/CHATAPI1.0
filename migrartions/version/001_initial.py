"""
Migración inicial para la base de datos
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Crear tabla de usuarios
    op.create_table(
        'users',
        sa.Column('email', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('google_id', sa.String(), unique=True),
        sa.Column('picture_url', sa.String(), nullable=True),
        sa.Column('given_name', sa.String()),
        sa.Column('family_name', sa.String()),
        sa.Column('locale', sa.String()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True)
    )
    
    # Índices
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_google_id', 'users', ['google_id'])

def downgrade():
    op.drop_index('ix_users_google_id')
    op.drop_index('ix_users_email')
    op.drop_table('users')