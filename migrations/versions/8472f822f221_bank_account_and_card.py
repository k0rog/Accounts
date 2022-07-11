"""bank account and card

Revision ID: 8472f822f221
Revises: 9b2932e41253
Create Date: 2022-07-11 14:44:54.372845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8472f822f221'
down_revision = '9b2932e41253'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bank_account',
    sa.Column('IBAN', sa.String(length=18), nullable=False),
    sa.Column('currency', sa.Enum('BYN', 'USD', 'EUR', name='currencyenum'), nullable=False),
    sa.Column('balance', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('IBAN')
    )
    op.create_table('bank_card',
    sa.Column('card_number', sa.String(length=16), nullable=False),
    sa.Column('expiration_date', sa.Date(), nullable=False),
    sa.Column('CVV', sa.Integer(), nullable=False),
    sa.Column('_pin_hash', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('card_number')
    )
    op.create_table('bank_accounts',
    sa.Column('customer_id', sa.String(length=9), nullable=False),
    sa.Column('bank_account_id', sa.String(length=18), nullable=False),
    sa.ForeignKeyConstraint(['bank_account_id'], ['bank_account.IBAN'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.passport_number'], ),
    sa.PrimaryKeyConstraint('customer_id', 'bank_account_id')
    )
    op.alter_column('customer', 'first_name',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    op.alter_column('customer', 'last_name',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    op.alter_column('customer', 'email',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('customer', 'email',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    op.alter_column('customer', 'last_name',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    op.alter_column('customer', 'first_name',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    op.drop_table('bank_accounts')
    op.drop_table('bank_card')
    op.drop_table('bank_account')
    # ### end Alembic commands ###