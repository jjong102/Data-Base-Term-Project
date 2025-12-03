from django.db import models


class Festival(models.Model):
    external_id = models.CharField(max_length=255, unique=True, db_index=True, blank=True)
    title = models.CharField(max_length=200)
    place = models.CharField(max_length=200, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    organizer = models.CharField(max_length=200, blank=True)  # 주관
    host = models.CharField(max_length=200, blank=True)  # 주최
    sponsor = models.CharField(max_length=200, blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    homepage = models.URLField(blank=True)
    extra_info = models.TextField(blank=True)
    address_road = models.CharField(max_length=255, blank=True)
    address_lot = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=12, null=True, blank=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=12, null=True, blank=True)
    data_reference_date = models.DateField(null=True, blank=True)
    pub_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_date", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.external_id:
            base = f"{self.title}-{self.start_date or ''}".strip() or self.title
            self.external_id = base[:250]
        super().save(*args, **kwargs)


class Comment(models.Model):
    festival = models.ForeignKey(Festival, related_name="comments", on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nickname}: {self.content[:20]}"
