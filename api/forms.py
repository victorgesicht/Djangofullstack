
import re

from django import forms
from django.core.validators import URLValidator
from django.utils.html import strip_tags

from .models import Comment, TrainingOffer

_SCRIPT_STYLE_BLOCK = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL
)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'body')


class TrainingOfferForm(forms.ModelForm):
    """Plain-text only. HTML is stripped, links must be http(s), and the
    hidden `website` field traps bots without telling them why."""

    website = forms.CharField(
        required=False,
        label='Website',
        widget=forms.TextInput(attrs={
            'class': 'ops-hp',
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
        }),
    )

    class Meta:
        model = TrainingOffer
        fields = ('callsign', 'contact', 'kind', 'link', 'message')
        widgets = {
            'callsign': forms.TextInput(attrs={'placeholder': '0xr3d', 'autocomplete': 'off'}),
            'contact': forms.TextInput(attrs={'placeholder': 'email, handle or matrix id'}),
            'link': forms.URLInput(attrs={'placeholder': 'https://forum.example/thread/123'}),
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'What are you offering? Voucher value, forum scope, collab idea…',
            }),
        }

    @staticmethod
    def _plain(value):
        value = _SCRIPT_STYLE_BLOCK.sub('', value or '')
        return strip_tags(value).replace('\x00', '').strip()

    def clean_callsign(self):
        value = self._plain(self.cleaned_data.get('callsign'))
        if len(value) < 2:
            raise forms.ValidationError('Give us a callsign (2+ characters).')
        return value

    def clean_contact(self):
        value = self._plain(self.cleaned_data.get('contact'))
        if len(value) < 3:
            raise forms.ValidationError('Add a way to reach you.')
        return value

    def clean_message(self):
        value = self._plain(self.cleaned_data.get('message'))
        if len(value) < 10:
            raise forms.ValidationError('Add a bit more detail (10+ characters).')
        return value

    def clean_link(self):
        link = (self.cleaned_data.get('link') or '').strip()
        if link:
            URLValidator(schemes=['http', 'https'])(link)
        return link
