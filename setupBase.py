import psycopg2
import sys

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

db_string = str(sys.argv[1])

try:
    conn = psycopg2.connect(db_string)
except:
    print "I am unable to connect to the database"


def setup(conn):
    cur = conn.cursor()
    cur.execute("""
        DROP TABLE IF EXISTS opiniao;
        DROP TABLE IF EXISTS pergunta;
        DROP TABLE IF EXISTS usuario;

        CREATE TABLE usuario (
            id_usuario int NOT NULL PRIMARY KEY,
            nickname varchar(255)
        );

        CREATE TABLE pergunta (
            id_pergunta SERIAL NOT NULL PRIMARY KEY,
            pergunta varchar(500),
            perguntou int REFERENCES usuario,
            respondeu int REFERENCES usuario,
            respondido boolean,
            resposta varchar(500),
            data_pergunta date
        );

        CREATE TABLE opiniao(
            id_opiniao SERIAL NOT NULL PRIMARY KEY,
            perguntou int REFERENCES usuario,
            respondeu int REFERENCES usuario,
            id_pergunta int REFERENCES pergunta,
            opiniao varchar(20)
        );
    """)

    conn.commit()


    print "Funcionou"

setup(conn)

