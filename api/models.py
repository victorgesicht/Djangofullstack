
# Create your models here.
from django.db import models
import uuid


class Bulletins(models.Model):

    class Platform(models.TextChoices):
        TRYHACKME = 'THM', 'TryHackMe'
        PORTSWIGGER = 'PS', 'PortSwigger'
        ROOT_ME = 'RM', 'Root-Me'
        HACKTHEBOX = 'HTB', 'HackTheBox'

    class Difficulty(models.TextChoices):
        EASY = 'E', 'Easy'
        MEDIUM = 'M', 'Medium'
        HARD = 'H', 'Hard'
        INSANE = 'I', 'Insane'

    class Category(models.TextChoices):
        WEB='WEB', 'web-apps'
        RE='RE', 'Reverse engineering'
        SOC='SOC', 'Forensics'




    publication_date=models.DateField(auto_now_add=True)
    id=models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    writeup_author=models.CharField(max_length=5,default='cratis')
    title=models.CharField(max_length=20, default='title goes here.')
    writeup_body=models.TextField
    writeup_difficulty=models.CharField(max_length=1, choices=Difficulty.choices, default=Difficulty.EASY)
    writeup_platform=models.CharField(max_length=3,default=Platform.TRYHACKME, choices=Platform.choices)
    writeup_slug=models.SlugField(unique=True, default='slugify')
    writeup_category=models.CharField(default=Category.SOC, max_length=3, choices=Category.choices)




    def __str__(self):
        return f"{self.title}"


class IntelNote(models.Model):
    id=models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    writeup_author=models.CharField(max_length=5,default='cratis')
    title=models.CharField(max_length=20, default='title goes here.')
    writeup_body=models.TextField



