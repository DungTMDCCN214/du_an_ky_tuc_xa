from django.db import models
from dormitory.models import Contract, Student

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Tiền mặt'),
        ('bank_transfer', 'Chuyển khoản'),
        ('momo', 'Ví MoMo'),
        ('zalopay', 'ZaloPay'),
    )

    PAYMENT_CHOICES = (
        ('room', 'Tiền phòng'),
        ('electric', 'Tiền điện'),
        ('water', 'Tiền nước'),
    )

    STATUS_CHOICES = (
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('cancelled', 'Đã hủy'),
        ('failed', 'Thất bại'),
    )

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='room')
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Hóa đơn #{self.id} - {self.contract.student.student_id} - {self.amount:,.0f} VNĐ"
