from django import forms
from .models import Comment, PaperComment

class CommentForm(forms.ModelForm):
    class Meta:
        model  = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name':  forms.TextInput(attrs={'class':'form-control','placeholder':'Your name / Izina ryawe'}),
            'email': forms.EmailInput(attrs={'class':'form-control','placeholder':'Email / Imeli'}),
            'body':  forms.Textarea(attrs={'class':'form-control','rows':4,'placeholder':'Write your comment…'}),
        }


class PaperCommentForm(forms.ModelForm):
    class Meta:
        model  = PaperComment
        fields = ['name', 'email', 'affiliation', 'body']
        widgets = {
            'name':        forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name / Izina ryawe',
            }),
            'email':       forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email / Imeli',
            }),
            'affiliation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Institution / University (optional)',
            }),
            'body':        forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your comment or question about this paper…',
            }),
        }
