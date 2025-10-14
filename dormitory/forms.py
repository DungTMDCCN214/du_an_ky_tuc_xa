# dormitory/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
from .models import Room, Building, Student, Contract

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'building', 'room_type', 'floor', 'status', 'notes']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'building': forms.Select(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'address', 'total_floors', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'university', 'faculty', 'course', 'date_of_birth']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'university': forms.TextInput(attrs={'class': 'form-control'}),
            'faculty': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['contract_number', 'student', 'room', 'start_date', 'end_date', 'deposit', 'status']
        widgets = {
            'contract_number': forms.TextInput(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'room': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

# dormitory/forms.py - THÊM VALIDATION
class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=True, label="Số điện thoại")
    student_id = forms.CharField(max_length=20, required=True, label="Mã sinh viên")
    university = forms.CharField(max_length=200, required=True, label="Trường")
    faculty = forms.CharField(max_length=100, required=True, label="Khoa")
    course = forms.CharField(max_length=50, required=True, label="Khóa học")
    date_of_birth = forms.DateField(required=True, label="Ngày sinh", 
                                   widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập đã tồn tại!")
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email đã được sử dụng!")
        return email
    
    def clean_student_id(self):
        student_id = self.cleaned_data['student_id']
        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("Mã sinh viên đã tồn tại!")
        return student_id
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.user_type = 'student'
        if commit:
            user.save()
        return user