from fastapi import APIRouter, HTTPException
from datetime import date, datetime, timedelta
from backend.database import conectar

router = APIRouter(prefix="/api/relatorios", tags=["Relatórios"])

@router.get("/vendas/diario")
def relatorio_vendas_diario():
    conexao = conectar()
    if not conexao:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")

    cursor = None
    try:
        cursor = conexao.cursor(dictionary=True)
        sql = """
            SELECT 
                v.id, 
                v.codigo_produto,
                COALESCE(p.nome, 'Produto não encontrado') AS nome_produto, 
                v.quantidade AS quantidade_vendida, 
                v.valor_total, 
                v.metodo_pagamento, 
                DATE_FORMAT(v.data_venda, '%d/%m/%Y %H:%i') AS data_venda
            FROM vendas v
            LEFT JOIN produtos p ON v.codigo_produto = p.codigo
            WHERE DATE(v.data_venda) = CURDATE()
            ORDER BY v.data_venda DESC
        """
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro SQL: {str(e)}")
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


@router.get("/vendas/mensal")
def relatorio_vendas_mensal():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT v.id, v.codigo_produto, COALESCE(p.nome, 'Produto não encontrado') AS nome, 
                   v.quantidade AS quantidade, v.valor_total, v.metodo_pagamento, 
                   DATE_FORMAT(v.data_venda, '%d/%m/%Y %H:%i') as data_hora
            FROM vendas v
            LEFT JOIN produtos p ON v.codigo_produto = p.codigo
            WHERE MONTH(v.data_venda) = MONTH(CURRENT_DATE()) 
              AND YEAR(v.data_venda) = YEAR(CURRENT_DATE())
            ORDER BY v.data_venda DESC
        """
        cursor.execute(sql)
        vendas = cursor.fetchall()
        total_mes = sum(float(v['valor_total']) for v in vendas)
        return {"vendas": vendas, "total_mes": total_mes}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()


@router.get("/critico")
def relatorio_critico(dias_alerta: int = 30):
    conexao = conectar()
    if not conexao:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")

    cursor = None
    try:
        cursor = conexao.cursor(dictionary=True)
        hoje = date.today()
        data_limite = hoje + timedelta(days=dias_alerta)

        sql = """
            SELECT codigo, nome, quantidade, qnt_minima, data_vencimento
            FROM produtos
            WHERE quantidade <= qnt_minima 
               OR (data_vencimento IS NOT NULL AND data_vencimento <= %s)
            ORDER BY data_vencimento ASC, quantidade ASC
        """
        cursor.execute(sql, (data_limite,))
        produtos = cursor.fetchall()

        resultado = []
        for prod in produtos:
            alertas = []
            qtd = prod["quantidade"]
            qnt_min = prod["qnt_minima"]
            vencimento_raw = prod["data_vencimento"]

            # Tratamento robusto para data de vencimento vinda do MySQL
            vencimento = None
            if isinstance(vencimento_raw, datetime):
                vencimento = vencimento_raw.date()
            elif isinstance(vencimento_raw, date):
                vencimento = vencimento_raw

            if qtd <= qnt_min:
                alertas.append(f"📦 ESTOQUE BAIXO ({qtd}/{qnt_min})")

            if vencimento:
                if vencimento < hoje:
                    alertas.append(f"⛔ VENCIDO EM {vencimento.strftime('%d/%m/%Y')}")
                elif vencimento <= data_limite:
                    dias_restantes = (vencimento - hoje).days
                    alertas.append(f"⏳ VENCE EM {dias_restantes} DIA(S)")

            venc_str = vencimento.strftime('%d/%m/%Y') if vencimento else "N/A"
            venc_iso = vencimento.strftime('%Y-%m-%d') if vencimento else None

            resultado.append({
                "codigo": prod["codigo"],
                "nome": prod["nome"],
                "quantidade": qtd,
                "qnt_minima": qnt_min,
                "data_vencimento": venc_str,
                "data_vencimento_str": venc_str,
                "data_vencimento_iso": venc_iso,
                "alertas": alertas
            })

        return {
            "produtos": resultado,
            "hoje": hoje.strftime("%Y-%m-%d"),
            "data_limite": data_limite.strftime("%Y-%m-%d")
        }

    except Exception as e:
        print(f"❌ Erro MySQL detalhado: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conexao and conexao.is_connected(): conexao.close()