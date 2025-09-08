"""
Notification channels implementation.
"""
import requests
import logging
import urllib3
from typing import Dict, Any
from django.conf import settings
from django.core.mail import send_mail
from core.patterns import NotificationChannel, NotificationChannelFactory, CircuitBreaker
import time

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class TelegramChannel(NotificationChannel):
    """Telegram notification channel implementation."""
    
    def __init__(self):
        self.bot_token = settings.NOTIFICATION_CONFIG['TELEGRAM']['BOT_TOKEN']
        self.default_chat_id = settings.NOTIFICATION_CONFIG['TELEGRAM']['DEFAULT_CHAT_ID']
        self.timeout = settings.NOTIFICATION_CONFIG['TELEGRAM']['TIMEOUT']
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=300)
    
    def send(self, message: str, recipient: str, **kwargs) -> bool:
        """Send Telegram message."""
        try:
            return self.circuit_breaker.call(self._send_telegram_message, message, recipient, **kwargs)
        except Exception as e:
            logger.error(f"Telegram notification failed: {str(e)}")
            return False
    
    def _send_telegram_message(self, message: str, recipient: str, **kwargs) -> bool:
        """Internal method to send Telegram message."""
        if not self.bot_token:
            raise ValueError("Telegram bot token not configured")
        
        chat_id = recipient or self.default_chat_id
        if not chat_id:
            raise ValueError("No Telegram chat ID provided")
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': kwargs.get('parse_mode', 'HTML'),
            'disable_web_page_preview': kwargs.get('disable_preview', True),
        }
        
        # Add reply markup if provided
        if 'reply_markup' in kwargs:
            payload['reply_markup'] = kwargs['reply_markup']
        
        response = requests.post(url, json=payload, timeout=self.timeout, verify=False)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            logger.info(f"Telegram message sent successfully to {chat_id}")
            return True
        else:
            logger.error(f"Telegram API error: {result.get('description', 'Unknown error')}")
            return False
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate Telegram chat ID format."""
        if not recipient:
            return bool(self.default_chat_id)
        
        # Telegram chat IDs can be numeric or start with @
        return (recipient.startswith('@') and len(recipient) > 1) or recipient.isdigit() or recipient.startswith('-')


class EmailChannel(NotificationChannel):
    """Email notification channel implementation."""
    
    def __init__(self):
        self.timeout = settings.NOTIFICATION_CONFIG['EMAIL']['TIMEOUT']
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=300)
    
    def send(self, message: str, recipient: str, **kwargs) -> bool:
        """Send email notification."""
        try:
            return self.circuit_breaker.call(self._send_email, message, recipient, **kwargs)
        except Exception as e:
            logger.error(f"Email notification failed: {str(e)}")
            return False
    
    def _send_email(self, message: str, recipient: str, **kwargs) -> bool:
        """Internal method to send email."""
        if not recipient:
            raise ValueError("No email recipient provided")
        
        subject = kwargs.get('subject', 'Notification')
        from_email = kwargs.get('from_email', settings.DEFAULT_FROM_EMAIL)
        html_message = kwargs.get('html_message')
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            raise
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate email address format."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, recipient))


def register_channels():
    """Register all notification channels with the factory."""
    factory = NotificationChannelFactory()
    
    factory.register_channel('telegram', TelegramChannel)
    factory.register_channel('email', EmailChannel)
    
    logger.info("Notification channels registered successfully")
