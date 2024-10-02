from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from ...models import MentorshipData


class Command(BaseCommand):
    help = 'Create users from faculty mentor data and assign Mentor role'

    def handle(self, *args, **kwargs):
        # Ensure the Mentor group exists
        mentor_group, created = Group.objects.get_or_create(name='Mentor')

        if created:
            self.stdout.write('Created Mentor group')
        
        # Loop through each record in MentorshipData
        for record in MentorshipData.objects.all():
            faculty_mentor_name = record.faculty_mentor
            
            # Create a unique username by removing spaces and using a suffix if necessary
            username = faculty_mentor_name.replace(' ', '_').lower()

            if not User.objects.filter(username=username).exists():
                # Generate a random password
                random_password = get_random_string(length=8)

                # Create the new user
                user = User.objects.create_user(
                    username=username,
                    password=random_password,
                    first_name=faculty_mentor_name.split()[0],
                    last_name=' '.join(faculty_mentor_name.split()[1:]),
                )

                # Assign the user to the Mentor group
                user.groups.add(mentor_group)

                # Save the user
                user.save()

                # Output to console
                self.stdout.write(f"Created user: {faculty_mentor_name} with username: {username}")
                
                # TODO: Send the password to the user via email (requires email setup)
            else:
                self.stdout.write(f"User {username} already exists")
