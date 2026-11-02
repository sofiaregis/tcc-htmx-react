from django.db import models
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model


User = get_user_model()


class Event(models.Model):
    CATEGORY_CHOICES = [
        ("tech", "Tecnologia"),
        ("business", "Negócios"),
        ("art", "Artes"),
        ("sports", "Esportes"),
        ("music", "Música"),
        ("education", "Educação"),
        ("health", "Saúde e Bem-estar"),
        ("food", "Culinária"),
        ("environment", "Meio Ambiente"),
        ("photography", "Fotografia"),
        ("other", "Outros"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="other")
    image = models.ImageField(upload_to="event_images/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    organizer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organized_events"
    )

    class Meta:
        db_table = 'events_event'

    def __str__(self):
        return self.title
    
    @property
    def is_past(self):
        """Retorna True se o evento já foi encerrado."""
        from .time_utils import get_current_time
        event_datetime = datetime.combine(self.date, self.time)
        # Garante que o datetime seja timezone-aware
        event_datetime = timezone.make_aware(event_datetime, timezone.get_current_timezone())
        return event_datetime < get_current_time()

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'events_registration'
        unique_together = ("event", "participant")  # evita inscrição duplicada

    def __str__(self):
        return f"{self.participant.username} -> {self.event.title}"
