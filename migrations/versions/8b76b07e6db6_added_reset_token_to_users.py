"""added reset token to users

Revision ID: 8b76b07e6db6
Revises: fe53fcd69d60
Create Date: 2024-04-08 19:21:49.665263

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8b76b07e6db6'
down_revision: Union[str, None] = 'fe53fcd69d60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'reset_token')
    # ### end Alembic commands ###
