# dormitory/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .utils import create_notification

# ==================== CONTRACT SIGNALS ====================

@receiver(post_save, sender='dormitory.Contract')
def notify_contract_created(sender, instance, created, **kwargs):
    """
    Tạo thông báo khi hợp đồng mới được tạo
    """
    if created:
        create_notification(
            user=instance.student.user,
            title="📄 Hợp đồng mới được tạo",
            message=f"Hợp đồng {instance.contract_number} cho phòng {instance.room.room_number} đã được tạo thành công. Ngày bắt đầu: {instance.start_date}",
            notification_type='contract',
            related_url=''
        )

@receiver(pre_save, sender='dormitory.Contract')
def notify_contract_expiring(sender, instance, **kwargs):
    """
    Kiểm tra hợp đồng sắp hết hạn (30 ngày trước khi hết hạn)
    """
    if instance.pk:  # Chỉ kiểm tra với instance đã tồn tại
        try:
            from .models import Contract
            old_instance = Contract.objects.get(pk=instance.pk)
            # Nếu end_date thay đổi và còn 30 ngày nữa là hết hạn
            if (old_instance.end_date != instance.end_date and 
                instance.end_date <= timezone.now().date() + timedelta(days=30)):
                create_notification(
                    user=instance.student.user,
                    title="⚠️ Hợp đồng sắp hết hạn",
                    message=f"Hợp đồng {instance.contract_number} sẽ hết hạn vào {instance.end_date}. Vui lòng gia hạn sớm!",
                    notification_type='warning',
                    related_url=''
                )
        except Exception:
            pass

# ==================== ROOM SIGNALS ====================

@receiver(post_save, sender='dormitory.Room')
def notify_room_status_change(sender, instance, **kwargs):
    """
    Thông báo khi trạng thái phòng thay đổi
    """
    if instance.pk:
        try:
            from .models import Room, Contract
            old_instance = Room.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Tìm tất cả sinh viên đang ở trong phòng này
                active_contracts = Contract.objects.filter(
                    room=instance, 
                    status='active'
                ).select_related('student__user')
                
                for contract in active_contracts:
                    create_notification(
                        user=contract.student.user,
                        title="🏠 Thay đổi trạng thái phòng",
                        message=f"Phòng {instance.room_number} đã chuyển sang trạng thái: {instance.get_status_display()}",
                        notification_type='info',
                        related_url=''
                    )
        except Exception:
            pass

# ==================== BOOKING SIGNALS ====================

def notify_room_booking_success(student, room):
    """
    Thông báo khi sinh viên đặt phòng thành công
    """
    create_notification(
        user=student.user,
        title="✅ Đặt phòng thành công",
        message=f"Bạn đã đặt phòng {room.room_number} thành công! Vui lòng hoàn tất thủ tục hợp đồng.",
        notification_type='success',
        related_url=''
    )