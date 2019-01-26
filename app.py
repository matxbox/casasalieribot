import logging
from datetime import (date,datetime)
from time import time
from telegram.ext import (CommandHandler,MessageHandler,ConversationHandler,Filters,Updater)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import requests
token='669719701:AAE7F6GdGKw1eVT_fy_8hyRA2_1c3HKxhuQ'
#%% Funzione di avvio del bot
def start(bot, update):
    print(update.message.text)
    bot.send_message(chat_id=update.message.chat_id,
                     text='Per ricevere la situazione delle aule nel tuo campus usa il comando /occupation, altrimenti attaccati a sto cazzo')
#%% vars
csickey=[['Milano Bovisa', 'La Masa','Candiani'],
         ['Milano Leonardo'],
         ['Como', 'Lecco'],
         ['Cremona','Mantova','Piacenza']]
daykey=[['Oggi'],['Domani'],['Dopodomani']]
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
def preparafile(sede,giorno):
    daytemp=giorno[0]
    urlkeys={'csic':sede[0],
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
    return 'occupazioni.html'
def occupation(bot,update):
    logging.info('user @%s said %s',update.message.from_user.username,update.message.text)
    bot.send_message(chat_id=update.message.chat_id,
                     text='Scegli il tuo campus o usa il comando /cancel per annullare',
                     reply_markup=ReplyKeyboardMarkup(csickey,True,True))
    return 0
def sede(bot,update):
    csic.append(csicdict.get(update.message.text))
    if csic==[None]:
        logging.warning('user @%s said %s',update.message.from_user.username,update.message.text)
        bot.send_message(chat_id=update.message.chat_id,text='Qualcosa è andato storto, riprova',reply_markup=ReplyKeyboardMarkup(csickey,True,True))
        csic.clear()
        day.clear()
        return 0
    else:
        logging.info('user @%s said %s',update.message.from_user.username,update.message.text)
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
    if day==[None]:
        logging.warning('user @%s said %s',update.message.from_user.username,update.message.text)
        bot.send_message(chat_id=update.message.chat_id,text='Qualcosa è andato storto, riprova',reply_markup=ReplyKeyboardMarkup(daykey,True,True))
        day.clear()
        return 1
    else:
        nomefile=preparafile(csic,day)
        with open(nomefile,'rb') as sendpage:
            bot.send_document(chat_id=update.message.chat_id,document=sendpage,reply_markup=ReplyKeyboardRemove())
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

#%% Avvia il bot
def avvio():
    logging.info('RUNNING')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    updater=Updater(token=token)
    dispatcher=updater.dispatcher
    convers=ConversationHandler(entry_points=[CommandHandler('occupation',occupation)],
                            states={0:[MessageHandler(Filters.text & ~ Filters.command,sede)],
                                    1:[MessageHandler(Filters.text & ~ Filters.command,giorno)]},
                            fallbacks=[CommandHandler('cancel',cancel)],
                            allow_reentry=True)
    start_handler=CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(convers)
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()
if __name__=='__main__':
    avvio()
#%% chatids
#252089415 tia
#60099501 ale
