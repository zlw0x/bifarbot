import datetime as dt
import random
from threading import Thread
import requests
import telebot
import time

token = '###'
garry_id = ###
sanya_id = ###
url = 'https://fs3.drugber.ru/assembling'
cookie = {'###': '###'}
headers = {
    'Connection': 'close',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}
last_update = dt.datetime(2022, 1, 1)
bot = telebot.TeleBot(token)
enable = {sanya_id: True, garry_id: True}
cur_orders = {'': ''}
old_orders = {'': ''}
types = {'FS.': 'Самовывоз',
         'FSK': 'Наш водила',
         'SDEK': 'СДЭК',
         'X5': '5Post',
         'WILD': 'WildBerries',
         'OZON': 'Ozon',
         'DOSTA': 'Dostavista',
         'YAND': 'Экспресс',
         'YD3': 'Яднекс',
         'POST': 'Почта',
         'CAT': 'Индивидуальная доставка'
         }


def set_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("Все заказы")
    btn2 = telebot.types.KeyboardButton("KUSHETKA MODE")
    markup.add(btn1, btn2)
    return markup


def update_info():
    global last_update
    if dt.datetime.now() - last_update > dt.timedelta(seconds=57):
        x = True
        while x:
            try:
                r = requests.get(url, headers=headers, cookies=cookie)
                page = r.text
                x = False
                print(f'update {dt.datetime.now().strftime("%H:%M:%S")}')
            except ConnectionError:
                x = True
                page = 'error order-list-update /img/order-images/ error'
                print("connection error")
                time.sleep(5)
        old_orders.clear()
        old_orders.update(cur_orders.copy())
        cur_orders.clear()
        for i in page.split('order-list-')[1:]:
            for j in i.split('/img/order-images/')[1:]:
                for k in types:
                    if j.startswith(k):
                        j = types[k]
                        if i.__contains__("border-2 border-stone-300 opacity-25 shadow-inner ring ring-gray-300"):
                            j += "  нет товара"
                cur_orders[i[:6]] = j
                last_update = dt.datetime.now()


def send_notify():
    for n in enable:
        if enable[n]:
            update_info()
            body_message = ''
            if old_orders != cur_orders:
                for i in cur_orders:
                    if not old_orders.__contains__(i):
                        body_message = body_message + i + " " + cur_orders[i] + "\n"
            if body_message != '':
                try:
                    bot.send_message(n, body_message, reply_markup=set_markup())
                except ConnectionError:
                    print(f'err notify {dt.datetime.now().strftime("%H:%M:%S")}')
                finally:
                    print(f'continue notify {dt.datetime.now().strftime("%H:%M:%S")}')


@bot.message_handler(content_types=['text'])
def send_all_orders(message):
    update_info()
    if message.text == "Все заказы" and enable.__contains__(message.chat.id):
        out = f'Обновлено {last_update.strftime("%H:%M %d.%m")} \n\n'
        for i in cur_orders:
            out = out + f'{i} {cur_orders[i]} \n'
        try:
            bot.send_message(message.chat.id, out, reply_to_message_id=message.id, reply_markup=set_markup())
        except ConnectionError:
            print(f'err all orders {dt.datetime.now().strftime("%H:%M:%S")}')
        finally:
            print(f'continue all orders {dt.datetime.now().strftime("%H:%M:%S")}')
    if message.text == "KUSHETKA MODE":
        on_off(message)


def on_off(message):
    if enable[message.chat.id]:
        enable[message.chat.id] = False
        msg = 'OFF'
    else:
        enable[message.chat.id] = True
        msg = 'ON'
    try:
        bot.send_message(message.chat.id, msg, reply_to_message_id=message.id, reply_markup=set_markup())
    except ConnectionError:
        print(f'err on_off {dt.datetime.now().strftime("%H:%M:%S")}')
    finally:
        print(f'continue on_off {dt.datetime.now().strftime("%H:%M:%S")}')


def notify():
    while True:
        if 10 <= int(dt.datetime.now().strftime("%H")) < 19:
            update_info()
            send_notify()
        time.sleep(random.uniform(58.330185127252884, 63.092324756265473))


if __name__ == "__main__":
    noti = Thread(target=notify, daemon=True)
    noti.start()
    bot.infinity_polling()
