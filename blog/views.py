from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User 
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.http import HttpResponse
from .models import Post
from django.http import JsonResponse
from .tasks import send_new_post_notification
from users.models import Profile
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import time
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
import logging

def home (request):
    context = {
        'posts' : Post.objects.all()
    }
    return render(request, 'blog/home.html', context)

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs.get('username')  
        return context

class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        send_new_post_notification.delay(
            form.instance.title,
            form.instance.content
        )

        return super().form_valid(form)
    
    
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def trigger_task(request):
    send_email_task.delay()
    return HttpResponse("Basic email task triggered!")

@cache_page(60 * 10)
def get_all_blog_posts():
    posts = cache.get('all_blog_posts')
    if not posts:
        posts = Post.objects.all().order_by('-date_posted')  
        cache.set('all_blog_posts', posts, timeout=60 * 15) 
    return posts


def test_cache_view(request):
    value = cache.get("test_key")
    if value is None:
        value = f"Stored at {time.ctime()}"
        cache.set("test_key", value, timeout=60)  # 1 min
    return HttpResponse(f"Cached value: {value}")

def schedule_mail(request):
    schedule, created = CrontabSchedule.objects.get_or_create(hour=13, minute=5)
    task, created = PeriodicTask.objects.get_or_create(
        crontab=schedule,
        name="schedule_mail_task",
        defaults={'task': 'blog.tasks.send_daily_blog_summary', 'enabled': True}
    )
    return HttpResponse("done")

logger = logging.getLogger(__name__)

def index(request):
    logger.info("testing the logger!")
    try:
        User.objects.get(pk=1)
    except User.DoesNotExist:
        logger.error("User with ID %s does not exist", 1)
    context = {}
    return render(request, 'index.html', context)

import logging
logger = logging.getLogger(__name__)
logger.debug("Testing file log output")