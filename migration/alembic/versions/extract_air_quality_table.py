from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "air_quality",
        sa.Column("id",              sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("weather_id",      sa.Integer(), sa.ForeignKey("weather.id"), nullable=False),
        sa.Column("air_co",          sa.Float(),   nullable=True),
        sa.Column("air_no2",         sa.Float(),   nullable=True),
        sa.Column("air_ozone",       sa.Float(),   nullable=True),
        sa.Column("air_so2",         sa.Float(),   nullable=True),
        sa.Column("air_pm25",        sa.Float(),   nullable=True),
        sa.Column("air_pm10",        sa.Float(),   nullable=True),
        sa.Column("air_epa_index",   sa.Integer(), nullable=True),
        sa.Column("air_defra_index", sa.Integer(), nullable=True),
    )

    op.execute("""
        INSERT INTO air_quality (
            weather_id, air_co, air_no2, air_ozone, air_so2,
            air_pm25, air_pm10, air_epa_index, air_defra_index
        )
        SELECT
            id, air_co, air_no2, air_ozone, air_so2,
            air_pm25, air_pm10, air_epa_index, air_defra_index
        FROM weather
    """)

    with op.batch_alter_table("weather") as batch_op:
        batch_op.drop_column("air_co")
        batch_op.drop_column("air_no2")
        batch_op.drop_column("air_ozone")
        batch_op.drop_column("air_so2")
        batch_op.drop_column("air_pm25")
        batch_op.drop_column("air_pm10")
        batch_op.drop_column("air_epa_index")
        batch_op.drop_column("air_defra_index")


def downgrade():
    with op.batch_alter_table("weather") as batch_op:
        batch_op.add_column(sa.Column("air_co",          sa.Float()))
        batch_op.add_column(sa.Column("air_no2",         sa.Float()))
        batch_op.add_column(sa.Column("air_ozone",       sa.Float()))
        batch_op.add_column(sa.Column("air_so2",         sa.Float()))
        batch_op.add_column(sa.Column("air_pm25",        sa.Float()))
        batch_op.add_column(sa.Column("air_pm10",        sa.Float()))
        batch_op.add_column(sa.Column("air_epa_index",   sa.Integer()))
        batch_op.add_column(sa.Column("air_defra_index", sa.Integer()))

    op.execute("""
        UPDATE weather w
        SET
            air_co          = aq.air_co,
            air_no2         = aq.air_no2,
            air_ozone       = aq.air_ozone,
            air_so2         = aq.air_so2,
            air_pm25        = aq.air_pm25,
            air_pm10        = aq.air_pm10,
            air_epa_index   = aq.air_epa_index,
            air_defra_index = aq.air_defra_index
        FROM air_quality aq
        WHERE aq.weather_id = w.id
    """)

    op.drop_table("air_quality")