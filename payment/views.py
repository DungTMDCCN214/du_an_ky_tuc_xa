# payment/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Payment
from dormitory.models import Contract, Student
from .forms import PaymentForm
from django.db.models import Q, Sum

@login_required
def payment_list(request):
    """Danh sách hóa đơn thanh toán"""
    search_query = request.GET.get('search', '')
    selected_status = request.GET.get('status', '')
    today = timezone.now().date()

    payments = Payment.objects.select_related(
        'contract__student',
        'contract__room__building'
    )

    # Nếu là sinh viên => chỉ xem hóa đơn của mình
    if getattr(request.user, 'user_type', None) == 'student' and not (request.user.is_staff or request.user.is_superuser):
        payments = payments.filter(contract__student__user=request.user)

    # Lọc theo tìm kiếm
    if search_query:
        payments = payments.filter(
            Q(id__icontains=search_query)
            | Q(contract__student__student_id__icontains=search_query)
            | Q(contract__student__full_name__icontains=search_query)
            | Q(contract__room__room_number__icontains=search_query)
            | Q(contract__room__building__name__icontains=search_query)
        )

    # Lọc theo trạng thái
    if selected_status == 'pending':
        payments = payments.filter(status='pending', due_date__gte=today)
    elif selected_status == 'paid':
        payments = payments.filter(status='paid')
    elif selected_status == 'overdue':
        payments = payments.filter(status='pending', due_date__lt=today)

    # Thống kê tổng quát
    stats = {
        'total_pending': Payment.objects.filter(status='pending').count(),
        'total_paid': Payment.objects.filter(status='paid').count(),
        'total_amount': Payment.objects.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0,
    }

    context = {
        'payments': payments,
        'stats': stats,
        'today': today,
        'search_query': search_query,
        'selected_status': selected_status,
    }
    return render(request, 'payment/payment_list.html', context)

@login_required
def payment_create(request):
    """Tạo hóa đơn thanh toán (chỉ quản lý hoặc nhân viên)"""
    if getattr(request.user, 'user_type', None) == 'student' and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Bạn không có quyền tạo hóa đơn!")
        return redirect('payment_list')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.save()
            messages.success(request, f"💾 Đã tạo hóa đơn #{payment.id} thành công!")
            return redirect('payment_list')
    else:
        form = PaymentForm()

    return render(request, 'payment/payment_form.html', {'form': form})


@login_required
def payment_detail(request, pk):
    """Chi tiết thanh toán"""
    payment = get_object_or_404(Payment, pk=pk)

    # Nếu là sinh viên và không phải staff/superuser => chỉ xem hóa đơn của mình
    if getattr(request.user, 'user_type', None) == 'student' and not (request.user.is_staff or request.user.is_superuser):
        if payment.contract.student.user != request.user:
            messages.error(request, "Bạn không có quyền xem hóa đơn này!")
            return redirect('payment_list')

    return render(request, 'payment/payment_detail.html', {'payment': payment})


@login_required
def payment_update(request, pk):
    """Cập nhật hóa đơn (chỉ quản lý hoặc nhân viên)"""
    if getattr(request.user, 'user_type', None) == 'student' and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Bạn không có quyền cập nhật hóa đơn!")
        return redirect('payment_list')

    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Đã cập nhật hóa đơn #{payment.id}!")
            return redirect('payment_list')
    else:
        form = PaymentForm(instance=payment)

    return render(request, 'payment/payment_form.html', {'form': form})

# payment/views.py - THÊM FUNCTION
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .services import send_payment_reminder

def send_reminder(request, pk):
    """Gửi email nhắc nhở cho hóa đơn cụ thể"""
    if request.user.user_type == 'student':
        messages.error(request, "Bạn không có quyền gửi email!")
        return redirect('payment_list')
    
    payment = get_object_or_404(Payment, pk=pk)
    
    if send_payment_reminder(payment, request):
        messages.success(request, f'✅ Đã gửi email nhắc nhở cho HĐ #{payment.id}!')
    else:
        messages.error(request, '❌ Gửi email thất bại!')
    
    return redirect('admin:payment_payment_changelist')
