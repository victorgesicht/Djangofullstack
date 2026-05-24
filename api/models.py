from django.db import models
import uuid
from martor.models import MartorField


class Bulletins(models.Model):

    class Platform(models.TextChoices):
        TRYHACKME = 'THM', 'TryHackMe'
        PORTSWIGGER = 'PortSwigger', 'PortSwigger'
        ROOT_ME = 'Root Me', 'Root-Me'
        HACKTHEBOX = 'HTB', 'HackTheBox'
        FAQ = 'FAQ', 'FAQ'

    class Difficulty(models.TextChoices):
        EASY = 'E', 'Easy'
        MEDIUM = 'M', 'Medium'
        HARD = 'H', 'Hard'
        INSANE = 'I', 'Insane'

    class Category(models.TextChoices):
        WEB = 'WEB', 'web-apps'
        RE = 'RE', 'Reverse engineering'
        SOC = 'SOC', 'Forensics'
        INFRA = 'SYS', 'Systems'


    # IDENTIFIERS
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    writeup_slug = models.SlugField(unique=True, max_length=100) # Removed 'slugify' default to avoid collisions

    # CONTENT
    title = models.CharField(max_length=100, default='ANALYSIS_LOG_0x0')
    writeup_body = MartorField(verbose_name="Post Content",
        help_text="Write your post content in Markdown",
        blank=True,
        null=True,
        max_length=10000,)
    writeup_author = models.CharField(max_length=20, default='cratis')

    # THE NEW IMAGE FIELD
    # This stores images in /media/bulletins/ (Ensure Pillow is installed)
    writeup_image = models.ImageField(upload_to='bulletins/%Y/%m/', null=True, blank=True)

    # METADATA
    writeup_difficulty = models.CharField(max_length=1, choices=Difficulty.choices, default=Difficulty.EASY)
    writeup_platform = models.CharField(max_length=11, default=Platform.TRYHACKME, choices=Platform.choices)
    writeup_category = models.CharField(default=Category.SOC, max_length=3, choices=Category.choices)
    publication_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"[{self.writeup_platform}] {self.title}"


class IntelNote(models.Model):
    id=models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    writeup_author=models.CharField(max_length=5,default='cratis')
    title=models.CharField(max_length=20, default='title goes here.')
    writeup_body=models.TextField

class Comment(models.Model):
    body=models.TextField()
    author = models.CharField(max_length=100)
    post = models.ForeignKey('Bulletins', on_delete=models.CASCADE, related_name='comments')
    created_on=models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_on'] # Newest first

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'


