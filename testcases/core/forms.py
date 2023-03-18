from django import forms

from .models import UserQuestionAnswer


class UserQuestionAnswerForm(forms.ModelForm):

    class Meta:
        model = UserQuestionAnswer
        exclude = ('date_answering', 'subject')
