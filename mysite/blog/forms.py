from django import forms


class EmailPostForm(forms.Form):
    subject = forms.CharField(max_length=25)
    email_to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)
