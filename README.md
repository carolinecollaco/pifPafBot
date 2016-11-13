# pifPafBot
Precisa instalar o postgres
criar uma base ex botpif
instalar o python 2 e psycopg2, no ubuntu é sudo apt-get install python-psycopg2 
http://initd.org/psycopg/docs/install.html

primeiro roda: 
python setupBase.py "String de conexão da base ex: dbname='botpif' user='postgres' host='localhost' password='suasenha'"
depois
python botCadastro.py "String de conexão da base" "token do bot"
