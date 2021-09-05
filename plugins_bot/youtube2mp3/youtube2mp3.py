"""
Youtube video to mp3 file.
"""
# установка зависимостей
# sudo -H pip3 install --upgrade youtube-dl
# apt install mp3splt


import asyncio
from telethon import events
import re

from tlgbotcore.i_utils import run_cmd

rexp_http_url = r"https?:\/\/(www\.)?((youtu.be)|(youtube.com))*\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
path_mp3 = "mp3"


# получение урл
@tlgbot.on(events.NewMessage(pattern=r".*\n*" + rexp_http_url))
async def get_mp3_from_youtube(event):
    tlgbot._logger.info("get_mp3_from_youtube start subprocess begin")

    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    # if not is_allow_user(sender_id, settings.get_all_user()):
    #     await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
    #                         f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
    #     return
    # END проверка на право доступа к боту

    # chat = await event.get_input_chat()
    sender = await event.get_sender()
    sender_id = sender.id

    # current_user = settings.get_user(sender_id)

    # buttons = await event.get_buttons()
    # print(sender.id)
    user_folder = str(sender.id)
    # print(event.raw_text)
    # выделение урл из общей массы сообщения
    match = re.search(rexp_http_url, event.raw_text)
    url_youtube = match.group()
    # print(url_youtube)

    await event.respond("Начало конвертации ютуб клипа в mp3...")
    # print("get_mp3_from_youtube start subprocess begin")
    cmds = f'youtube-dl --extract-audio --audio-format mp3 ' \
           f'--output "{path_mp3}/{user_folder}/%(title)s.%(ext)s" {url_youtube}'
    # print(cmds)

    done, _ = await asyncio.wait([run_cmd(cmds)])

    # result - результат выполнения команды cmds
    # error - ошибка, если команда cmds завершилась с ошибкой
    # code - код работы команды, если 0 , то команда прошла без ошибок
    result, error, code = done.pop().result()

    if code != 0:
        await event.respond(f"!!!! код: {code} \n" \
                            f"Внутренняя ошибка: {error}")
        return

    result = result.decode("utf-8")
    str_result = result.split("\n")
    str_search = "[ffmpeg] Destination:"
    file_mp3 = ""
    for s in str_result:
        if str_search in s:
            file_mp3 = s[len(str_search):].strip()
            break

    await event.respond("mp3 файл скачан...будем делить на части")
    # деление mp3 файла на части, если нужно с помощью команды mp3splt
    timesplit = "59.0"  # длительность каждой части формат: минуты.секунда
    cmds2 = f'mp3splt -t {timesplit} "{file_mp3}"'

    # print(cmds)

    done2, _ = await asyncio.wait([
        run_cmd(cmds2)
    ])

    # result - результат выполнения команды cmds
    # error - ошибка, если команда cmds завершилась с ошибкой
    # code - код работы команды, если 0 , то команда прошла без ошибок
    result2, error2, code2 = done2.pop().result()

    if code2 != 0:
        await event.respond(f"!!!! код: {code2} \n" \
                            f"Внутреняя ошибка: {error2}")
        return

    result2 = result2.decode("utf-8")
    str_result2 = result2.split("\n")
    str_search2 = "File"
    files_mp3 = []
    for s in str_result2:
        if str_search2 in s:
            ss = s[s.index('"') + 1:]
            files_mp3.append(ss[:ss.index('"')].strip())

    try:
        await event.respond(f"Результат конвертации:")
        for el in files_mp3:
            await event.respond(file=el)

    except FileNotFoundError:
        await event.respond(f"Вывод результат команды {cmds}:\n {result}")
        await event.respond("Внутренняя ошибка: или урл не доступен, "
                            "или конвертация невозможна.\n"
                            "Попробуйте позже или другую ссылку.")
    except Exception as err:
        # print("!!!! Внутренняя ошибка: ", err)
        await event.respond(f"!!!! Внутренняя ошибка: {err}")
    # END сделать конвертирование в mp3
    await event.respond("Конец конвертации!")


@tlgbot.on(events.NewMessage(pattern='/delfiles'))
async def clear_all_mp3(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    # if not is_allow_user(sender_id, settings.get_all_user()):
    #     await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
    #                         f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
    #     return
    # END проверка на право доступа к боту

    await event.respond("Очистка папки mp3 от файлов...")
    user_folder = str(sender.id)
    folder_mp3 = f"{path_mp3}/{user_folder}"

    done, pending = await asyncio.wait([
        run_cmd(f"ls {folder_mp3}")
    ])

    # result - результат выполнения команды cmds
    # error - ошибка, если команда cmds завершилась с ошибкой
    # code - код работы команды, если 0 , то команда прошла без ошибок
    result, error, code = done.pop().result()

    if code != 0:
        await event.respond(error.decode("utf8"))

    result = result.decode("utf8")
    if len(result) == 0:
        await event.respond("Файлов на удаления нет.")
        return
    # print("RESULT LS = ", result)
    # print("result = ", result)
    await event.respond(result)

    done, pending = await asyncio.wait([
        run_cmd(f"rm -f {folder_mp3}/*")
    ])

    result, error, code = done.pop().result()

    if code != 0:
        await event.respond(error.decode("utf8"))

    result = result.decode("utf8")
    # print("result = ", result)
    # await event.respond(result)

    await event.respond("Очистка завершена.")
