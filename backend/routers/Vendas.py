from fastapi import APIRouter, HTTPException
from backend.database import conectar
from backend.schemas.schemas import VendaSchema

router = APIRouter(prefix="/api/vendas", tags=["Vendas"])

@router.post("")
def registrar_venda(venda: VendaSchema):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT quantidade, preco_compra FROM produtos WHERE codigo = %s",
            (venda.codigo_produto,)
        )
        produto = cursor.fetchone()

        if not produto:
            raise HTTPException(status_code=404, detail="Produto não encontrado!")
        
        if produto['quantidade'] < venda.quantidade:
            raise HTTPException(
                status_code=400, 
                detail=f"Estoque insuficiente! Disponível: {produto['quantidade']}"
            )

        nova_qtd = produto['quantidade'] - venda.quantidade
        cursor.execute(
            "UPDATE produtos SET quantidade = %s WHERE codigo = %s",
            (nova_qtd, venda.codigo_produto)
        )

        valor_total = venda.quantidade * float(produto['preco_compra'])

        sql_venda = """
            INSERT INTO vendas (codigo_produto, quantidade, valor_total, metodo_pagamento, data_venda) 
            VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(
            sql_venda, 
            (venda.codigo_produto, venda.quantidade, valor_total, venda.metodo_pagamento)
        )

        conexao.commit()
        return {"sucesso": True, "mensagem": "Venda realizada com sucesso!"}

    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        if conexao: conexao.rollback()
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()