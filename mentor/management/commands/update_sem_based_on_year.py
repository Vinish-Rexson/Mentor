from django.core.management.base import BaseCommand
from mentor.models import MentorshipData

class Command(BaseCommand):
    help = "Update sem based on year for preloaded data"

    def handle(self, *args, **kwargs):
        records_updated = 0
        for mentorship_data in MentorshipData.objects.all():
            if mentorship_data.year:
                previous_sem = mentorship_data.sem
                mentorship_data.set_sem_based_on_year()  # This will set sem based on year
                if previous_sem != mentorship_data.sem:
                    mentorship_data.save()  # Save only if sem has changed
                    records_updated += 1
        self.stdout.write(self.style.SUCCESS(f'Updated {records_updated} records'))
