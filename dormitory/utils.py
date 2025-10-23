# dormitory/utils.py - TẠO FILE MỚI
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

def create_notification(user, title, message, notification_type='info', related_url=''):
    """
    Tạo thông báo mới
    
    Args:
        user: User object
        title: Tiêu đề thông báo
        message: Nội dung thông báo
        notification_type: Loại thông báo (info, success, warning, error, payment, contract, maintenance, booking)
        related_url: URL khi click vào thông báo
    """
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        related_url=related_url
    )
    return notification

def create_bulk_notification(users, title, message, notification_type='info', related_url=''):
    """
    Tạo thông báo hàng loạt cho nhiều user
    
    Args:
        users: Danh sách User objects
        title: Tiêu đề thông báo
        message: Nội dung thông báo
        notification_type: Loại thông báo
        related_url: URL khi click vào thông báo
    """
    notifications = []
    for user in users:
        notifications.append(
            Notification(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                related_url=related_url
            )
        )
    Notification.objects.bulk_create(notifications)
    return len(notifications)

def get_unread_count(user):
    """
    Lấy số thông báo chưa đọc của user
    
    Args:
        user: User object
    
    Returns:
        int: Số thông báo chưa đọc
    """
    return Notification.objects.filter(user=user, is_read=False).count()

def get_recent_notifications(user, limit=10):
    """
    Lấy danh sách thông báo gần đây
    
    Args:
        user: User object
        limit: Số lượng thông báo (mặc định: 10)
    
    Returns:
        QuerySet: Danh sách thông báo
    """
    return Notification.objects.filter(user=user).order_by('-created_at')[:limit]

def mark_all_as_read(user):
    """
    Đánh dấu tất cả thông báo là đã đọc
    
    Args:
        user: User object
    
    Returns:
        int: Số thông báo đã đánh dấu
    """
    updated = Notification.objects.filter(
        user=user, 
        is_read=False
    ).update(is_read=True)
    return updated