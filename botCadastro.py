from telegram import (ReplyKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import logging
import psycopg2
import persistence
import sys

PEDINDO_NICKNAME, \
CUMPRIMENTOS, \
DECIDA_SE_PERGUNTA_OU_RESPONDE, \
PERGUNTA, \
NAO_IMPLEMENTADO, \
RESPONDA, \
REPUTACAO = range(7)

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

db_string = str(sys.argv[1])
token = str(sys.argv[2])

print token

try:
    conn = psycopg2.connect(db_string)
except:
    print "Falha ao conectar na base"

updater = Updater(token)
dp = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(bot, update):
    user = update.message.from_user
    if persistence.existe_usuario_na_base(conn, user.id):
        return cumprimentos(bot, update)
    update.message.reply_text(
        'Ola, sou o bot PifPaf e vou conversar com voce para fazer o seu cadastro \n\n '
        'Se nao quiser fazer isso agora escreva /cancelar \n\n '
        'Qual seu apelido?')
    return PEDINDO_NICKNAME

def pedindo_nickname(bot, update):
    user = update.message.from_user
    user_id = user.id
    nickname = update.message.text
    first_name = user.first_name
    logger.info("Nome de %s: %s" % (first_name, nickname))
    persistence.adicionar_novo_usuario(conn, nickname, user_id)
    return cumprimentos(bot, update)

def cumprimentos(bot, update):
    reply_keyboard = [['Perguntar', 'Responder']]

    user = update.message.from_user
    nome = persistence.nome_de_usuario(conn, user.id)
    score = persistence.score(conn, user.id)
    update.message.reply_text('Ola, %s. Seu score e: %s deseja perguntar ou responder' % (nome, score),
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return DECIDA_SE_PERGUNTA_OU_RESPONDE

def cancelar(bot, update):
    user = update.message.from_user
    logger.info("Usuario %s cancelou a conversa." % user.first_name)
    update.message.reply_text('Tchau :)')
    return ConversationHandler.END

def decida_se_pergunta_ou_responde(bot, update):
    if update.message.text == "Perguntar":
        update.message.reply_text("Faca sua pergunta")
        return PERGUNTA
    else:
        user = update.message.from_user
        if persistence.existe_pergunta_nao_respondida(conn, user.id):
            pergunta = persistence.escolhe_pergunta_para_usuario(conn, user.id)
            update.message.reply_text(pergunta)
            return RESPONDA
        else:
            update.message.reply_text("Nao tem pergunta")
            return ConversationHandler.END

def pergunta (bot,update):
    user = update.message.from_user
    perguntou = user.id
    logger.info("Pergunta de %s: %s" % (user.first_name, update.message.text))
    persistence.adicionar_pergunta(conn, update.message.text, perguntou)
    id_pergunta = persistence.pega_id_da_pergunta_perguntou(conn,perguntou)
    persistence.adiciona_opiniao_vazia(conn, perguntou, id_pergunta)
    update.message.reply_text("Logo sua pergunta sera respondida. Tchau :)")
    return ConversationHandler.END

def responda(bot, update):
    user = update.message.from_user
    respondeu = update.message.from_user.id
    pergunta = persistence.escolhe_pergunta_para_usuario(conn, user.id)
    resposta = update.message.text
    id_pergunta = persistence.pega_id_da_pergunta(conn, respondeu)
    persistence.adiciona_resposta_na_tabela_pergunta(conn, resposta, respondeu)
    persistence.adicionar_respondeu_na_opiniao(conn, respondeu, id_pergunta)
    update.message.reply_text("Respondido, obrigado")

    reply_keyboard = [['Sim', 'Nao']]
    chat_id, resposta = persistence.pegar_a_resposta(conn, id_pergunta)
#PROBLEMA: Mais de uma resposta nao avaliada nao funciona
#Tem que fazer o usuario avalias se gostou ou nao uma resposta por vez
#uma solucao eh jogar essa logica em outro metodo e fazer ser recursivo ate
#nao ter mais respostas pra avaliar, pra isso o select das respostas a serem avaliadas
# tem que ser deterministico (melhor jeito e order by uma coluna nova de timestamp)
    bot.sendMessage(chat_id=chat_id, text="Alguem respondeu a pergunta : %s" %pergunta)
    bot.sendMessage(chat_id=chat_id, text=resposta)
    bot.sendMessage(chat_id=chat_id, text="Gostou da resposta?",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    dp.handlers[0][0].conversations[(chat_id, chat_id)] = REPUTACAO
    return ConversationHandler.END


def reputacao(bot,update):
    user_id = update.message.from_user.id
    opiniao = update.message.text
    persistence.adicionar_opiniao(conn, user_id, opiniao)
    update.message.reply_text("Obrigado pela sua opiniao :)")
    return ConversationHandler.END


def nao_implementado(bot, update):
    logger.info("Nao implementado %s" % update.message.text)
    update.message.reply_text('404')
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        PEDINDO_NICKNAME: [MessageHandler([Filters.text], pedindo_nickname)],
        CUMPRIMENTOS: [MessageHandler([Filters.text], cumprimentos)],
        NAO_IMPLEMENTADO : [MessageHandler([Filters.text], nao_implementado)],
        PERGUNTA: [MessageHandler([Filters.text], pergunta)],
        DECIDA_SE_PERGUNTA_OU_RESPONDE: [RegexHandler('^(Perguntar|Responder)$', decida_se_pergunta_ou_responde)],
        RESPONDA: [MessageHandler([Filters.text], responda)],
        REPUTACAO: [MessageHandler([Filters.text], reputacao)]
    },

    fallbacks=[CommandHandler('cancelar', cancelar)]
)
dp.add_handler(conv_handler)


updater.start_polling()
updater.idle()
