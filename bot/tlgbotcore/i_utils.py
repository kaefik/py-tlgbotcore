"""
 my ulitites
 Author: Ilnur Sayfutdinov
 E-mail: ilnursoft@gmail.com
"""

import requests
import asyncio
import logging


# преобразование строки вида "SAMSUNG a50 64\\xd0\\xb3\\xd0\\xb1" в строку c кодировкой encoding
def string_escape(s, encoding="utf-8"):
    import codecs
    byte_s = bytes(s, encoding)
    res = codecs.escape_decode(byte_s)[0]
    res = res.decode(encoding)
    return res


# сохранить в файл html из urls
# True - если смогли получить данные с запроса и сохранить в файл
def savefile_from_url(urls=None, filename="test.html", timeout=10):
    if urls is None:
        return False
    session = requests.Session()
    try:
        r = session.get(urls, timeout=timeout)
        logging.info("GET %s -> %s", urls, r.status_code)
        if r.status_code == 200:
            html = r.text
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            return True
        return False
    except requests.RequestException as exc:
        logging.exception("Request failed: %s", exc)
        return False


# запуск команды cmd asyncio
async def run_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    logging.info("Command exited: %r -> %s", cmd, proc.returncode)
    if stdout:
        logging.debug("stdout: %s", stdout.decode(errors="replace"))
    if stderr:
        logging.debug("stderr: %s", stderr.decode(errors="replace"))

    return stdout, stderr, proc.returncode
