from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django import forms
from .widgets import FengyuanChenDatePickerInput

# class DateInput(forms.DateInput):
#     input_type = 'date'

class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)

class SignupForm(UserCreationForm):

    def clean(self):
          email = self.cleaned_data.get('email')
          if User.objects.filter(email=email).exists():
                raise forms.ValidationError("This email is already registered.")
          return self.cleaned_data

    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
#        fields = ('username', 'email', 'password1', 'password2')

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('sex', 'date_of_birth', 'country', 'occupation')

    date_of_birth = forms.DateField(
        widget=FengyuanChenDatePickerInput(),
        input_formats=('%m/%d/%Y', )
        )

class ChangePswdForm(UserCreationForm):

        password1 = forms.CharField(label = 'New password', max_length=32, widget=forms.PasswordInput)

        class Meta:
            model = User
            fields = ('password1', 'password2')
