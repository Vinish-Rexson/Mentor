from django.core.management.base import BaseCommand
import csv
from mentor.models import Student

class Command(BaseCommand):
    help = 'Load student data from CSV into the database'

    def handle(self, *args, **kwargs):
        file_path = 'static/marksheet.csv'  # Update this path
        
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Student.objects.create(
                    name=row['Name'],
                    gender=row['Gender'],
                    age=row['Age'],
                    section=row['Section'],
                    science_marks=row['Science'],
                    english_marks=row['English'],
                    history_marks=row['History'],
                    maths_marks=row['Maths']
                )
        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))
