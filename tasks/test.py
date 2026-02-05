from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Project, Task
from datetime import date, timedelta

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_project(self):
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            status='pending'
        )
        self.assertEqual(str(project), 'Test Project')
        self.assertEqual(project.created_by, self.user)
    
    def test_create_task(self):
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user,
            start_date=date.today(),
            status='pending'
        )
        
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=project,
            created_by=self.user,
            due_date=date.today() + timedelta(days=3),
            priority='medium',
            status='pending'
        )
        
        self.assertEqual(str(task), 'Test Task')
        self.assertEqual(task.project, project)
        self.assertEqual(task.created_by, self.user)

class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user,
            start_date=date.today()
        )
    
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_project_list_view(self):
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
    
    def test_task_list_view(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_project_create_view(self):
        response = self.client.post(reverse('project_create'), {
            'name': 'New Project',
            'description': 'New Description',
            'start_date': date.today(),
            'status': 'pending'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name='New Project').exists())

class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_project_form_valid(self):
        from .forms import ProjectForm
        form_data = {
            'name': 'Test Project',
            'description': 'Test Description',
            'start_date': date.today(),
            'status': 'pending'
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_project_form_invalid_date(self):
        from .forms import ProjectForm
        form_data = {
            'name': 'Test Project',
            'description': 'Test Description',
            'start_date': date.today() + timedelta(days=1),
            'end_date': date.today(),
            'status': 'pending'
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)