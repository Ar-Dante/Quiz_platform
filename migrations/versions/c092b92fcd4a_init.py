"""Init

Revision ID: c092b92fcd4a
Revises: 
Create Date: 2023-10-03 10:02:56.447263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c092b92fcd4a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_email', sa.String(), nullable=False),
    sa.Column('user_firstname', sa.String(), nullable=True),
    sa.Column('user_lastname', sa.String(), nullable=True),
    sa.Column('user_status', sa.String(), nullable=False),
    sa.Column('user_city', sa.String(), nullable=True),
    sa.Column('user_phone', sa.String(), nullable=True),
    sa.Column('user_links', sa.String(), nullable=True),
    sa.Column('user_avatar', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_user_email'), 'users', ['user_email'], unique=True)
    op.create_table('companies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_name', sa.String(), nullable=True),
    sa.Column('company_title', sa.String(), nullable=True),
    sa.Column('company_description', sa.String(), nullable=True),
    sa.Column('company_city', sa.String(), nullable=True),
    sa.Column('company_phone', sa.String(), nullable=True),
    sa.Column('company_links', sa.String(), nullable=True),
    sa.Column('company_avatar', sa.String(), nullable=True),
    sa.Column('is_visible', sa.Boolean(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_id'), 'companies', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_companies_id'), table_name='companies')
    op.drop_table('companies')
    op.drop_index(op.f('ix_users_user_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###