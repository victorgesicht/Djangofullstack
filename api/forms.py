from django import forms


class ContactForm(forms.form):
    email=forms.EmailField(max_length=100)
    message_body=forms.TextInput
