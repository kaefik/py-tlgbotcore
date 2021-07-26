"""
реализация БД с помощью CSV файлов.

каждый файл это таблица, папка символизирует БД
"""
import os
import shutil
import csv


class CSVDB:

    def __init__(self, name_db='test_db', force=False):
        """
        инициализация БД
        force - если True, то создаем БД заново, удаляем старую
        """
        self.name_db = name_db  # название БД
        self.tables = []  # файлы таблиц

        if os.path.exists(self.name_db):
            print("папка БД существует")
            if force:
                print("Удаляем папку БД")
                shutil.rmtree(self.name_db)
            else:
                return
        else:
            print("папки БД нет.")

        print("Создаем папку БД")
        os.mkdir(self.name_db)

    def create_table(self, name_table='NonameTable', colums=['col1', 'col2']):
        """
        создание таблицы в БД, проверяется есть ли файл
        сым файл разделен ;
        return: True - если успешно создан файл таблицы, иначе False
        """
        full_path = f"{self.name_db}/{name_table}.csv"
        if os.path.exists(full_path):
            return False

        with open(full_path, mode="w", encoding='utf-8') as w_file:
            file_writer = csv.DictWriter(w_file, delimiter=";", fieldnames=colums)
            file_writer.writeheader()
            # file_writer.writerow('')

        self.tables.append(name_table)