# THÊM VÀO payment/views.py - CUỐI FILE


@login_required
def student_payments(request):
    """Trang thanh toán dành cho sinh viên"""
    if request.user.user_type != 'student':
        messages.error(request, "Chỉ sinh viên mới có thể truy cập trang này")
        return redirect('home')

    try:
        student = request.user.student
        current_contract = Contract.objects.filter(student=student, status='active').first()

        # Lấy tất cả hóa đơn của sinh viên
        payments = Payment.objects.filter(student=student).select_related('contract__room').order_by('-created_at')

        # Phân loại theo loại thanh toán
        payments_room = payments.filter(payment_type='room')
        payments_electric = payments.filter(payment_type='electric')
        payments_water = payments.filter(payment_type='water')

        # Nhóm trạng thái
        pending_payments = payments.filter(status='pending')
        paid_payments = payments.filter(status='paid')

        total_pending_amount = sum(p.amount for p in pending_payments)

        context = {
            'student': student,
            'current_contract': current_contract,
            'payments_room': payments_room,
            'payments_electric': payments_electric,
            'payments_water': payments_water,
            'pending_payments': pending_payments,
            'paid_payments': paid_payments,
            'total_pending_amount': total_pending_amount,
            'today': timezone.now().date(),
        }
        return render(request, 'payment/student_payments.html', context)

    except Student.DoesNotExist:
        messages.error(request, "Vui lòng hoàn thiện hồ sơ sinh viên trước!")
        return redirect('complete_profile')

@login_required
def payment_history(request):
    """Lịch sử thanh toán đầy đủ của sinh viên"""
    if request.user.user_type != 'student':
        return redirect('home')
    
    student = request.user.student
    payments = Payment.objects.filter(student=student).select_related('contract__room').order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    return render(request, 'payment/payment_history.html', context)


@login_required
def process_payment(request, payment_id):
    """Xử lý thanh toán - TRANG CHỌN PHƯƠNG THỨC"""
    if request.user.user_type != 'student':
        return redirect('home')
    
    payment = get_object_or_404(Payment, id=payment_id, student__user=request.user)
    
    if payment.status == 'paid':
        messages.info(request, "Hóa đơn này đã được thanh toán!")
        return redirect('student_payments')
    
    context = {
        'payment': payment,
    }
    return render(request, 'payment/payment_method.html', context)
@login_required
def create_monthly_invoice(request):
    """Tạo hóa đơn hàng tháng (cho testing)"""
    if request.user.user_type != 'student':
        return redirect('home')
    
    student = request.user.student
    current_contract = Contract.objects.filter(student=student, status='active').first()
    
    if not current_contract:
        messages.error(request, "Bạn chưa có hợp đồng phòng!")
        return redirect('student_payments')
    
    # Kiểm tra xem đã có hóa đơn tháng này chưa
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    existing_invoice = Payment.objects.filter(
        student=student,
        created_at__month=current_month,
        created_at__year=current_year,
        notes__contains="Tiền phòng tháng"
    ).first()
    
    if existing_invoice:
        messages.info(request, "Đã có hóa đơn tháng này!")
        return redirect('student_payments')
    
    # Tạo hóa đơn mới
    due_date = timezone.now().date() + timezone.timedelta(days=7)
    
    payment = Payment.objects.create(
        contract=current_contract,
        student=student,  # Thêm student
        amount=current_contract.room.room_type.price_per_month,
        due_date=due_date,
        notes=f"Tiền phòng tháng {current_month}/{current_year} - Phòng {current_contract.room.room_number}"
    )
    
    messages.success(request, f"Đã tạo hóa đơn tháng {current_month}!")
    return redirect('student_payments')

