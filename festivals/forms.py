from django import forms

from .models import Comment, Festival


class CommentForm(forms.ModelForm):
    nickname = forms.CharField(
        max_length=30,
        min_length=2,
        widget=forms.TextInput(attrs={"placeholder": "닉네임", "maxlength": 30}),
        error_messages={
            "required": "닉네임을 입력해주세요.",
            "min_length": "닉네임은 2자 이상 입력해주세요.",
        },
    )
    content = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": "축제에 대한 의견을 남겨주세요", "maxlength": 1000}
        ),
        error_messages={"required": "내용을 입력해주세요."},
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
            raise forms.ValidationError("내용을 입력해주세요.")
        return content


class FestivalForm(forms.ModelForm):
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
