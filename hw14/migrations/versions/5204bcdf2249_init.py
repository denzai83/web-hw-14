"""Init

Revision ID: 5204bcdf2249
Revises: 
Create Date: 2023-04-30 20:47:45.663588

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5204bcdf2249'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('phone', sa.String(), nullable=False),
    sa.Column('date_of_birth', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_contacts_id'), table_name='contacts')
    op.drop_table('contacts')
    # ### end Alembic commands ###