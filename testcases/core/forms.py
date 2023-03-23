from django import forms

from .models import Answer, TestingData


class TestingDataForm(forms.ModelForm):
    """Форма для создания объекта тестирования пользователя."""

    answer = forms.ModelChoiceField(
        queryset=Answer.objects,
        label='Варианты ответов',
        empty_label=None,
        widget=forms.RadioSelect(
            attrs={
                'onclick': 'terms_changed(this)',
            }
        ),
    )

    class Meta:
        model = TestingData
        fields = ['answer', ]

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('field_queryset', Answer.objects)
        super(TestingDataForm, self).__init__(*args, **kwargs)
        self.fields['answer'].queryset = queryset
