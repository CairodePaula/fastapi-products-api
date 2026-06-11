import pytest


def test_lista_vazia(client):
    res = client.get("/produtos")
    assert res.status_code == 200
    assert res.json() == []


def test_criar_produto(client):
    dados = {"nome": "Notebook", "preco": 3500.00, "estoque": 5}
    res = client.post("/produtos", json=dados)
    assert res.status_code == 201
    corpo = res.json()
    assert corpo["id"] is not None
    assert corpo["nome"] == "Notebook"
    assert corpo["preco"] == 3500.00
    assert corpo["estoque"] == 5
    assert corpo["ativo"] is True


def test_produto_criado_aparece_na_lista(client):
    client.post("/produtos", json={"nome": "Teclado Mecânico", "preco": 450.00, "estoque": 20})
    res = client.get("/produtos")
    assert res.status_code == 200
    nomes = [p["nome"] for p in res.json()]
    assert "Teclado Mecânico" in nomes


def test_buscar_por_id(client, prod_salvo):
    pid = prod_salvo["id"]
    res = client.get(f"/produtos/{pid}")
    assert res.status_code == 200
    assert res.json()["id"] == pid
    assert res.json()["nome"] == prod_salvo["nome"]


def test_buscar_id_nao_existe(client):
    res = client.get("/produtos/99999")
    assert res.status_code == 404


def test_deletar_produto(client, prod_salvo):
    pid = prod_salvo["id"]
    res = client.delete(f"/produtos/{pid}")
    assert res.status_code == 204


def test_deletar_e_confirmar_remocao(client, prod_salvo):
    pid = prod_salvo["id"]
    client.delete(f"/produtos/{pid}")
    res = client.get(f"/produtos/{pid}")
    assert res.status_code == 404


def test_deletar_id_nao_existe(client):
    res = client.delete("/produtos/99999")
    assert res.status_code == 404


@pytest.mark.parametrize("dados", [
    {"nome": "", "preco": 10.0},
    {"nome": "Produto", "preco": 0},
    {"nome": "Produto", "preco": -5.0},
    {"nome": "Produto"},
    {"preco": 10.0},
])
def test_payload_invalido(client, dados):
    res = client.post("/produtos", json=dados)
    assert res.status_code == 422


def test_isolamento_cria_produto(client):
    res = client.post("/produtos", json={"nome": "Produto temporario", "preco": 1.0})
    assert res.status_code == 201


def test_isolamento_banco_limpo(client):
    res = client.get("/produtos")
    assert res.status_code == 200
    assert res.json() == []


def test_listar_varios_produtos(client):
    for nome in ["Mouse", "Monitor", "Headset"]:
        client.post("/produtos", json={"nome": nome, "preco": 100.0})
    res = client.get("/produtos")
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_valores_padrao(client):
    res = client.post("/produtos", json={"nome": "Produto Simples", "preco": 25.00})
    assert res.status_code == 201
    corpo = res.json()
    assert corpo["estoque"] == 0
    assert corpo["ativo"] is True
