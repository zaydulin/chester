from django import forms

from mainapp.models import Messages


class MessageForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Введите ваше сообщение",
                "class": "chat__text",
                "id": "chat-text",
                "rows": "3",
                "maxlength": "200",
            }
        )
    )

    class Meta:
        model = Messages
        fields = ["user", "message", "events"]


class EventSearchForm(forms.Form):
    search_description = forms.CharField(
        max_length=100,  # Максимальная длина поискового запроса
        required=False,  # Поле не обязательно для заполнения
        widget=forms.TextInput(attrs={"placeholder": "     Поиск", "style": "font-weight: 700;color: white;"}),
    )
