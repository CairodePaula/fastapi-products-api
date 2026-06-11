# API de Gerenciamento de Produtos

API REST construída com **FastAPI + SQLAlchemy + PostgreSQL**, com testes automatizados via **Pytest** e banco de testes isolado em container **Docker**.

---

## Requisitos

- Docker e Docker Compose instalados
- Python 3.12+

---

## Como subir os bancos de dados

```bash
docker-compose up -d
```

Isso sobe dois containers PostgreSQL:
- `db` na porta **5432** — banco de desenvolvimento
- `db_test` na porta **5433** — banco exclusivo para testes (sem volume persistente)

Para verificar se ambos estão saudáveis:

```bash
docker-compose ps
```

Aguarde o status `healthy` em ambos antes de prosseguir.

---

## Como executar os testes

Com o container `db_test` rodando:

```bash
pytest --cov=main -v
```

Para rodar com relatório de cobertura detalhado:

```bash
pytest --cov=main --cov-report=term-missing -v
```

---

## Saída esperada do pytest

```
collected 14 items

tests/test_produtos.py::test_listar_produtos_banco_vazio PASSED
tests/test_produtos.py::test_criar_produto_persiste_no_banco PASSED
tests/test_produtos.py::test_criar_produto_aparece_na_listagem PASSED
tests/test_produtos.py::test_buscar_produto_por_id_sucesso PASSED
tests/test_produtos.py::test_buscar_produto_id_inexistente_retorna_404 PASSED
tests/test_produtos.py::test_deletar_produto_retorna_204 PASSED
tests/test_produtos.py::test_deletar_produto_confirmar_remocao PASSED
tests/test_produtos.py::test_deletar_produto_inexistente_retorna_404 PASSED
tests/test_produtos.py::test_criar_produto_payload_invalido_retorna_422[payload0] PASSED
tests/test_produtos.py::test_criar_produto_payload_invalido_retorna_422[payload1] PASSED
tests/test_produtos.py::test_criar_produto_payload_invalido_retorna_422[payload2] PASSED
tests/test_produtos.py::test_criar_produto_payload_invalido_retorna_422[payload3] PASSED
tests/test_produtos.py::test_criar_produto_payload_invalido_retorna_422[payload4] PASSED
tests/test_produtos.py::test_banco_isolado_entre_testes_parte1 PASSED
tests/test_produtos.py::test_banco_isolado_entre_testes_parte2 PASSED
tests/test_produtos.py::test_listar_multiplos_produtos PASSED
tests/test_produtos.py::test_valores_padrao_estoque_e_ativo PASSED

---------- coverage: platform linux, python 3.12 ----------
Name      Stmts   Miss  Branch  BrPartial  Cover
-------------------------------------------------
main.py      48      0       8          0   100%

17 passed in 3.21s
```

---

## Como o isolamento entre testes funciona

Cada teste recebe uma instância limpa do banco. O mecanismo funciona assim:

1. A fixture `client` (em `conftest.py`) é do escopo `function` — ou seja, executa **antes e depois de cada teste individualmente**.
2. No **setup**, ela chama `Base.metadata.create_all(bind=test_engine)`, criando as tabelas do zero no banco de testes.
3. Usa `app.dependency_overrides[get_db]` para substituir a sessão do banco de produção pela sessão do banco de testes — sem alterar nenhuma linha do `main.py`.
4. Faz `yield` do `TestClient`, entregando o cliente ao teste.
5. No **teardown** (após o yield), chama `Base.metadata.drop_all(bind=test_engine)`, destruindo todas as tabelas e garantindo que nenhum dado do teste anterior vaze para o próximo.

Isso significa que a ordem de execução dos testes **não importa** — cada um começa com um banco completamente vazio.

---

## Endpoints disponíveis

| Método | Rota | Status | Descrição |
|--------|------|--------|-----------|
| GET | `/produtos` | 200 | Lista todos os produtos |
| POST | `/produtos` | 201 | Cria um novo produto |
| GET | `/produtos/{id}` | 200 / 404 | Busca produto por ID |
| DELETE | `/produtos/{id}` | 204 / 404 | Remove produto por ID |

Documentação interativa disponível em `http://localhost:8000/docs` com a API rodando.

---

## Verificação final antes de entregar

```bash
docker-compose up -d db_test && pytest --cov=main -v
```
