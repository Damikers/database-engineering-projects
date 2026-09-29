# Database engineering projects

KPI database coursework covering index structures, transaction concurrency, relational-data migration, layered application architecture and MongoDB.

## Projects

### B+ tree

`bplus_tree/bplus_tree.py` implements insertion, node splitting, exact/range-style search, deletion, linked leaf traversal and a small cache. Running the script builds a demonstration tree and prints search/deletion behaviour.

```bash
python bplus_tree/bplus_tree.py
```

### PostgreSQL concurrency control

`concurrency/concurrency_demo.py` compares:

- an intentionally unsafe read-modify-write sequence that demonstrates lost updates
- an atomic in-place SQL update
- row-level locking with `SELECT ... FOR UPDATE`
- optimistic concurrency using a version column

The original experiment used ten threads with 10,000 operations each.

Create the table with `concurrency/schema.sql`, configure the environment variables shown in `.env.example`, and run:

```bash
python concurrency/concurrency_demo.py
```

### PostgreSQL-to-MySQL migration

The `migration/` project contains SQLAlchemy models, repository/service/CLI layers, batch migration logic and three Alembic migrations. The original coursework migrated approximately 138,000 weather records.

The source dataset is intentionally not included. Set `CSV_PATH` to an authorised local copy or a compatible sample.

### MongoDB

The MongoDB report documents cloud CRUD operations, aggregation pipelines, `$lookup` and capped collections. No standalone source file was present in the original coursework folder.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Export the variables from `.env` using your preferred environment manager. Do not commit `.env`.

## Security

The public copies use environment variables and placeholder passwords. No original classroom credentials, database files, virtual environments or full datasets are included.

## Academic context

Individual KPI Databases coursework, 2026. The accompanying reports document design decisions, experiments and results.

