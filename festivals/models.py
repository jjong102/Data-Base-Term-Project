from django.db import models


class Location(models.Model):
    """Normalized location information for a festival."""

    name = models.CharField(max_length=200, blank=True)
    address_road = models.CharField(max_length=255, blank=True)
    address_lot = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=12, null=True, blank=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=12, null=True, blank=True)

    class Meta:
        unique_together = ("name", "address_road", "address_lot", "latitude", "longitude")

    def __str__(self):
        parts = [self.name or "", self.address_road or self.address_lot or ""]
        return " ".join(part for part in parts if part).strip() or "Unknown location"


class Organization(models.Model):
    """Party involved with a festival (organizer/host/sponsor)."""

    name = models.CharField(max_length=200, unique=True)
    telephone = models.CharField(max_length=50, blank=True)
    homepage = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Festival(models.Model):
    external_id = models.CharField(max_length=255, unique=True, db_index=True, blank=True)
    title = models.CharField(max_length=200)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name="festivals")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    homepage = models.URLField(blank=True)
    extra_info = models.TextField(blank=True)
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

    def _get_org_name(self, role: str):
        rel = self.organizations.filter(role=role).select_related("organization").first()
        return rel.organization.name if rel else ""

    @property
    def organizer_name(self):
        return self._get_org_name(FestivalOrganization.Role.ORGANIZER)

    @property
    def host_name(self):
        return self._get_org_name(FestivalOrganization.Role.HOST)

    @property
    def sponsor_name(self):
        return self._get_org_name(FestivalOrganization.Role.SPONSOR)

    @property
    def place_name(self):
        return self.location.name if self.location else ""

    @property
    def address_display(self):
        if not self.location:
            return ""
        return self.location.address_road or self.location.address_lot or ""

    # Compatibility properties (for legacy templates/admin)
    @property
    def place(self):
        return self.place_name

    @property
    def organizer(self):
        return self.organizer_name

    @property
    def host(self):
        return self.host_name

    @property
    def sponsor(self):
        return self.sponsor_name

    @property
    def address_road(self):
        return self.location.address_road if self.location else ""

    @property
    def address_lot(self):
        return self.location.address_lot if self.location else ""

    @property
    def latitude(self):
        return self.location.latitude if self.location else None

    @property
    def longitude(self):
        return self.location.longitude if self.location else None


class FestivalOrganization(models.Model):
    class Role(models.TextChoices):
        ORGANIZER = "organizer", "Organizer"
        HOST = "host", "Host"
        SPONSOR = "sponsor", "Sponsor"

    festival = models.ForeignKey(Festival, on_delete=models.CASCADE, related_name="organizations")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="festival_roles")
    role = models.CharField(max_length=20, choices=Role.choices)

    class Meta:
        unique_together = ("festival", "role")

    def __str__(self):
        return f"{self.festival.title} - {self.get_role_display()}: {self.organization.name}"


class Comment(models.Model):
    festival = models.ForeignKey(Festival, related_name="comments", on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nickname}: {self.content[:20]}"
