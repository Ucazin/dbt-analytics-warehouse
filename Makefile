# Convenience targets for the dbt analytics_warehouse project.
# Requires:  pip install dbt-duckdb matplotlib networkx pandas numpy
# Usage:     make <target>

DBT_PROFILES_DIR := $(CURDIR)
export DBT_PROFILES_DIR

PY ?= py -3.12

.PHONY: help setup seed deps build test docs dag clean all

help:
	@echo "Targets:"
	@echo "  make setup    Create .venv and install dbt-duckdb"
	@echo "  make seed     Re-generate raw.* tables in warehouse.duckdb"
	@echo "  make deps     dbt deps"
	@echo "  make build    dbt build (seeds, models, snapshots, tests)"
	@echo "  make test     dbt test only"
	@echo "  make docs     dbt docs generate (writes target/manifest.json)"
	@echo "  make dag      Render outputs/dag.png from manifest.json"
	@echo "  make all      seed + deps + build + docs + dag"
	@echo "  make clean    Remove target/, dbt_packages/, warehouse.duckdb*"

setup:
	$(PY) -m venv .venv
	./.venv/Scripts/python.exe -m pip install --upgrade pip
	./.venv/Scripts/python.exe -m pip install "dbt-duckdb>=1.7,<1.10" pandas numpy matplotlib networkx

seed:
	./.venv/Scripts/python.exe scripts/seed_sources.py

deps:
	./.venv/Scripts/dbt.exe deps

build:
	./.venv/Scripts/dbt.exe build

test:
	./.venv/Scripts/dbt.exe test

docs:
	./.venv/Scripts/dbt.exe docs generate

dag: docs
	./.venv/Scripts/python.exe scripts/render_dag.py

all: seed deps build docs dag

clean:
	rm -rf target dbt_packages
	rm -f warehouse.duckdb warehouse.duckdb.wal
