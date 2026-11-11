import mysql.connector

def conectar():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='@Maya2901',
        database='estoque'
    )

# Código de teste (roda apenas se você executar o database.py diretamente)
if __name__ == '__main__':
    try:
        con = conectar()
        print("✅ Conexão com o MySQL realizada com sucesso!")
        con.close()
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")