@login_required
def payment_gateway(request, payment_id):
    """Hiển thị thông tin thanh toán chi tiết theo phương thức"""
    if request.user.user_type != 'student':
        return redirect('home')
    
    payment = get_object_or_404(Payment, id=payment_id, student__user=request.user)
    
    if payment.status == 'paid':
        messages.info(request, "Hóa đơn này đã được thanh toán!")
        return redirect('student_payments')
    
    method = request.GET.get('method', 'bank_transfer')
    
    bank_info = {
        "bank_name": "Ngân hàng @@@",
        "account_name": "KTX  Học viện Công nghệ Bưu chính Viễn thông",
        "account_number": "0123456789",
        "branch": "Chi nhánh Hà Nội",
        "transfer_content": f"Thanh toan hoa don #{payment.id} - {payment.contract.room.room_number}",
    }

    context = {
        'payment': payment,
        'method': method,
        'method_display': dict(Payment.PAYMENT_METHODS).get(method, method),
        'bank_info': bank_info,
    }
    return render(request, 'payment/payment_gateway.html', context)


@login_required
def confirm_payment(request, payment_id):
    """Xác nhận thanh toán (chỉ xử lý khi POST)"""
    if request.user.user_type != 'student':
        return redirect('home')
    
    payment = get_object_or_404(Payment, id=payment_id, student__user=request.user)
    
    if payment.status == 'paid':
        messages.info(request, "Hóa đơn này đã được thanh toán!")
        return redirect('student_payments')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

    # ✅ Xử lý theo từng phương thức
        if payment_method == 'bank_transfer':
            payment.payment_method = 'bank_transfer'
            payment.status = 'pending'  # Chờ quản lý xác nhận
            payment.paid_date = None
            payment.transaction_id = f"BT{timezone.now().strftime('%Y%m%d%H%M%S')}"
            payment.save()
            messages.info(request, "💳 Đã ghi nhận thông tin chuyển khoản. Quản lý sẽ xác nhận sau khi kiểm tra.")
            return redirect('student_payments')

        elif payment_method in ['momo', 'zalopay']:
            payment.payment_method = payment_method
            payment.status = 'paid'
            payment.paid_date = timezone.now().date()
            payment.transaction_id = f"TX{timezone.now().strftime('%Y%m%d%H%M%S')}"
            payment.save()
            messages.success(request, f"✅ Thanh toán thành công qua {payment_method.capitalize()} {payment.amount:,.0f} VNĐ!")
            return redirect('student_payments')

        elif payment_method == 'cash':
            # Tiền mặt sẽ xử lý ở select_payment_method -> chỉ phòng khi bị gửi lại
            messages.info(request, "💵 Thanh toán tiền mặt đã được ghi nhận trước đó.")
            return redirect('student_payments')

        else:
            return redirect('student_payments')
    else:
        return redirect('payment_gateway', payment_id=payment_id)


from django.urls import reverse
from django.utils.http import urlencode

@login_required
def select_payment_method(request, payment_id):
    if request.user.user_type != 'student':
        return redirect('home')

    payment = get_object_or_404(Payment, id=payment_id, student__user=request.user)

    if request.method != 'POST':
        return redirect('payment_gateway', payment_id=payment_id)

    method = request.POST.get('payment_method')

    if method == 'cash':
        messages.info(request, "Vui lòng đến văn phòng để hoàn tất thanh toán tiền mặt.")
        url = reverse('payment_gateway', args=[payment.id]) + '?method=cash'
        return redirect(url)

    elif method == 'bank_transfer':
        # Chuyển đến trang hiển thị thông tin chuyển khoản (bank account + hướng dẫn).
        url = reverse('payment_gateway', args=[payment.id]) + '?' + urlencode({'method': 'bank_transfer'})
        return redirect(url)

    elif method == 'momo':
        # Redirect đến trang mô phỏng / tạo link MoMo (trang này có thể tạo request đến MoMo)
        url = reverse('payment_gateway', args=[payment.id]) + '?' + urlencode({'method': 'momo'})
        return redirect(url)

    elif method == 'zalopay':
        url = reverse('payment_gateway', args=[payment.id]) + '?' + urlencode({'method': 'zalopay'})
        return redirect(url)
    else:
        return redirect('process_payment', payment_id=payment.id)

