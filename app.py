import logging
from datetime import date
from time import time
from telegram.ext import (CommandHandler,MessageHandler,ConversationHandler,Filters,Updater)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import requests
token='669719701:AAE7F6GdGKw1eVT_fy_8hyRA2_1c3HKxhuQ'
updater=Updater(token=token)
dispatcher=updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
alleluia=[]
#%% Funzione di avvio del bot
def start(bot, update):
    alleluia.append(update)
    print(update.message.text)
    bot.send_message(chat_id=update.message.chat_id,
                     text='Per ricevere la situazione delle aule nel tuo campus usa il comando /occupation, altrimenti attaccati a sto cazzo')
start_handler=CommandHandler('start', start)
dispatcher.add_handler(start_handler)
#%% vars
csicdict={'Milano Bovisa': 'MIB',
          'La Masa':'MIB01',
          'Candiani':'MIB02',
          'Milano Leonardo':'MIA',
          'Como':'COE',
          'Cremona':'CRG',
          'Lecco':'LCF',
          'Mantova':'MNI',
          'Piacenza':'PCL'}
csic=[]
day=[]
#%% Conversation Handler
def occupation(bot,update):
    logging.info('user @%s said %s',update.message.from_user.username,update.message.text)
    csickey=[['Milano Bovisa', 'La Masa','Candiani'],
             ['Milano Leonardo'],
             ['Como', 'Lecco'],
             ['Cremona','Mantova','Piacenza']]
    bot.send_message(chat_id=update.message.chat_id,
                     text='Scegli il tuo campus o usa il comando /cancel per annullare',
                     reply_markup=ReplyKeyboardMarkup(csickey,True,True))
    return 0
def sede(bot,update):
    daykey=[['Oggi'],['Domani'],['Dopodomani']]
    logging.info('user @%s said %s',update.message.from_user.username,update.message.text)
    csic.append(csicdict.get(update.message.text))
    if csic==[None]:
        bot.send_message(chat_id=update.message.chat_id,text='Qualcosa è andato storto, riprova',reply_markup=ReplyKeyboardRemove())
        csic.clear()
        day.clear()
        return ConversationHandler.END
    else:
        bot.send_message(chat_id=update.message.chat_id,
                 text='Scegli il giorno',
                 reply_markup=ReplyKeyboardMarkup(daykey,True,True))
        return 1
def giorno(bot,update):
    logging.info('user @%s said %s',update.message.from_user.username,update.message.text)
    daydict={'Oggi':date.fromtimestamp(time()),
             'Domani':date.fromtimestamp(time()+3600*24),
             'Dopodomani':date.fromtimestamp(time()+3600*48)}
    day.append(daydict.get(update.message.text))
    daytemp=day[0]
    try:
        urlkeys={'csic':csic[0],
                 'categoria':'tutte',
                 'tipologia':'tutte',
                 'giorno_day':str(daytemp.day),
                 'giorno_month':str(daytemp.month),
                 'giorno_year':str(daytemp.year),
                 'jaf_giorno_date_format':'dd%2FMM%2Fyyyy',
                 'evn_visualizza':'Visualizza+occupazioni'}
        webpage=requests.get('https://www7.ceda.polimi.it/spazi/spazi/controller/OccupazioniGiornoEsatto.do',params=urlkeys)
        oldcontent=webpage.content
        newcontent=oldcontent.replace(b'/spazi/table-MOZ.css',b'https://www7.ceda.polimi.it/spazi/table-MOZ.css')
        with open('occupazioni.html','wb') as page:
            page.write(newcontent)
        with open('occupazioni.html','rb') as sendpage:
            bot.send_document(chat_id=update.message.chat_id,document=sendpage,reply_markup=ReplyKeyboardRemove())
        csic.clear()
        day.clear()
        return ConversationHandler.END
    except AttributeError:
        logging.warning('user @%s said %s and something wrong happened',update.message.from_user.username,update.message.text)
        bot.send_message(chat_id=update.message.chat_id,text='Qualcosa è andato storto, riprova',reply_markup=ReplyKeyboardRemove())
        csic.clear()
        day.clear()
        return ConversationHandler.END
def cancel(bot,update):
    logging.info('user @%s said %s',update.message.from_user.username,update.message.text)
    bot.send_message(chat_id=update.message.chat_id,text='Richiesta annullata',reply_markup=ReplyKeyboardRemove())
    csic.clear()
    day.clear()
    return ConversationHandler.END 
def error(bot,update,error):
    logging.warning('user @%s said %s and something wrong happened',update.message.from_user.username,update.message.text)
    bot.send_message(chat_id=update.message.chat_id,text='Qualcosa è andato storto, riprova',reply_markup=ReplyKeyboardRemove())
    csic.clear()
    day.clear()
convers=ConversationHandler(entry_points=[CommandHandler('occupation',occupation)],
                            states={0:[MessageHandler(Filters.text & ~ Filters.command,sede)],
                                    1:[MessageHandler(Filters.text & ~ Filters.command,giorno)]},
                            fallbacks=[CommandHandler('cancel',cancel)],
                            allow_reentry=True)
dispatcher.add_handler(convers)
dispatcher.add_error_handler(error)
#%% Comando /occupation
"""
def occupation(bot, update, args):
    bot.send_message(chat_id=update.message.chat_id,text='scegli cosa preferisci',reply_markup=ReplyKeyboardMarkup(keyboard=buttons,resize_keyboard=True))
#def occ_details(bot,update):
#    bot.send_message(chat_id=update.message.chat_id,text='Scegli la sede'
    
    with open('laltra.jpg','rb') as image:
        bot.send_photo(chat_id=update.message.chat_id,photo=image,reply_to_message_id=update.message.message_id,reply_markup=ReplyKeyboardRemove)
dispatcher.add_handler(CommandHandler('occupation',occupation))
dispatcher.add_handler(messhandler(Filters.text,placeholder))
"""
#%% Avvia il bot
updater.start_polling()
updater.idle()
#%% chatids
#252089415 tia
#60099501 ale