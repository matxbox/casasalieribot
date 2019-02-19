import logging
import time
from datetime import date
from telegram.ext import (CommandHandler, MessageHandler, ConversationHandler, Filters, Updater)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from requests import get
from os import environ
#%% vars
token = '633258565:AAHXlsA5cQklnLcZ8tg125LZjhGCLc0_hQc'
csickey = [['Milano Bovisa', 'La Masa', 'Candiani'],
		   ['Milano Leonardo'],
		   ['Como', 'Lecco'],
		   ['Cremona', 'Mantova', 'Piacenza']]
daykey = [['Oggi'], ['Domani'], ['Dopodomani']]
csicdict = {'Milano Bovisa': 'MIB',
			'La Masa': 'MIB01',
			'Candiani': 'MIB02',
			'Milano Leonardo': 'MIA',
			'Como': 'COE',
			'Cremona': 'CRG',
			'Lecco': 'LCF',
			'Mantova': 'MNI',
			'Piacenza': 'PCL'}
daydict = {'Oggi': 0,
		   'Domani': 3600*24,
		   'Dopodomani': 3600*48}
csic = []
day = []
#%% Comando /start


def start(bot, update):
	logging.info('@%s started with %s', update.message.from_user.username, update.message.text)
	bot.send_message(chat_id=update.message.chat_id,
					 text='Per ricevere la situazione delle aule nel tuo campus usa il comando /occupation, ' +

#%% General handler


# noinspection PyUnusedLocal
def generalupdate(bot, update):
	logging.info('@%s: %s', update.message.from_user.username, update.message.text)

#%% Conversation Handler


def preparafile(luogo, periodo):
	daytemp = periodo[0]
	urlkeys = {'csic': luogo[0],
			   'categoria': 'tutte',
			   'tipologia': 'tutte',
			   'giorno_day': str(daytemp.day),
			   'giorno_month': str(daytemp.month),
			   'giorno_year': str(daytemp.year),
			   'jaf_giorno_date_format': 'dd%2FMM%2Fyyyy',
			   'evn_visualizza': 'Visualizza+occupazioni'}
	url = 'https://www7.ceda.polimi.it/spazi/spazi/controller/OccupazioniGiornoEsatto.do'
	webpage = get(url, params=urlkeys)
	content = webpage.text
	startpoint = content.find('<table cellpadding="0" cellspacing="0" class="scrollTable"')
	endpoint = content.find('</table>', startpoint)
	table = content[startpoint:endpoint]
	with open('occupazioni.html', 'wb') as writeme:
		head = [r'<!DOCTYPE html>',
				r'<html>',
				r'<head>',
				r'<title>Occupazioni per Data</title>']
		csshead = r'<link rel="stylesheet" type="text/css" href="https://www7.ceda.polimi.it/spazi/table-MOZ.css"></head>'
		tail = r'</html>'
		final = '\n'.join(head)+'\n'+csshead+'\n'+table+'\n'+tail
		writeme.write(final.encode('utf-8'))
	return 'occupazioni.html'


def occupation(bot, update):
	logging.info('CONVSTART @%s: %s', update.message.from_user.username, update.message.text)
	bot.send_message(chat_id=update.message.chat_id,
					 text='Scegli il tuo campus o usa il comando /cancel per annullare',
					 reply_markup=ReplyKeyboardMarkup(csickey, True, True))
	return 0


def sede(bot, update):
	csic.append(csicdict.get(update.message.text))
	if csic == [None]:
		logging.warning('CONVSEDE @%s: %s', update.message.from_user.username, update.message.text)
		bot.send_message(chat_id=update.message.chat_id,
						 text='Non ho capito, riprova',
						 reply_markup=ReplyKeyboardMarkup(csickey, True, True))
		csic.clear()
		day.clear()
		return 0
	else:
		logging.info('CONVSEDE @%s: %s', update.message.from_user.username, update.message.text)
		bot.send_message(chat_id=update.message.chat_id,
						 text='Scegli il giorno',
						 reply_markup=ReplyKeyboardMarkup(daykey, True, True))
		return 1


def giorno(bot, update):
	try:
		day.append(date.fromtimestamp(time.time()+daydict.get(update.message.text)))
		logging.info('CONVGIORNO @%s: %s', update.message.from_user.username, update.message.text)
		nomefile = preparafile(csic, day)
		with open(nomefile, 'rb') as sendpage:
			bot.send_document(chat_id=update.message.chat_id, document=sendpage, reply_markup=ReplyKeyboardRemove())
		csic.clear()
		day.clear()
		return ConversationHandler.END
	except TypeError:
		logging.warning('CONVGIORNO @%s: %s', update.message.from_user.username, update.message.text)
		bot.send_message(chat_id=update.message.chat_id,
						 text='Non ho capito, riprova',
						 reply_markup=ReplyKeyboardMarkup(daykey, True, True))
		day.clear()
		return 1


def cancel(bot, update):
	logging.info('user @%s said %s', update.message.from_user.username, update.message.text)
	bot.send_message(chat_id=update.message.chat_id,
					 text='Richiesta annullata',
					 reply_markup=ReplyKeyboardRemove())
	csic.clear()
	day.clear()
	return ConversationHandler.END


def error(bot, update, errore):
	print(errore)
	logging.critical('TELEGRAMERROR @%s: %s', update.message.from_user.username, update.message.text)
	bot.send_message(chat_id=update.message.chat_id,
					 text='Qualcosa è andato storto, ricomincia da capo',
					 reply_markup=ReplyKeyboardRemove())
	csic.clear()
	day.clear()

#%% Avvia il bot


def avvio():
	try:
		environ['TZ'] = 'Europe/Rome'
		time.tzset()
		platf = 'UNIX'
	except AttributeError:
		platf = 'WIN'
	finally:
		logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
		logging.info('RUNNING on '+platf)
		updater = Updater(token=token)
		dispatcher = updater.dispatcher
		convers = ConversationHandler(entry_points=[CommandHandler('occupation', occupation)],
									  states={0: [MessageHandler(Filters.text & ~ Filters.command, sede)],
											  1: [MessageHandler(Filters.text & ~ Filters.command, giorno)]},
									  fallbacks=[CommandHandler('cancel', cancel)],
									  allow_reentry=True)
		start_handler = CommandHandler('start', start)
		general = MessageHandler(Filters.all, generalupdate)
		dispatcher.add_handler(start_handler)
		dispatcher.add_handler(convers)
		dispatcher.add_handler(general)
		dispatcher.add_error_handler(error)
		updater.start_polling()
		updater.idle()


if __name__ == '__main__':
	avvio()
#%% chatids
#252089415 tia
#60099501 ale
#91878464 bionda
#215417816 nana
