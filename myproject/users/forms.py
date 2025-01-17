from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm , PasswordResetForm


class UserRegisterForm(UserCreationForm):
	username = forms.EmailField()
	

	class Meta:
		model = User
		fields = ['username','first_name','last_name','password1', 'password2']

class UserUpdateForm(forms.ModelForm):
	
	class Meta:
		model = User
		fields = ['first_name','last_name',]
  
  
class ResetPasswd(PasswordResetForm):
    # username = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username']


