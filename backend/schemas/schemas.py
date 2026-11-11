from pydantic import BaseModel
from typing import Optional

class ProdutoSchema(BaseModel):
    codigo: int
    quantidade: int
    qnt_minima: int
    preco_compra: float
    nome: str
    categoria: str
    fornecedor: str
    data_vencimento: Optional[str] = None

class VendaSchema(BaseModel):
    codigo_produto: int
    quantidade: int
    metodo_pagamento: str