import aysinco 
import requests
import random
import time
import aiogram
from faker import Faker
from aiogram.types import InputFile
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import live

fake = Faker()

def luhn_algorithm(card_number):
    digits = [int(digit) for digit in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0

async def send_messages():
    # Inicia el bot
    bot = aiogram.Bot(token='6914089102:AAG4FD04B0EPjTBcjQiYA838s4ZEUciVDKM')
    chat_id = -1002086823988

    # Lee el archivo de texto
    with open('cards.txt') as file:
        lines = file.readlines()

    # Configuración de límite y pausa
    requests_limit = 1  # Número de solicitudes por cada pausa larga
    pause_duration = 1  # Duración de la pausa larga en segundos

    # Itera sobre las líneas del archivo de texto y envía cada mensaje al canal
    for i, line in enumerate(lines, start=1):
        # Elimina los últimos 4 dígitos del número de tarjeta
        linea = line[:28]
        card_number = line[:12]

        # Verifica si la tarjeta es válida usando el algoritmo de Luhn
        if not luhn_algorithm(card_number):
            print(f"Tarjeta inválida en la posición {i}: {linea}")
            continue

        # Verifica el bin de la tarjeta
        BIN = card_number[:6]
        req = requests.get(f"https://bins.antipublic.cc/bins/{BIN}").json()

        # Manejo del error si la clave 'brand' no está presente
        try:
            brand = req['brand']
        except KeyError:
            print("La clave 'brand' no está presente en la respuesta JSON. Se omitirá esta entrada.")
            continue

        # Capturando los valores de la respuesta JSON
        country = req['country']
        country_name = req['country_name']
        country_flag = req['country_flag']
        country_currencies = req['country_currencies']
        bank = req['bank']
        level = req['level']
        typea = req['type']

        # Genera una fecha aleatoria en el rango de los últimos 5 años
        month = str(random.randint(1, 12)).zfill(2)

        # Genera un año aleatorio de dos dígitos (entre 22 y 29)
        year = str(random.randint(24, 32)).zfill(2)

        # Genera un nombre aleatorio
        full_name = fake.name()

        # Genera una dirección aleatoria
        address = fake.address()

        # Ruta de la foto que deseas enviar
        photo_path = "scrap.jpg"

        # Carga la foto utilizando InputFile
        photo = InputFile(photo_path)

        button_consultas = InlineKeyboardButton("CONSULTAS", url="https://t.me/+IFKDiAO_wDU1ZWMx")
        # Agrega los botones a una lista
        keyboard = [[button_consultas]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        message = ""
        message += f"\n"
        message += f" HirsuiteScrapper V2.1 🐍"
        message += "━━━━━━━━━━━━━━\n"
        message += f"<b>⌖ 𝗖𝗰 ⤳</b> <code>{linea}</code>\n"
        message += f"⌖ 𝗦𝘁𝗮𝘁𝘂𝘀 ⤳ 𝙏𝘼𝙍𝙅𝙀𝙏𝘼 𝙑𝘼𝙇𝙄𝘿𝘼! ✅\n"
        message += f"⌖ 𝗕𝗶𝗻 ⤳ #Bin{BIN}\n"
        message += "━━━━━━━━━━━━━━\n"
        message += f"<b>⌮ 𝗜𝗻𝗳𝗼 ⤳ </b>  <code>{brand}-{typea}-{level}</code>\n"
        message += f"<b>⌮ 𝗕𝗮𝗻𝗰𝗼 ⤳ </b>  <code>{bank}</code>\n"
        message += f"<b>⌮ 𝗣𝗮𝗶𝘀 ⤳ </b>  <code>{country_name} [{country_flag}]</code>\n"
        message += "━━━━━━━━━━━━━━\n"
        message += f"<b>⌮ 𝐄𝐱𝐭𝐫𝐚 ⤳ </b>  <code>{card_number}xxxx|{month}|{year}|rnd</code>\n"
        message += f"⌖  Realizado por ⤳ HirsuiteCobra\n"
        message += "━━━━━━━━━━━━━━\n"


        # Envía el mensaje al canal con parse_mode='HTML'
        try:
            await bot.send_photo(chat_id, photo, caption=message, reply_markup=reply_markup, parse_mode='HTML')
        except Exception as e:
            print(f"Error al enviar el mensaje: {e}")

        # Verifica si se alcanzó el límite de solicitudes
        if i % requests_limit == 0 and i != len(lines):
            print(f"Se ha alcanzado el límite de solicitudes. Se realizará una pausa de {pause_duration} segundos.")
            time.sleep(pause_duration)

live()
if __name__ == '__main__':
  asyncio.run(send_messages())
