import os

# Ensure tests run with an in-memory SQLite DB when no DB is provided by CI
# This file is loaded by pytest before any package-level conftest, so it is
# a reliable place to set env vars required for app import-time initialization.
os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
os.environ.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", "false")

# Optionally set a simple Redis URL to avoid failing redis clients during import
# Tests that require a real Redis should override this in their fixtures or CI.
# Some services expect DATABASE_URL env var - set it to the same sqlite memory DB for tests
os.environ.setdefault("DATABASE_URL", os.environ.get("SQLALCHEMY_DATABASE_URI"))
