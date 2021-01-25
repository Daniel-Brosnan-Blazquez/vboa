"""
Automated tests for the eboa_nav submodule

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import os
import tempfile
import pytest
from vboa import create_app
from eboa.engine.query import Query

@pytest.fixture
def app():
    app = create_app()
    query = Query()
    query.clear_db()
    yield app

@pytest.fixture
def client(app):

    return app.test_client()

