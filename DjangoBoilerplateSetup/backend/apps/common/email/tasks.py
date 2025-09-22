from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger('api_errors')


@shared_task
def send_email_task(subject, recipient_list, template_name, context=None):
    """
    Universal Celery task to send any email with HTML template.
    
    Usage:
        send_email_task.delay(
            subject='Welcome!',
            recipient_list=['user@example.com'],
            template_name='emails/welcome.html',
            context={'user_name': 'John', 'app_name': 'CSR Matchmaking'}
        )
        
        send_email_task.delay(
            subject='Password Reset',
            recipient_list=['user@example.com'],
            template_name='emails/password_reset.html',
            context={'user_name': 'John', 'reset_link': 'https://...'}
        )
    """
    try:
        html_content = render_to_string(template_name, context or {})
        text_content = "Please view this email in an HTML-capable email client."
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        
        msg.attach_alternative(html_content, "text/html")
        
        msg.send()
        
        logger.info(f"Email sent successfully to {recipient_list}")
        return f"Email sent to {recipient_list}"
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return f"Email failed to send to {recipient_list}: {str(e)}"
