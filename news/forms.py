from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model  = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name':  forms.TextInput(attrs={'class':'form-control','placeholder':'Your name / Izina ryawe'}),
            'email': forms.EmailInput(attrs={'class':'form-control','placeholder':'Email / Imeli'}),
            'body':  forms.Textarea(attrs={'class':'form-control','rows':4,'placeholder':'Write your comment…'}),
        }
