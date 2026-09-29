from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("air_quality") as batch_op:
        batch_op.add_column(
            sa.Column("go_outside", sa.Boolean(), nullable=True)
        )

    #   EPA Index <= 3  — рівень "добре" або "помірно"
    #   PM2.5 < 35      — безпечний рівень дрібних частинок
    #   Ozone < 180     — безпечний рівень озону (мкг/м3)
    op.execute("""
        UPDATE air_quality
        SET go_outside = (
            COALESCE(air_epa_index, 99) <= 3
            AND COALESCE(air_pm25, 999) < 35
            AND COALESCE(air_ozone, 999) < 180
        )
    """)


def downgrade():
    with op.batch_alter_table("air_quality") as batch_op:
        batch_op.drop_column("go_outside")