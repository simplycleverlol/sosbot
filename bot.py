for i in range(2):
    try:
        import os, sys, json, logging, random
        from datetime import datetime as dt
        from aiogram import Bot, Dispatcher, executor, types
        from paho.mqtt import client as mqtt_client
        break
    except ModuleNotFoundError as e:
        print(e)
        os.system(sys.executable + ' -m pip install paho.mqtt aiogram')


logging.basicConfig(level=logging.INFO, 
                    filename = f'soslog-{dt.now().year}-{dt.now().month}.log',
                    format='%(asctime)s %(levelname)s: %(message)s',
                    encoding='utf-8')

class storage(dict):
    def __init__(self, name : str):
        TEMPLATEVAL = {'chats': [], 'master': None,
                        'api': '', 'secret': 'GoodWin',
                        'mqtt':{
                            'server': '127.0.0.1', 
                            'login' : None, 
                            'pass': None,
                            'topic':''
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

config = storage('cnf.json')

bot = Bot(token=config['api'])
dp = Dispatcher(bot)
inline_ctp = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Вызов Росгвардии', callback_data="ctp"))
cl = mqtt_client.Client(f'sos{random.random()}')
cl.username_pw_set(config['mqtt']['login'], config['mqtt']['pass'])


def bins(a, x):
    l, r = -1, len(a)
    while r-l > 1:
        m = (r+l)//2
        if a[m] < x:
            l = m
        else: r = m
    return r
def findc(l, c):
    p = bins(l, c)
    return p if p < len(l) and l[p] == c else -1

def checkc(c):
    return findc(config['chats'], c) != -1

def addc(c):
    global config
    l = config['chats']
    x = findc(l, c)
    if x == -1:
        l.append(c)
        l.sort()

def remc(c):
    global config
    l = config['chats']
    x = findc(l, c)
    if x != -1:
        l.pop(x)


def msginfo(m, chat = None):
    if chat is None:
        chat = m.chat
    try:
        return f'User: @{m.from_user.username} #{m.from_user.id} "{m.from_user.full_name}" Chat: #{chat.id} "{chat.title}"'
    except:
        try:
            return f'User: @{m.from_user.username} #{m.from_user.id} "{m.from_user.full_name}"'
        except:
            return f'User: #{m.from_user.id}'


def fsos(mtext):
    mtext = mtext.text.lower().split()
    return any(word in mtext for word in ['sos', 'омон', 'тревога']) or mtext == ['!']


@dp.message_handler(fsos)
async def regularmsg(message: types.Message):
    if checkc(message.chat.id):
        logging.info(f'Alarm msg received: {msginfo(message)}') 
        await message.reply('Необходима помощь?', reply_markup=inline_ctp)

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer("""
Данный бот позволяет активировать тревожную кнопку в коворкинге на мясницкой.
Добавьте его в рабочий чат, или напишите в личные сообщения.
Реагирует на сообщения, содержащие sos, тревога или омон
    """)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    logging.info(f'Start msg received: {msginfo(message)}') 
    if checkc(message.chat.id):
        await message.reply("Сервис активен")
    else:    await message.reply("Для активации отправьте кодовое слово ответным сообщением")

@dp.message_handler(commands=['stop'])
async def send_unwelcome(message: types.Message):
    logging.info(f'Stop msg received: {msginfo(message)}') 
    if checkc(message.chat.id):
        remc(message.chat.id)
        config.save()
        await message.reply('Успешно отключено')
    else:    await message.reply("Сервис не активен")

@dp.message_handler(text = config['secret'])
async def activate(message: types.Message):
    logging.info(f'Secret msg received: {msginfo(message)}') 
    if checkc(message.chat.id):
        await message.reply('Уже активно')
    else:
        addc(message.chat.id)
        config.save()
        logging.info(f'Activation for chat #{message.chat.id} : {message.chat.title} by {message.from_user.id} : {message.from_user.full_name}')
        await message.reply("Бот активирован!")


@dp.callback_query_handler(text = 'ctp')
async def process_callback_opendoor(callback_query: types.CallbackQuery):
    logging.warning(f'Called pollice by {msginfo(callback_query, callback_query.message.chat)})')
    await callback_query.answer()
    if callPolice():
        await callback_query.message.reply('Тревожная кнопка успешно нажата.')
    else:
        await callback_query.message.reply('Тревожная кнопка не нажимается')

def callPolice():
    cnf = config['mqtt']
    try:
        cl.reconnect()
        return not cl.publish(cnf['topic']+'/in', 'sos')[0]
    except Exception as e:
        logging.critical(e)
        return False




if __name__ == "__main__":
    # Запуск бота
    cl.connect(config['mqtt']['server'], 1883)
    executor.start_polling(dp)