@login_required
def payment_pending(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student__user=request.user)
    return render(request, 'payment/payment_pending.html', {'payment': payment})



@login_required
def generate_qr_payment(request, payment_id):
    """Tạo QR code cho thanh toán"""
    try:
        payment = get_object_or_404(Payment, id=payment_id, student__user=request.user)
        
        # Tạo nội dung QR code
        import qrcode
        from io import BytesIO
        from django.http import HttpResponse
        
        qr_data = {
            'payment_id': payment.id,
            'amount': float(payment.amount),
            'account': 'KTX_UNIVERSITY',
            'content': f'Thanh toan tien phong {payment.contract.room.room_number}',
            'timestamp': timezone.now().isoformat()
        }
        
        # Tạo QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        
        # Tạo image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Lưu vào buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return HttpResponse(buffer.getvalue(), content_type='image/png')
        
    except Exception as e:
        # Trả về ảnh lỗi hoặc redirect
        return redirect('student_payments')

@login_required
def payment_list(request):
    search_query = request.GET.get('search', '')
    selected_status = request.GET.get('status', '')
    selected_type = request.GET.get('type', '')

    today = timezone.now().date()

    payments = Payment.objects.select_related(
        'contract__student',
        'contract__room__building'
    )

    # Lọc theo từ khóa tìm kiếm
    if search_query:
        payments = payments.filter(
            Q(id__icontains=search_query) |
            Q(contract__student__student_id__icontains=search_query) |
            Q(contract__student__full_name__icontains=search_query) |
            Q(contract__room__room_number__icontains=search_query) |
            Q(contract__room__building__name__icontains=search_query)
        )

    # Lọc theo loại thanh toán
    if selected_type in ['room', 'electric', 'water']:
        payments = payments.filter(payment_type=selected_type)

    # Lọc theo trạng thái
    if selected_status == 'pending':
        payments = payments.filter(status='pending', due_date__gte=today)
    elif selected_status == 'paid':
        payments = payments.filter(status='paid')
    elif selected_status == 'overdue':
        payments = payments.filter(status='pending', due_date__lt=today)

    # Thống kê tổng quát
    stats = {
        'total_pending': Payment.objects.filter(status='pending').count(),
        'total_paid': Payment.objects.filter(status='paid').count(),
        'total_amount': Payment.objects.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0,
    }

    context = {
        'payments': payments,
        'stats': stats,
        'today': today,
        'search_query': search_query,
        'selected_status': selected_status,
        'selected_type': selected_type,
    }
    return render(request, 'payment/payment_list.html', context)

@login_required
def create_electric_payment(request):
    """Tạo hóa đơn tiền điện"""
    if request.user.user_type == 'student':
        messages.error(request, "Bạn không có quyền tạo hóa đơn!")
        return redirect('payment_list')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payment_type = 'electric'
            payment.save()
            messages.success(request, f"Đã tạo hóa đơn tiền điện #{payment.id} thành công!")
            return redirect('payment_list')
    else:
        form = PaymentForm(initial={'payment_type': 'electric'})
    
    return render(request, 'payment/payment_form.html', {'form': form})


@login_required
def create_water_payment(request):
    """Tạo hóa đơn tiền nước"""
    if request.user.user_type == 'student':
        messages.error(request, "Bạn không có quyền tạo hóa đơn!")
        return redirect('payment_list')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payment_type = 'water'
            payment.save()
            messages.success(request, f"Đã tạo hóa đơn tiền nước #{payment.id} thành công!")
            return redirect('payment_list')
    else:
        form = PaymentForm(initial={'payment_type': 'water'})
    
    return render(request, 'payment/payment_form.html', {'form': form})
