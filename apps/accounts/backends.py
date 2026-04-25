from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOrStudentIDBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # username field holds either email or student_id from the login form
        user = (
            User.objects.filter(email=username).first() or
            User.objects.filter(student_id=username).first()
        )
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
