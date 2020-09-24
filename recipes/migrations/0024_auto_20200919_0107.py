from django.db import migrations
import os
import csv
from pathlib import Path


def get_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    
    csv_file=os.path.join('ingredients.csv')
    data = csv.reader(open(csv_file, encoding='utf-8'), delimiter = ',')
    try:
        obj_list = [
            Ingredient( 
                title=row[0],
                dimension='г' if row[1] == '' else row[1],
            )
            for row in list(data)
        ]
    except (IndexError):
        return 'IndexError'

    Ingredient.objects.bulk_create(obj_list)


def delete_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    Ingredient.objects.all().delete()



class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(get_ingredients, reverse_code=delete_ingredients),
    ]
