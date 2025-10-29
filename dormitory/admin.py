# dormitory/admin.py
from django.contrib import admin
from .models import Building, RoomType, Room, Student, Contract

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'total_floors']
    search_fields = ['name', 'address']

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'price_per_month']
    list_filter = ['capacity']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'building', 'room_type', 'floor', 'status']
    list_filter = ['building', 'floor', 'status']
    search_fields = ['room_number']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'university', 'faculty']
    search_fields = ['student_id', 'user__first_name', 'user__last_name']

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'student', 'room', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'start_date']
    search_fields = ['contract_number', 'student__student_id']


from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    
    def mark_as_read(self, request, queryset):
        """Action: Đánh dấu đã đọc"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'Đã đánh dấu {updated} thông báo là đã đọc')
    mark_as_read.short_description = "Đánh dấu đã đọc"
    
    actions = [mark_as_read]