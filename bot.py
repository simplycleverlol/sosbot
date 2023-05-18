import os, json, logging, random
from aiogram import Bot, Dispatcher, executor, types
from paho.mqtt import client as mqtt_client
logging.basicConfig(level=logging.INFO)
class storage(dict):
    def __init__(self, name : str):
        TEMPLATEVAL = {'chats': [], 'master': None,
                        'api': '', 'secret': 'GoodWin',
                        'mqtt':{
                            'server': '127.0.0.1', 
                            'login' : None, 
                            'pass': None,
                            'topic':'myaso/sos/sos'
                        }
                        }
        self.name = name
        if os.path.exists(self.name):
            with open(self.name, 'r') as f:
                try:
                    self.update(json.load(f))
                    for key in TEMPLATEVAL:
                        if self.get(key) == None:
                            self[key] = TEMPLATEVAL[key]
                except:
                    self.update(TEMPLATEVAL) 
                self.save()
        else:
            self.update(TEMPLATEVAL) 
            self.save() 

    def save(self):
        with open(self.name, 'w') as f:
            json.dump(self, f, indent=4)
    def read(self):
        with open(self.name, 'r') as f:
            self.update(json.load(f))

def bins(a, x):
    l, r = -1, len(a)
    while r-l > 1:
        m = (r+l)//2
        if a[m] < x:
            l = m
        else: r = m
    return r
def checkc(c):
    global config
    l = config['chats']
    return bins(l, c) < len(l)

def addc(c):
    global config
    l = config['chats']
    x = bins(l, c)
    if x == len(l):
        l.append(c)
        l.sort()

def remc(c):
    global config
    l = config['chats']
    x = bins(l, c)
    if x < len(l):
        l.pop(x)


config = storage('cnf.json')

bot = Bot(token=config['api'])
dp = Dispatcher(bot)
inline_ctp = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Вызов Росгвардии', callback_data="ctp"))

def fsos(mtext):
    mtext = mtext.text.lower().split()
    return any(word in mtext for word in ['sos', 'омон', 'тревога']) or mtext == ['!']

@dp.message_handler(fsos)
async def regularmsg(message: types.Message):
    logging.info(f'Alarm msg received: Chat id: {message.chat.id}')
    if checkc(message.chat.id):
        await message.reply('Необходима помощь?', reply_markup=inline_ctp)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    print(message)
    if checkc(message.chat.id):
        await message.reply("Сервис активен")
    else:    await message.reply("Для активации отправьте кодовое слово ответным сообщением")

@dp.message_handler(commands=['stop'])
async def send_unwelcome(message: types.Message):
    if checkc(message.chat.id):
        remc(message.chat.id)
        config.save()
        await message.reply('Успешно отключено')
    else:    await message.reply("Сервис не активен")

@dp.message_handler(text = config['secret'])
async def activate(message: types.Message):
    if checkc(message.chat.id):
        await message.reply('Уже активно')
    else:
        config.save()
        logging.info(f'Activation for chat #{message.chat.id} : {message.chat.title} by {message.from_user.id} : {message.from_user.full_name}')
        await message.reply("Бот активирован!")



@dp.callback_query_handler(text = 'ctp')
async def process_callback_opendoor(callback_query: types.CallbackQuery):
    logging.info(f'Called pollice by @{callback_query.from_user.username} ({callback_query.from_user.full_name} chat: {callback_query.message.chat.title})')
    await callback_query.answer()
    if callPolice():
        await callback_query.message.reply('Тревожная кнопка успешно нажата.')
    else:
        await callback_query.message.reply('Тревожная кнопка не нажимается')

def callPolice():
    cnf = config['mqtt']
    try:
        cl = mqtt_client.Client(f'sos{random.random()}')
        cl.username_pw_set(cnf['login'], cnf['pass'])
        cl.connect(cnf['server'], 1883)
        return not cl.publish(cnf['topic']+'/in', '0')[0]
    except:
        return False


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp)


