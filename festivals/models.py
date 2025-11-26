from django.db import models


class Festival(models.Model):
    external_id = models.CharField(max_length=20, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    link = models.URLField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    organizer = models.CharField(max_length=200, blank=True)
    start_year = models.CharField(max_length=10, blank=True)
    period = models.CharField(max_length=120, blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    pub_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    festival = models.ForeignKey(Festival, related_name="comments", on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nickname}: {self.content[:20]}"
