from django.urls import path
from . import views

urlpatterns = [
    # URLs cho quản lý
    path('', views.payment_list, name='payment_list'),
    path('create/', views.payment_create, name='payment_create'),
    path('<int:pk>/', views.payment_detail, name='payment_detail'),
    path('<int:pk>/update/', views.payment_update, name='payment_update'),
    path('<int:pk>/send-reminder/', views.send_reminder, name='send_reminder'),
    path('', views.payment_list, name='payment_list'),
    path('create/', views.payment_create, name='payment_create'),
    # URLs cho sinh viên
    path('student/', views.student_payments, name='student_payments'),
    path('student/history/', views.payment_history, name='payment_history'),
    path('student/process/<int:payment_id>/', views.process_payment, name='process_payment'),
    path('student/create-invoice/', views.create_monthly_invoice, name='create_monthly_invoice'),
    
    # URLs MỚI cho thanh toán chi tiết
    path('student/gateway/<int:payment_id>/', views.payment_gateway, name='payment_gateway'),
    path('student/select/<int:payment_id>/', views.select_payment_method, name='select_payment_method'),
    path('student/confirm/<int:payment_id>/', views.confirm_payment, name='confirm_payment'),  
    path('create/electric/', views.create_electric_payment, name='create_electric_payment'),
    path('create/water/', views.create_water_payment, name='create_water_payment'),
]   