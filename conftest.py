import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, Base, get_db

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/produtos_test"
)

engine_teste = create_engine(TEST_DATABASE_URL)
SessaoTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine_teste)

    def db_teste():
        db = SessaoTeste()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = db_teste

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_teste)


@pytest.fixture(scope="function")
def prod_salvo(client):
    dados = {"nome": "Produto Teste", "preco": 49.90, "estoque": 10, "ativo": True}
    res = client.post("/produtos", json=dados)
    assert res.status_code == 201
    return res.json()
