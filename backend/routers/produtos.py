from fastapi import APIRouter, HTTPException
from datetime import datetime
from backend.database import conectar
from backend.schemas.schemas import ProdutoSchema

router = APIRouter(prefix="/api/produtos", tags=["Produtos"])

@router.post("")
def cadastrar_produto(produto: ProdutoSchema):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        data_venc = None
        if produto.data_vencimento:
            data_venc = datetime.strptime(produto.data_vencimento, "%Y-%m-%d").date()

        sql = """
            INSERT INTO produtos (codigo, quantidade, qnt_minima, preco_compra, nome, categoria, fornecedor, data_vencimento) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            produto.codigo, produto.quantidade, produto.qnt_minima, produto.preco_compra,
            produto.nome, produto.categoria, produto.fornecedor, data_venc
        )

        cursor.execute(sql, valores)
        conexao.commit()
        return {"sucesso": True, "mensagem": "Produto cadastrado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()

@router.get("")
def listar_produtos():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produtos ORDER BY nome ASC")
        produtos = cursor.fetchall()

        for p in produtos:
            if p['data_vencimento']:
                p['data_vencimento'] = p['data_vencimento'].strftime("%Y-%m-%d")

        return {"produtos": produtos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()

@router.put("/{codigo}")
def atualizar_produto(codigo: int, produto: ProdutoSchema):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        data_venc = None
        if produto.data_vencimento:
            data_venc = datetime.strptime(produto.data_vencimento, "%Y-%m-%d").date()

        sql = """
            UPDATE produtos 
            SET quantidade = %s, qnt_minima = %s, preco_compra = %s, 
                nome = %s, categoria = %s, fornecedor = %s, data_vencimento = %s
            WHERE codigo = %s
        """
        valores = (
            produto.quantidade, produto.qnt_minima, produto.preco_compra,
            produto.nome, produto.categoria, produto.fornecedor, data_venc, codigo
        )

        cursor.execute(sql, valores)
        conexao.commit()
        return {"sucesso": True, "mensagem": "Produto atualizado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()

@router.delete("/{codigo}")
def excluir_produto(codigo: int):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM produtos WHERE codigo = %s", (codigo,))
        conexao.commit()
        return {"sucesso": True, "mensagem": "Produto excluído com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()