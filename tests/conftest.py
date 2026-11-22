import os
import tempfile
import pytest

@pytest.fixture
def isolated_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("DATABASE_PATH", path)
    from database import init_db
    init_db()
    yield path
    try:
        os.remove(path)
    except OSError:
        pass
