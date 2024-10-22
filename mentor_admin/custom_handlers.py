import logging
import traceback
from django.utils.log import AdminEmailHandler
from django.conf import settings
from django.template.loader import render_to_string

class CustomAdminEmailHandler(AdminEmailHandler):
    def handle(self, record):
        self.request = record.request  # Save the request object
        super().handle(record)

    def send_mail(self, subject, message, *args, **kwargs):
        # Prepare the context for the HTML template
        context = {
            'error_message': message,
            'request_method': self.request.method,
            'request_path': self.request.path,
            'user': self.request.user if self.request.user.is_authenticated else 'Anonymous',
            'traceback': traceback.format_exc(),
            'debug_mode': settings.DEBUG,
        }

        # Render the HTML template with the context
        html_message = render_to_string('error_email_template.html', context)

        # Update kwargs with the HTML message
        kwargs['html_message'] = html_message

        # Call the parent class's send_mail method with all arguments
        super().send_mail(subject, message, *args, **kwargs)
