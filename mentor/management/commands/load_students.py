from django.core.management.base import BaseCommand
import csv
from mentor.models import Student

class Command(BaseCommand):
    help = 'Load student data from CSV into the database'

    def handle(self, *args, **kwargs):
        file_path = 'static/STUDENT_MENTOR_LIST.csv'  # Update this path
        
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Student.objects.create(
                    name=row['Name'],
                    year=row['Year'],
                    semester=row['Sem'],
                    roll_number=row['Roll Number'],
                    branch=row['Branch'],
                    division=row['Div'],
                    gender=row['Gender']
                )
        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))