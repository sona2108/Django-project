from celery import shared_task
from django.core.mail import send_mass_mail, EmailMessage
from django.contrib.auth import get_user_model
from django.conf import settings
import time
from .models import Post  
from django.utils import timezone
import csv
import os, io 
from blog.models import LogEntry

@shared_task
def send_new_post_notification(post_title, post_content):
    User = get_user_model()
    recipients = User.objects.values_list('email', flat=True)

    subject = f"New Blog Post: {post_title}"
    message = f"{post_content[:200]}...\n\nRead more on the site!"

    messages = [(subject, message, 'sona.sharma21x8@gmail.com', [email]) for email in recipients]

    send_mass_mail(messages, fail_silently=False)

@shared_task
def send_daily_blog_summary():
    User = get_user_model()
    recipients = User.objects.filter(is_active=True).exclude(email="").values_list('email', flat=True)

    today = timezone.now().date()
    new_posts = Post.objects.filter(date_posted__date=today)

    if not new_posts.exists():
        return "No new posts today."

    subject = "📬 Daily Blog Summary"
    post_lines = [f"- {post.title}" for post in new_posts]
    message = "Today's new blog posts:\n\n" + "\n".join(post_lines)

    messages = [
        (subject, message, 'sona.sharma21x8@gmail.com', [email])
        for email in recipients
    ]

    send_mass_mail(messages, fail_silently=False)
    return f"Sent to {len(recipients)} users."

@shared_task
def export_logs_to_csv_and_email():
    logs = LogEntry.objects.all().order_by('-timestamp')[:500]

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Timestamp", "Level", "Source", "Message"])

    for log in logs:
        writer.writerow([
            log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            log.level,
            log.logger_name,
            log.message
        ])

    buffer.seek(0)

    email = EmailMessage(
        subject="Django Log Report",
        body="Attached is the log report exported from the database.",
        from_email=settings.EMAIL_HOST_USER,
        to=["sona.sharma21x8@gmail.com"],
    )
    email.attach("log_report.csv", buffer.getvalue(), "text/csv")
    email.send()

    return "CSV log file emailed successfully."
