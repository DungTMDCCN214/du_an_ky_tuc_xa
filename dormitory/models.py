# dormitory/models.py
from django.db import models
from accounts.models import CustomUser

class Building(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    total_floors = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class RoomType(models.Model):
    name = models.CharField(max_length=100)  # Phòng đơn, đôi, tập thể
    capacity = models.IntegerField()
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.capacity} người"

class Room(models.Model):
    room_number = models.CharField(max_length=10)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    floor = models.IntegerField()
    status_choices = (
        ('available', 'Còn trống'),
        ('occupied', 'Đã thuê'),
        ('maintenance', 'Bảo trì'),
    )
    status = models.CharField(max_length=20, choices=status_choices, default='available')
    current_occupancy = models.IntegerField(default=0) 
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['building', 'room_number']
    def is_available(self):
        """Kiểm tra phòng còn chỗ trống không"""
        return self.current_occupancy < self.room_type.capacity and self.status == 'available'
    def get_available_slots(self):
        """Lấy số chỗ trống còn lại"""
        return self.room_type.capacity - self.current_occupancy
    def __str__(self):
        return f"{self.building.name} - Phòng {self.room_number}"

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    university = models.CharField(max_length=200)
    faculty = models.CharField(max_length=100)
    course = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

class Contract(models.Model):
    contract_number = models.CharField(max_length=20, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    status_choices = (
        ('active', 'Đang hoạt động'),
        ('expired', 'Đã hết hạn'),
        ('terminated', 'Đã chấm dứt'),
    )
    status = models.CharField(max_length=20, choices=status_choices, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.contract_number} - {self.student}"
    

    # dormitory/models.py - THÊM CUỐI FILE, TRƯỚC các signals

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', '📢 Thông tin'),
        ('success', '✅ Thành công'), 
        ('warning', '⚠️ Cảnh báo'),
        ('error', '❌ Lỗi'),
        ('payment', '💳 Thanh toán'),
        ('contract', '📄 Hợp đồng'),
        ('maintenance', '🔧 Bảo trì'),
        ('booking', '🏠 Đặt phòng'),
    )
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name="Người dùng"
    )
    title = models.CharField(
        max_length=200, 
        verbose_name="Tiêu đề"
    )
    message = models.TextField(
        verbose_name="Nội dung"
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='info',
        verbose_name="Loại thông báo"
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="Đã đọc"
    )
    related_url = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name="URL liên quan"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Đánh dấu đã đọc"""
        self.is_read = True
        self.save()
    
    def get_icon(self):
        """Lấy icon tương ứng với loại thông báo"""
        icons = {
            'info': '📢',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌', 
            'payment': '💳',
            'contract': '📄',
            'maintenance': '🔧',
            'booking': '🏠',
        }
        return icons.get(self.notification_type, '📢')