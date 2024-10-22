from django.core.management.base import BaseCommand
from mentor.models import MentorshipData
from django.utils import timezone

class Command(BaseCommand):
    help = 'Update batch information for existing students'

    def handle(self, *args, **options):
        current_year = timezone.now().year

        # Update SE students (batch of 2027)
        MentorshipData.objects.filter(year='SE').update(batch=current_year + 3)

        # Update TE students (batch of 2026)
        MentorshipData.objects.filter(year='TE').update(batch=current_year + 2)

        # Update BE students (batch of 2025)
        MentorshipData.objects.filter(year='BE').update(batch=current_year + 1)

        self.stdout.write(self.style.SUCCESS('Successfully updated student batches'))
