import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_na_base(conn, query, values):
    cur = conn.cursor()
    query_log = "QUERY => "+query
    logger.info(query_log % values)
    cur.execute(query, values)
    conn.commit()

def pegue_o_primeiro_resultado(conn, query, values):
    cur = conn.cursor()
    query_log = "QUERY => "+query
    logger.info(query_log % values)
    cur.execute(query, values)
    rows = cur.fetchall()
    return rows[0][0]

def adicionar_novo_usuario(conn, nickname, id):
    execute_na_base(conn, """INSERT INTO usuario (id_usuario , nickname) VALUES (%s, %s)""", (id, nickname))

def adicionar_pergunta(conn, pergunta, id):
    execute_na_base(conn, """INSERT INTO pergunta (pergunta, perguntou, respondido, data_pergunta) VALUES (%s, %s, false, current_date)""", (pergunta, id))

def pega_id_da_pergunta(conn, respondeu):
    return pegue_o_primeiro_resultado(conn, """SELECT  id_pergunta FROM pergunta WHERE respondeu = %s AND respondido = FALSE """, (respondeu,))

def pega_id_da_pergunta_perguntou(conn, perguntou):
    return pegue_o_primeiro_resultado(conn, """SELECT  id_pergunta FROM pergunta WHERE perguntou = %s AND respondido = FALSE """, (perguntou,))

def adiciona_resposta_na_tabela_pergunta(conn, resposta, id_usuario):
    cur = conn.cursor()
    cur.execute("""UPDATE pergunta SET resposta = %s, respondido = TRUE WHERE respondeu = %s AND respondido = FALSE """, (resposta, id_usuario))
    conn.commit()

def nome_de_usuario(conn, id):
    return pegue_o_primeiro_resultado(conn, """SELECT nickname from usuario WHERE id_usuario = %s""", (id,))

def existe_usuario_na_base(conn, id):
    cur = conn.cursor()
    cur.execute("""SELECT nickname from usuario WHERE id_usuario = %s""", (id,))
    rows = cur.fetchall()
    return len(rows) > 0

def existe_pergunta_nao_respondida(conn, id_usuario):
    cur = conn.cursor()
    cur.execute("""
SELECT
  pergunta
from pergunta, usuario
WHERE
  respondido = FALSE
  AND pergunta.perguntou = usuario.id_usuario
  AND perguntou <> %s
ORDER BY
  data_pergunta,
  (SELECT COUNT(*) FROM opiniao WHERE opiniao = 'Sim' AND respondeu = usuario.id_usuario) DESC,
  id_pergunta
LIMIT 1""", (id_usuario,))
    rows = cur.fetchall()
    return len(rows) > 0

def escolhe_pergunta_para_usuario(conn, id_usuario):
    cur = conn.cursor()
    cur.execute("""SELECT pergunta, id_pergunta from pergunta WHERE respondido = FALSE AND perguntou <> %s ORDER BY id_pergunta LIMIT 1""", (id_usuario,))
    rows = cur.fetchall()
    id_pergunta = rows[0][1]
    pergunta = rows[0][0]
    cur = conn.cursor()
    cur.execute("""UPDATE pergunta SET respondeu = %s WHERE id_pergunta = %s""", (id_usuario, id_pergunta))
    conn.commit()
    return pergunta

def pegar_a_resposta(conn, id_pergunta):
    cur = conn.cursor()
    cur.execute("""SELECT resposta, perguntou FROM Pergunta WHERE id_pergunta = %s""", (id_pergunta,))
    rows = cur.fetchall()
    chat_id = rows[0][1]
    resposta = rows[0][0]
    return (chat_id, resposta)

def adiciona_opiniao_vazia(conn, perguntou, pergunta):
    execute_na_base(conn, """INSERT INTO opiniao (perguntou, id_pergunta) VALUES (%s, %s)""", (perguntou, pergunta))

def adicionar_respondeu_na_opiniao(conn, respondeu, pergunta):
    execute_na_base(conn, """UPDATE opiniao SET respondeu = %s WHERE id_pergunta = %s""", (respondeu, pergunta))

def adicionar_opiniao(conn, perguntou, opiniao):
    execute_na_base(conn, """UPDATE opiniao SET perguntou = %s ,opiniao  = %s WHERE opiniao IS NULL""", (perguntou, opiniao))

def score(conn, respondeu):
    return pegue_o_primeiro_resultado(conn, """SELECT COUNT(*) FROM opiniao WHERE opiniao = 'Sim' AND respondeu = %s  """, (respondeu,))
