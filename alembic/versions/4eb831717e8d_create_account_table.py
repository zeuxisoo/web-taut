"""create account table

Revision ID: 4eb831717e8d
Revises: 32a9518ad88e
Create Date: 2014-12-12 00:15:25.359628

"""

# revision identifiers, used by Alembic.
revision = '4eb831717e8d'
down_revision = '32a9518ad88e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('role', sa.String(length=10), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('update_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_account_email'), 'account', ['email'], unique=True)
    op.create_index(op.f('ix_account_username'), 'account', ['username'], unique=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_account_username'), table_name='account')
    op.drop_index(op.f('ix_account_email'), table_name='account')
    op.drop_table('account')
    ### end Alembic commands ###
