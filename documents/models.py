from django.db import models
from django.contrib.auth.models import User
import uuid


class Asset(models.Model):
    """
    Represents a digital asset uploaded by a user.
    Matches the Digital_Asset table from the DLMS capstone report.
    """

    # ── Asset Types ───────────────────────────────────────────────
    ASSET_TYPE_CHOICES = [
        ('document',    'Document (PDF, Word)'),
        ('image',       'Image (JPG, PNG)'),
        ('video',       'Video'),
        ('note',        'Text Note'),
        ('financial',   'Financial Document'),
        ('social',      'Social Media Archive'),
        ('other',       'Other'),
    ]

    # ── Posthumous Actions ────────────────────────────────────────
    POSTHUMOUS_ACTION_CHOICES = [
        ('delete',    'Delete after death'),
        ('transfer',  'Transfer to beneficiary'),
    ]

    # ── Privacy Levels ────────────────────────────────────────────
    PRIVACY_CHOICES = [
        ('LOW',    'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH',   'High'),
    ]

    # ── Sensitivity (set by NLP) ──────────────────────────────────
    SENSITIVITY_CHOICES = [
        ('LOW',    'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH',   'High'),
    ]

    # Unique ID
    asset_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Owner
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assets'
    )

    # Basic info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    asset_type = models.CharField(
        max_length=20,
        choices=ASSET_TYPE_CHOICES,
        default='document'
    )

    # The actual file — stored in AWS S3
    # Files go to: s3://erth-dlms-assets/assets/user_{id}/filename
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        null=True,
        blank=True
    )

    # Text content (for text notes or extracted text)
    content = models.TextField(blank=True, null=True)

    # Privacy & sensitivity
    privacy_level = models.CharField(
        max_length=10,
        choices=PRIVACY_CHOICES,
        default='MEDIUM'
    )
    sensitivity_level = models.CharField(
        max_length=10,
        choices=SENSITIVITY_CHOICES,
        default='LOW'
    )

    # NLP analysis results
    nlp_score = models.FloatField(default=0.0)
    nlp_analyzed = models.BooleanField(default=False)

    # Posthumous action
    posthumous_action = models.CharField(
        max_length=20,
        choices=POSTHUMOUS_ACTION_CHOICES,
        default='transfer'
    )

    # Timestamps
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    deleted_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.asset_type}) — {self.user.username}"

    def get_file_url(self):
        """Returns the S3 URL of the uploaded file."""
        if self.file:
            return self.file.url
        return None