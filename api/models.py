from django.conf import settings
from django.db import models
import uuid
from martor.models import MartorField

from .pricing import kes_to_usd


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
    writeup_body=models.TextField()

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


class TrainingOffering(models.Model):
    """A paid training track or consultation slot shown on /training/."""

    class Kind(models.TextChoices):
        COURSE = 'COURSE', 'Course'
        CONSULT = 'CONSULT', 'Consultation'

    class Track(models.TextChoices):
        WEB_ENUM = 'WEB_ENUM', 'Web app enumeration'
        ACTIVE_DIRECTORY = 'AD', 'Active Directory'
        OSINT = 'OSINT', 'OSINT'
        INITIAL_ACCESS = 'INITIAL_ACCESS', 'Initial access'
        BACKDOORS = 'BACKDOORS', 'Backdoors & persistence'
        WEB_APIS = 'WEB_APIS', 'Web programming & APIs'
        FORENSICS = 'FORENSICS', 'Forensics'

    class Level(models.TextChoices):
        FOUNDATION = 'FND', 'Foundation'
        OPERATOR = 'OPS', 'Operator'
        ADVERSARY = 'ADV', 'Adversary'

    slug = models.SlugField(unique=True, max_length=80)
    title = models.CharField(max_length=100)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.COURSE)
    track = models.CharField(max_length=20, choices=Track.choices, blank=True, default='')
    level = models.CharField(max_length=3, choices=Level.choices, default=Level.OPERATOR)
    summary = models.CharField(max_length=240)
    details = models.TextField(max_length=4000, blank=True)
    hours = models.PositiveSmallIntegerField(default=4)
    hourly_rate_kes = models.PositiveIntegerField(default=settings.DEFAULT_TRAINING_RATE_KES)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ('sort_order', 'title')

    def __str__(self):
        return self.title

    @property
    def hourly_rate_kes_display(self):
        return f'{self.hourly_rate_kes:,}'

    @property
    def hourly_rate_usd(self):
        return kes_to_usd(self.hourly_rate_kes)

    @property
    def track_label(self):
        return self.get_track_display() if self.track else self.get_kind_display()


class TrainingOffer(models.Model):
    """Inbound voucher / forum-link / collaboration offers. Moderated in admin."""

    class Kind(models.TextChoices):
        VOUCHER = 'VOUCHER', 'Voucher / credit'
        FORUM = 'FORUM', 'Forum / community link'
        COLLAB = 'COLLAB', 'Collaboration'
        OTHER = 'OTHER', 'Something else'

    offering = models.ForeignKey(
        TrainingOffering,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offers',
    )
    callsign = models.CharField(max_length=80)
    contact = models.CharField(max_length=120)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.VOUCHER)
    link = models.URLField(max_length=300, blank=True)
    message = models.TextField(max_length=2000)
    is_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.callsign} · {self.get_kind_display()}'


