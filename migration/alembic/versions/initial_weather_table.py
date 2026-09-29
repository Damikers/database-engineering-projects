from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "weather",
        sa.Column("id",           sa.Integer(),  primary_key=True, autoincrement=True),
        sa.Column("country",      sa.String(100), nullable=False),
        sa.Column("wind_degree",  sa.Integer(),  nullable=True),
        sa.Column("wind_kph",     sa.Float(),    nullable=True),
        sa.Column("wind_dir",     sa.String(10), nullable=True),
        sa.Column("last_updated", sa.Date(),     nullable=False),
        sa.Column("sunrise",      sa.Time(),     nullable=True),
        sa.Column("air_co",           sa.Float(),   nullable=True),
        sa.Column("air_no2",          sa.Float(),   nullable=True),
        sa.Column("air_ozone",        sa.Float(),   nullable=True),
        sa.Column("air_so2",          sa.Float(),   nullable=True),
        sa.Column("air_pm25",         sa.Float(),   nullable=True),
        sa.Column("air_pm10",         sa.Float(),   nullable=True),
        sa.Column("air_epa_index",    sa.Integer(), nullable=True),
        sa.Column("air_defra_index",  sa.Integer(), nullable=True),
    )


def downgrade():
    op.drop_table("weather")