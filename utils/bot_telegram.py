import configparser
import redis
from aiogram import Bot, Dispatcher, executor, types
import bot_common
config = configparser.ConfigParser()
config.read('bot.ini')
TOKEN = config["bot"]["tg_token"]
issues_link = "https://www.ava.online/"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
r = redis.Redis(decode_responses=True)


@dp.message_handler(commands=["start", "pomoc"])
async def send_welcome(message: types.Message):
    await message.reply("Witaj! Jestem AvaBot! "
                        "Tutaj założysz swoje konto :) "
                        "Pamiętaj, aby z nikim nie dzielić się swoim hasłem!\n"
                        "Aby się zarejestrować, użyj komendy /rejestracja\n"
                        "Aby potem zmienić swoje hasło, użyj - /zmiana_hasła \n""Aby zresetować swoje konto, użyj - "
                        f"/reset\n Wszelkie błędy możesz zgłaszać tutaj: {issues_link}\n"
                        "Miłej gry! :)")


@dp.message_handler(commands=["rejestracja"])
async def password(message: types.Message):
    passwd = r.get(f"tg:{message.from_user.id}")
    if passwd:
        uid = r.get(f"auth:{passwd}")
    else:
        uid, passwd = bot_common.new_account(r)
        r.set(f"tg:{message.from_user.id}", passwd)
    await message.reply(f"Twoje ID logowania: {uid}\nTwoje tymczasowe hasło: {passwd}")


@dp.message_handler(commands=["zmiana_hasła"])
async def change_password(message: types.Message):
    passwd = r.get(f"tg:{message.from_user.id}")
    if not passwd:
        return await message.reply("Nie udało się zmienić hasła. Format komendy do zmiany hasła: /zmiana_hasła TU WPISZ NOWE HASŁO")
    while True:
        new_passwd = bot_common.random_string()
        if r.get(f"auth:{new_passwd}"):
            continue
        break
    uid = r.get(f"auth:{passwd}")
    r.delete(f"auth:{passwd}")
    r.set(f"auth:{new_passwd}", uid)
    r.set(f"tg:{message.from_user.id}", new_passwd)
    await message.reply(f"Twoje nowe hasło: {new_passwd}")


@dp.message_handler(commands=["reset"])
async def reset(message: types.Message):
    passwd = r.get(f"tg:{message.from_user.id}")
    if not passwd:
        return await message.reply("Nie możesz zresetować konta, gdyż go jeszcze nie stworzyłeś. Utwórz je używając komendy /rejestracja")
    uid = r.get(f"auth:{passwd}")
    bot_common.reset_account(r, uid)
    await message.reply(f"Konto zostało zresetowane.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
