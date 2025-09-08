"""
Celery tasks for notification processing.
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.db import models
from .models import Notification, NotificationLog
from .channels import NotificationChannelFactory
from .services import NotificationService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_notification_task(self, notification_id):
    """
    Celery task to send individual notification.
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        service = NotificationService()
        
        # Update status to queued
        notification.status = 'queued'
        notification.save(update_fields=['status', 'updated_at'])
        
        # Attempt to send notification
        success = service.send_notification(notification)
        
        if success:
            notification.mark_as_sent()
            logger.info(f"Notification {notification_id} sent successfully")
        else:
            notification.mark_as_failed("Failed to send notification")
            logger.error(f"Failed to send notification {notification_id}")
            
            # Retry if possible
            if notification.can_retry():
                notification.increment_retry()
                # Schedule retry with exponential backoff
                countdown = 60 * (2 ** notification.retry_count)
                raise self.retry(countdown=countdown)
        
        return success
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return False
    except Exception as exc:
        logger.error(f"Error sending notification {notification_id}: {str(exc)}")
        
        # Update notification status
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.mark_as_failed(str(exc))
            
            if notification.can_retry():
                notification.increment_retry()
                countdown = 60 * (2 ** notification.retry_count)
                raise self.retry(exc=exc, countdown=countdown)
        except Notification.DoesNotExist:
            pass
        
        return False


@shared_task
def send_bulk_notifications_task(notification_ids):
    """
    Celery task to send multiple notifications.
    """
    results = []
    for notification_id in notification_ids:
        try:
            result = send_notification_task.delay(notification_id)
            results.append({
                'notification_id': notification_id,
                'task_id': result.id,
                'status': 'queued'
            })
        except Exception as e:
            logger.error(f"Failed to queue notification {notification_id}: {str(e)}")
            results.append({
                'notification_id': notification_id,
                'task_id': None,
                'status': 'failed',
                'error': str(e)
            })
    
    return results


@shared_task
def process_scheduled_notifications():
    """
    Celery task to process scheduled notifications.
    """
    current_time = timezone.now()
    
    # Get notifications that are scheduled to be sent
    scheduled_notifications = Notification.objects.filter(
        status='pending',
        scheduled_at__lte=current_time
    ).order_by('priority', 'scheduled_at')
    
    processed_count = 0
    
    for notification in scheduled_notifications:
        try:
            send_notification_task.delay(str(notification.id))
            processed_count += 1
            logger.info(f"Queued scheduled notification {notification.id}")
        except Exception as e:
            logger.error(f"Failed to queue scheduled notification {notification.id}: {str(e)}")
    
    logger.info(f"Processed {processed_count} scheduled notifications")
    return processed_count


@shared_task
def cleanup_old_notifications():
    """
    Celery task to cleanup old notification records.
    """
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    # Delete old delivered notifications
    deleted_notifications = Notification.objects.filter(
        status='delivered',
        delivered_at__lt=cutoff_date
    ).delete()
    
    # Delete old notification logs
    deleted_logs = NotificationLog.objects.filter(
        created_at__lt=cutoff_date
    ).delete()
    
    logger.info(f"Cleaned up {deleted_notifications[0]} notifications and {deleted_logs[0]} logs")
    
    return {
        'deleted_notifications': deleted_notifications[0],
        'deleted_logs': deleted_logs[0]
    }


@shared_task
def retry_failed_notifications():
    """
    Celery task to retry failed notifications that can be retried.
    """
    failed_notifications = Notification.objects.filter(
        status='failed',
        retry_count__lt=models.F('max_retries')
    )
    
    retried_count = 0
    
    for notification in failed_notifications:
        try:
            if notification.can_retry():
                send_notification_task.delay(str(notification.id))
                retried_count += 1
                logger.info(f"Retrying failed notification {notification.id}")
        except Exception as e:
            logger.error(f"Failed to retry notification {notification.id}: {str(e)}")
    
    logger.info(f"Retried {retried_count} failed notifications")
    return retried_count


@shared_task
def send_order_update_notification(order_id, old_status, new_status):
    """
    Celery task to send order update notifications.
    """
    try:
        from apps.orders.models import Order
        from apps.customers.models import Customer
        
        order = Order.objects.select_related('customer').get(id=order_id)
        customer = order.customer
        
        # Check customer notification preferences
        if hasattr(customer, 'notification_preferences'):
            preferences = customer.notification_preferences
            if not preferences.order_updates:
                logger.info(f"Order update notifications disabled for customer {customer.id}")
                return False
        
        service = NotificationService()
        
        # Create context for notification
        context = {
            'customer_name': customer.name,
            'order_id': order.order_number,
            'order_status': new_status,
            'old_status': old_status,
            'new_status': new_status,
            'status_change': f"{old_status} to {new_status}",
            'order_total': str(order.total_amount),
            'order_date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            # Add individual status fields for template access
            'status_change_old': old_status,
            'status_change_new': new_status,
        }
        
        # Send notifications based on customer preferences
        notifications_sent = []
        
        # Email notification
        if customer.email and (not hasattr(customer, 'notification_preferences') or 
                               customer.notification_preferences.email_enabled):
            email_notification = service.create_notification(
                template_name='order_update_email',
                recipient=customer.email,
                customer=customer,
                order=order,
                context=context
            )
            if email_notification:
                send_notification_task.delay(str(email_notification.id))
                notifications_sent.append('email')
        
        # Telegram notification
        if customer.telegram_chat_id and (not hasattr(customer, 'notification_preferences') or 
                                          customer.notification_preferences.telegram_enabled):
            telegram_notification = service.create_notification(
                template_name='order_update_telegram',
                recipient=customer.telegram_chat_id,
                customer=customer,
                order=order,
                context=context
            )
            if telegram_notification:
                send_notification_task.delay(str(telegram_notification.id))
                notifications_sent.append('telegram')
        
        logger.info(f"Order update notifications queued for order {order_id}: {notifications_sent}")
        return notifications_sent
        
    except Exception as e:
        logger.error(f"Failed to send order update notification for order {order_id}: {str(e)}")
        return False
