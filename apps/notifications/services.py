"""
Notification services for the notification system.
"""
import logging
from typing import Dict, Any, Optional, List
from django.template import Template, Context
from django.utils import timezone
from .models import Notification, NotificationTemplate, NotificationLog
from .channels import NotificationChannelFactory

logger = logging.getLogger(__name__)


class NotificationService:
    """Service class for handling notification operations."""
    
    def __init__(self):
        self.channel_factory = NotificationChannelFactory()
    
    def create_notification(
        self,
        template_name: str,
        recipient: str,
        customer=None,
        order=None,
        context: Dict[str, Any] = None,
        priority: str = 'normal',
        scheduled_at: Optional[timezone.datetime] = None
    ) -> Optional[Notification]:
        """
        Create a new notification.
        """
        try:
            template = NotificationTemplate.objects.get(name=template_name, is_active=True)
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Notification template '{template_name}' not found")
            return None
        
        # Validate recipient for the channel
        channel = self.channel_factory.create_channel(template.channel)
        if not channel or not channel.validate_recipient(recipient):
            logger.error(f"Invalid recipient '{recipient}' for channel '{template.channel}'")
            return None
        
        # Render message from template
        context_data = context or {}
        subject = self._render_template(template.subject_template, context_data)
        message = self._render_template(template.body_template, context_data)
        
        # Create notification
        notification = Notification.objects.create(
            template=template,
            recipient=recipient,
            subject=subject,
            message=message,
            priority=priority,
            scheduled_at=scheduled_at or timezone.now(),
            customer=customer,
            order=order,
            context_data=context_data
        )
        
        logger.info(f"Created notification {notification.id} for {recipient}")
        return notification
    
    def send_notification(self, notification: Notification) -> bool:
        """
        Send a notification using the appropriate channel.
        """
        channel = self.channel_factory.create_channel(notification.template.channel)
        if not channel:
            error_msg = f"Channel '{notification.template.channel}' not available"
            self._log_notification_attempt(notification, 'failed', error_message=error_msg)
            return False
        
        try:
            # Prepare channel-specific kwargs
            kwargs = self._prepare_channel_kwargs(notification)
            
            # Send notification
            success = channel.send(notification.message, notification.recipient, **kwargs)
            
            # Log the attempt
            status = 'sent' if success else 'failed'
            self._log_notification_attempt(notification, status)
            
            return success
            
        except Exception as e:
            error_msg = f"Error sending notification: {str(e)}"
            logger.error(error_msg)
            self._log_notification_attempt(notification, 'failed', error_message=error_msg)
            return False
    
    def send_bulk_notifications(
        self,
        template_name: str,
        recipients: List[Dict[str, Any]],
        context: Dict[str, Any] = None,
        priority: str = 'normal'
    ) -> List[Notification]:
        """
        Create and send multiple notifications.
        """
        notifications = []
        
        for recipient_data in recipients:
            recipient = recipient_data.get('recipient')
            customer = recipient_data.get('customer')
            order = recipient_data.get('order')
            
            # Merge global context with recipient-specific context
            merged_context = {**(context or {}), **recipient_data.get('context', {})}
            
            notification = self.create_notification(
                template_name=template_name,
                recipient=recipient,
                customer=customer,
                order=order,
                context=merged_context,
                priority=priority
            )
            
            if notification:
                notifications.append(notification)
        
        return notifications
    
    def _render_template(self, template_string: str, context_data: Dict[str, Any]) -> str:
        """
        Render Django template string with context data.
        """
        if not template_string:
            return ""
        
        try:
            template = Template(template_string)
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            return template_string
    
    def _prepare_channel_kwargs(self, notification: Notification) -> Dict[str, Any]:
        """
        Prepare channel-specific keyword arguments.
        """
        kwargs = {}
        
        if notification.template.channel == 'email':
            kwargs['subject'] = notification.subject
            kwargs['html_message'] = notification.context_data.get('html_message')
        elif notification.template.channel == 'telegram':
            kwargs['parse_mode'] = notification.context_data.get('parse_mode', 'HTML')
            kwargs['disable_preview'] = notification.context_data.get('disable_preview', True)
        
        return kwargs
    
    def _log_notification_attempt(
        self,
        notification: Notification,
        status: str,
        response_data: Dict[str, Any] = None,
        error_message: str = None
    ):
        """
        Log notification delivery attempt.
        """
        NotificationLog.objects.create(
            notification=notification,
            attempt_number=notification.retry_count + 1,
            status=status,
            response_data=response_data or {},
            error_message=error_message or ''
        )


class TemplateService:
    """Service class for managing notification templates."""
    
    @staticmethod
    def create_template(
        name: str,
        channel: str,
        subject_template: str,
        body_template: str
    ) -> NotificationTemplate:
        """Create a new notification template."""
        template = NotificationTemplate.objects.create(
            name=name,
            channel=channel,
            subject_template=subject_template,
            body_template=body_template
        )
        logger.info(f"Created notification template: {name}")
        return template
    
    @staticmethod
    def get_template(name: str) -> Optional[NotificationTemplate]:
        """Get a notification template by name."""
        try:
            return NotificationTemplate.objects.get(name=name, is_active=True)
        except NotificationTemplate.DoesNotExist:
            return None
    
    @staticmethod
    def update_template(
        name: str,
        subject_template: str = None,
        body_template: str = None
    ) -> bool:
        """Update an existing notification template."""
        try:
            template = NotificationTemplate.objects.get(name=name)
            if subject_template is not None:
                template.subject_template = subject_template
            if body_template is not None:
                template.body_template = body_template
            template.save()
            logger.info(f"Updated notification template: {name}")
            return True
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Template '{name}' not found")
            return False


class NotificationAnalyticsService:
    """Service class for notification analytics and reporting."""
    
    @staticmethod
    def get_delivery_statistics(days: int = 7) -> Dict[str, Any]:
        """Get notification delivery statistics."""
        from django.db.models import Count, Q
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        notifications = Notification.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        stats = notifications.aggregate(
            total=Count('id'),
            sent=Count('id', filter=Q(status='sent')),
            delivered=Count('id', filter=Q(status='delivered')),
            failed=Count('id', filter=Q(status='failed')),
            pending=Count('id', filter=Q(status='pending')),
        )
        
        # Calculate success rate
        total = stats['total']
        if total > 0:
            stats['success_rate'] = (stats['sent'] + stats['delivered']) / total * 100
        else:
            stats['success_rate'] = 0
        
        # Get channel breakdown
        channel_stats = notifications.values('template__channel').annotate(
            count=Count('id')
        ).order_by('-count')
        
        stats['by_channel'] = list(channel_stats)
        
        return stats
    
    @staticmethod
    def get_customer_notification_history(customer_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get notification history for a specific customer."""
        notifications = Notification.objects.filter(
            customer_id=customer_id
        ).select_related('template').order_by('-created_at')[:limit]
        
        history = []
        for notification in notifications:
            history.append({
                'id': str(notification.id),
                'template': notification.template.name,
                'channel': notification.template.channel,
                'status': notification.status,
                'created_at': notification.created_at,
                'sent_at': notification.sent_at,
                'delivered_at': notification.delivered_at,
            })
        
        return history
