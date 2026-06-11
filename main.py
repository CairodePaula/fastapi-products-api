import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, field_validator
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/produtos_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)


class ProdutoCreate(BaseModel):
    nome: str
    preco: float
    estoque: Optional[int] = 0
    ativo: Optional[bool] = True

    @field_validator("nome")
    @classmethod
    def valida_nome(cls, v):
        if not v or not v.strip():
            raise ValueError("nome nao pode ser vazio")
        return v.strip()

    @field_validator("preco")
    @classmethod
    def valida_preco(cls, v):
        if v <= 0:
            raise ValueError("preco tem que ser maior que zero")
        return v


class ProdutoOut(BaseModel):
    id: int
    nome: str
    preco: float
    estoque: int
    ativo: bool

    model_config = {"from_attributes": True}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="API de Produtos")

Base.metadata.create_all(bind=engine)


@app.get("/produtos", response_model=list[ProdutoOut], status_code=200)
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).all()


@app.post("/produtos", response_model=ProdutoOut, status_code=201)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    novo = Produto(**produto.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@app.get("/produtos/{produto_id}", response_model=ProdutoOut, status_code=200)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    prod = db.query(Produto).filter(Produto.id == produto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return prod


@app.delete("/produtos/{produto_id}", status_code=204)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    prod = db.query(Produto).filter(Produto.id == produto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(prod)
    db.commit()
