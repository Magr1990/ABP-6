from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Project, Task
from .forms import UserRegisterForm, ProjectForm, TaskForm
from django.contrib.auth.models import User
from django.utils import timezone

def home(request):
    if request.user.is_authenticated:
        return redirect('project_list')
    return render(request, 'tasks/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada para {username}! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'tasks/register.html', {'form': form})

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'tasks/project_list.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        return Project.objects.filter(created_by=self.request.user)

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'tasks/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        return Project.objects.filter(created_by=self.request.user)

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'tasks/project_form.html'
    success_url = reverse_lazy('project_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Proyecto creado exitosamente!')
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'tasks/project_form.html'
    
    def get_queryset(self):
        return Project.objects.filter(created_by=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, 'Proyecto actualizado exitosamente!')
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'tasks/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')
    
    def get_queryset(self):
        return Project.objects.filter(created_by=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Proyecto eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Task.objects.all()
        return Task.objects.filter(
            Q(created_by=self.request.user) | Q(assigned_to=self.request.user)
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'all')
        context['today'] = timezone.now().date()
        
        if context['filter'] == 'my_tasks':
            context['tasks'] = Task.objects.filter(assigned_to=self.request.user)
        elif context['filter'] == 'created_by_me':
            context['tasks'] = Task.objects.filter(created_by=self.request.user)
        
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Task.objects.all()
        return Task.objects.filter(
            Q(created_by=self.request.user) | Q(assigned_to=self.request.user)
        ).distinct()

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Tarea creada exitosamente!')
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Task.objects.all()
        return Task.objects.filter(
            Q(created_by=self.request.user) | Q(assigned_to=self.request.user)
        ).distinct()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        messages.success(self.request, 'Tarea actualizada exitosamente!')
        return reverse_lazy('task_detail', kwargs={'pk': self.object.pk})

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Task.objects.all()
        return Task.objects.filter(created_by=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tarea eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)

@login_required
def dashboard(request):
    projects = Project.objects.filter(created_by=request.user)
    tasks = Task.objects.filter(
        Q(created_by=request.user) | Q(assigned_to=request.user)
    ).distinct()
    
    context = {
        'total_projects': projects.count(),
        'total_tasks': tasks.count(),
        'pending_tasks': tasks.filter(status='pending').count(),
        'completed_tasks': tasks.filter(status='completed').count(),
        'overdue_tasks': tasks.filter(due_date__lt=timezone.now().date()).exclude(status__in=['completed', 'cancelled']).count(),
        'recent_projects': projects.order_by('-created_at')[:5],
        'recent_tasks': tasks.order_by('-created_at')[:5],
    }
    
    return render(request, 'tasks/dashboard.html', context)