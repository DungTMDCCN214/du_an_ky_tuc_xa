from django.apps import AppConfig


class DormitoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dormitory'


# dormitory/apps.py
from django.apps import AppConfig

class DormitoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dormitory'

    def ready(self):
        """
        Kết nối signals khi app được load
        """
        try:
            import dormitory.signals
        except ImportError:
            # Bỏ qua nếu có lỗi import
            pass