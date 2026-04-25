from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser as User


class SignupViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')

    def test_signup_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user(self):
        response = self.client.post(self.url, {
            'student_id': 'AUCA-2024-001',
            'first_name': 'Test',
            'email':      'test@auca.ac.rw',
            'password1':  'StrongPass123!',
            'password2':  'StrongPass123!',
        })
        self.assertEqual(User.objects.filter(email='test@auca.ac.rw').count(), 1)
        self.assertRedirects(response, reverse('login'))

    def test_signup_password_mismatch(self):
        self.client.post(self.url, {
            'student_id': 'AUCA-2024-002',
            'first_name': 'Test',
            'email':      'test2@auca.ac.rw',
            'password1':  'StrongPass123!',
            'password2':  'WrongPass456!',
        })
        self.assertEqual(User.objects.filter(email='test2@auca.ac.rw').count(), 0)

    def test_signup_duplicate_email(self):
        User.objects.create_user(username='dup@auca.ac.rw', email='dup@auca.ac.rw', password='Pass123!')
        self.client.post(self.url, {
            'student_id': 'AUCA-2024-003',
            'first_name': 'Dup',
            'email':      'dup@auca.ac.rw',
            'password1':  'StrongPass123!',
            'password2':  'StrongPass123!',
        })
        self.assertEqual(User.objects.filter(email='dup@auca.ac.rw').count(), 1)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.user = User.objects.create_user(
            username='login@auca.ac.rw',
            email='login@auca.ac.rw',
            password='TestPass123!',
            student_id='AUCA-2024-003',
        )

    def test_login_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_login_with_valid_credentials(self):
        response = self.client.post(self.url, {
            'email':    'login@auca.ac.rw',
            'password': 'TestPass123!',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(self.url, {
            'email':    'login@auca.ac.rw',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username='login@auca.ac.rw', password='TestPass123!')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'))


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='profile@auca.ac.rw',
            email='profile@auca.ac.rw',
            password='TestPass123!',
        )
        self.client.login(username='profile@auca.ac.rw', password='TestPass123!')

    def test_profile_page_loads(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_update(self):
        self.client.post(reverse('profile'), {
            'first_name': 'Updated',
            'last_name':  'Name',
            'email':      'profile@auca.ac.rw',
            'phone':      '+250788000000',
            'bio':        'Test bio',
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.phone, '+250788000000')


class DecoratorTest(TestCase):
    def setUp(self):
        self.client = Client()

    def _make_user(self, role, email):
        return User.objects.create_user(username=email, email=email, password='Pass123!', role=role)

    def test_student_required_blocks_lecturer(self):
        self._make_user('lecturer', 'lec@auca.ac.rw')
        self.client.login(username='lec@auca.ac.rw', password='Pass123!')
        response = self.client.get(reverse('student_area'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_staff_required_blocks_student(self):
        self._make_user('student', 'stu@auca.ac.rw')
        self.client.login(username='stu@auca.ac.rw', password='Pass123!')
        response = self.client.get(reverse('staff_area'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_lecturer_required_allows_student(self):
        self._make_user('student', 'stu2@auca.ac.rw')
        self.client.login(username='stu2@auca.ac.rw', password='Pass123!')
        response = self.client.get(reverse('lecturer_area'))
        self.assertEqual(response.status_code, 200)
