from django import forms

from .models import Comment, Festival, FestivalOrganization, Location, Organization


class CommentForm(forms.ModelForm):
    nickname = forms.CharField(
        max_length=30,
        min_length=2,
        widget=forms.TextInput(attrs={"placeholder": "닉네임을 입력하세요", "maxlength": 30}),
        error_messages={
            "required": "닉네임을 입력해 주세요.",
            "min_length": "닉네임은 2자 이상 입력해 주세요.",
        },
    )
    content = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": "댓글을 입력해 주세요", "maxlength": 1000}
        ),
        error_messages={"required": "내용을 입력해 주세요."},
    )

    class Meta:
        model = Comment
        fields = ["nickname", "content"]

    def clean_nickname(self):
        nickname = self.cleaned_data["nickname"].strip()
        return nickname

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if not content:
            raise forms.ValidationError("?挫毄???呺牓?挫＜?胳殧.")
        return content


class FestivalForm(forms.ModelForm):
    place = forms.CharField(required=False, max_length=200)
    organizer = forms.CharField(required=False, max_length=200)
    host = forms.CharField(required=False, max_length=200)
    sponsor = forms.CharField(required=False, max_length=200)
    address_road = forms.CharField(required=False, max_length=255)
    address_lot = forms.CharField(required=False, max_length=255)
    latitude = forms.DecimalField(required=False, max_digits=18, decimal_places=12)
    longitude = forms.DecimalField(required=False, max_digits=18, decimal_places=12)

    class Meta:
        model = Festival
        fields = [
            "title",
            "place",
            "start_date",
            "end_date",
            "description",
            "organizer",
            "host",
            "sponsor",
            "telephone",
            "homepage",
            "extra_info",
            "address_road",
            "address_lot",
            "latitude",
            "longitude",
            "data_reference_date",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "extra_info": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance and instance.location:
            self.fields["place"].initial = instance.location.name
            self.fields["address_road"].initial = instance.location.address_road
            self.fields["address_lot"].initial = instance.location.address_lot
            self.fields["latitude"].initial = instance.location.latitude
            self.fields["longitude"].initial = instance.location.longitude
        if instance:
            self.fields["organizer"].initial = instance.organizer_name
            self.fields["host"].initial = instance.host_name
            self.fields["sponsor"].initial = instance.sponsor_name

    def _upsert_location(self):
        place = self.cleaned_data.get("place", "").strip()
        address_road = self.cleaned_data.get("address_road", "").strip()
        address_lot = self.cleaned_data.get("address_lot", "").strip()
        latitude = self.cleaned_data.get("latitude")
        longitude = self.cleaned_data.get("longitude")
        has_any = any([place, address_road, address_lot, latitude is not None, longitude is not None])
        if not has_any:
            return None
        location, _ = Location.objects.get_or_create(
            name=place,
            address_road=address_road,
            address_lot=address_lot,
            latitude=latitude,
            longitude=longitude,
        )
        return location

    def _set_org_role(self, festival: Festival, role: str, name: str):
        FestivalOrganization.objects.filter(festival=festival, role=role).delete()
        cleaned = name.strip()
        if not cleaned:
            return
        org, _ = Organization.objects.get_or_create(name=cleaned)
        FestivalOrganization.objects.create(festival=festival, organization=org, role=role)

    def save(self, commit=True):
        festival = super().save(commit=False)
        location = self._upsert_location()
        festival.location = location
        if commit:
            festival.save()
        # update normalized org roles
        self._set_org_role(festival, FestivalOrganization.Role.ORGANIZER, self.cleaned_data.get("organizer", ""))
        self._set_org_role(festival, FestivalOrganization.Role.HOST, self.cleaned_data.get("host", ""))
        self._set_org_role(festival, FestivalOrganization.Role.SPONSOR, self.cleaned_data.get("sponsor", ""))
        return festival
