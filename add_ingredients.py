import os
import csv
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'foodgram.settings'
django.setup()
from recipes.models import Ingredient


def upload_ingedients(csv_file='ingredients.csv'):
    '''Заливаем данные из файла ingredients.csv в Таблицу Ingredient
       Делим строку по символу ','. Присваиваем сзначения полям таблицы
       name и units соответственно.Если после запятой пустая строка - ставим 'г'.Можете поменять это поведение.
       Загружаем все данные в одном запросе методом bulk_create.
    '''
    old_data = Ingredient.objects.all()
    old_data.delete()
    data = csv.reader(open(csv_file, encoding='utf-8'), delimiter = ',')
    try:
        obj_list = [
            Ingredient( 
                id = id,
                title = row[0],
                dimension = 'г' if row[1] == '' else row[1],
            )
            for id, row in enumerate(data)
        ]
    except (IndexError):
        return 'IndexError'

    Ingredient.objects.bulk_create(obj_list)

    return 'ok'


if __name__=='__main__':
    print(upload_ingedients())