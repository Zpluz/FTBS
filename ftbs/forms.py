from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=20)
    password = forms.CharField(label='password', max_length=20)


class SignUpForm(forms.Form):
    username = forms.CharField(label='username', max_length=20)
    password = forms.CharField(label='password', max_length=20)
    telephone = forms.CharField(label='telephone', max_length=20)
    email = forms.CharField(label='email', max_length=20)


class FlightSearchForm(forms.Form):
    code = forms.CharField(max_length=6, required=False)
    start = forms.CharField(max_length=6, required=False)
    destination = forms.CharField(max_length=6, required=False)
    date = forms.DateField()


class CandidateForm(forms.Form):
    gender_choices = (
        (0, "女"),
        (1, "男"),
    )
    name = forms.CharField(max_length=20)
    identity = forms.CharField(max_length=18, min_length=18)
    gender = forms.ChoiceField(choices=gender_choices, required=False)
    contact = forms.CharField(required=False)
