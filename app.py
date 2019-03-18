import logging
import time
from datetime import date
from telegram.ext import (CommandHandler, MessageHandler, ConversationHandler, Filters, Updater)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from requests import get
from os import environ
from sys import argv

#%% vars
csic_keyboard = [['Milano Bovisa', 'La Masa', 'Candiani'],
		   ['Milano Leonardo'],
		   ['Como', 'Lecco'],
		   ['Cremona', 'Mantova', 'Piacenza']]
day_keyboard = [['Oggi'], ['Domani'], ['Dopodomani']]
csic_dict = {'Milano Bovisa': 'MIB',
			'La Masa': 'MIB01',
			'Candiani': 'MIB02',
			'Milano Leonardo': 'MIA',
			'Como': 'COE',
			'Cremona': 'CRG',
			'Lecco': 'LCF',
			'Mantova': 'MNI',
			'Piacenza': 'PCL'}
day_dict = {'Oggi': 0,
		   'Domani': 3600*24,
		   'Dopodomani': 3600*48}


def start(bot, update):
	logging.info('@%s started with %s', update.message.from_user.username, update.message.text)
	bot.send_message(chat_id=update.message.chat_id,
					 text='Per ricevere la situazione delle aule nel tuo campus usa il comando /occupation, ')


# noinspection PyUnusedLocal
def generalupdate(bot, update):
	logging.info('@%s: %s', update.message.from_user.username, update.message.text)


def preparafile(luogo, periodo):
	urlkeys = {'csic': luogo,
			   'categoria': 'tutte',
			   'tipologia': 'tutte',
			   'giorno_day': str(periodo.day),
			   'giorno_month': str(periodo.month),
			   'giorno_year': str(periodo.year),
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
					 reply_markup=ReplyKeyboardMarkup(csic_keyboard, True, True))
	return 0


def sede(bot, update):
	global csic
	csic = csic_dict.get(update.message.text)
	if csic is None:
		logging.warning('CONVSEDE @%s: %s', update.message.from_user.username, update.message.text)
		bot.send_message(chat_id=update.message.chat_id,
						 text='Non ho capito, riprova',
						 reply_markup=ReplyKeyboardMarkup(csic_keyboard, True, True))
		try: del csic
		except NameError: pass
		return 0
	else:
		logging.info('CONVSEDE @%s: %s', update.message.from_user.username, update.message.text)
		bot.send_message(chat_id=update.message.chat_id,
						 text='Scegli il giorno',
						 reply_markup=ReplyKeyboardMarkup(day_keyboard, True, True))
		return 1


def giorno(bot, update):
	global csic
	try:
		day = date.fromtimestamp(time.time() + day_dict.get(update.message.text))
		logging.info('CONVGIORNO @%s: %s', update.message.from_user.username, update.message.text)
		nomefile = preparafile(csic, day)
		with open(nomefile, 'rb') as sendpage:
			bot.send_document(chat_id=update.message.chat_id, document=sendpage, reply_markup=ReplyKeyboardRemove())
		try: del csic
		except NameError: pass
		return ConversationHandler.END
	except TypeError:
		logging.warning('CONVGIORNO @%s: %s', update.message.from_user.username, update.message.text)
		bot.send_message(chat_id=update.message.chat_id,
						 text='Non ho capito, riprova',
						 reply_markup=ReplyKeyboardMarkup(day_keyboard, True, True))
		return 1


def cancel(bot, update):
	global csic
	logging.info('user @%s said %s', update.message.from_user.username, update.message.text)
	bot.send_message(chat_id=update.message.chat_id,
					 text='Richiesta annullata',
					 reply_markup=ReplyKeyboardRemove())
	try: del csic
	except NameError: pass
	return ConversationHandler.END


def error(bot, update, errore):
	global csic
	print(errore)
	logging.critical('TELEGRAMERROR @%s: %s', update.message.from_user.username, update.message.text)
	bot.send_message(chat_id=update.message.chat_id,
					 text='Qualcosa è andato storto, ricomincia da capo',
					 reply_markup=ReplyKeyboardRemove())
	try: del csic
	except NameError: pass

def reply_location(bot, update):
	import polimi_struttura_oop as polimi
	polimi.force_load_of_data()
	location, time = update.message.location, update.message.date
	import datetime
	#time = datetime.datetime(2019, 3, 18, hour=15, minute = 15)  # TODO: elimina questa sovrascrittura
	best_rooms = polimi.best_rooms((location.latitude, location.longitude), time, limit=10)
	data = [(room.nome, room.occupation.evaluate(time)//60, room.occupation.evaluate(time)%60, room.current_event(time).endtime.strftime('%H:%M')) for room in best_rooms]
	rows = [f'{values[0]}: libera per {values[1]} h {values[2]} min (fino alle {values[3]})' for values in data]
	message = '\n'.join([str(i) for i in rows])
	bot.send_message(chat_id=update.message.chat_id,
						 text=message,
						 )

def avvio():
	try: token = argv[1]
	except IndexError:
		with open('token_sviluppo.txt', 'r') as file:
			token = file.read()
	updater = Updater(token=token)
	dispatcher = updater.dispatcher
	convers = ConversationHandler(entry_points=[CommandHandler('occupation', occupation)],
									states={0: [MessageHandler(Filters.text & ~ Filters.command, sede)],
											1: [MessageHandler(Filters.text & ~ Filters.command, giorno)]},
									fallbacks=[CommandHandler('cancel', cancel)],
									allow_reentry=True)
	start_handler = CommandHandler('start', start)
	general = MessageHandler(Filters.all, generalupdate)
	location_msg = MessageHandler(Filters.location, reply_location)
	dispatcher.add_handler(location_msg)
	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(convers)
	dispatcher.add_handler(general)
	dispatcher.add_error_handler(error)
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
	try:
		time.tzset()
	except AttributeError:
		platf = 'WIN'
		updater.start_polling()
	else:
		environ['TZ'] = 'Europe/Rome'
		platf = 'UNIX'
		PORT = int(environ.get('PORT', '8443'))
		updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=token)
		updater.bot.set_webhook("https://casa-salieri-bot.herokuapp.com/"+token)
	logging.info('RUNNING on ' + platf)
	updater.idle()


if __name__ == '__main__':
	avvio()
"""
chatids
252089415 tia
60099501 ale
91878464 bionda
215417816 nana
"""
