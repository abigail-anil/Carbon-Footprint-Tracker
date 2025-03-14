from django import forms 
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm 
from django.core import validators 

class UserSignUpForm(UserCreationForm): 
    email = forms.EmailField(validators=[validators.validate_email]) 
    min_length = 2 
    max_length = 30 
    message_lt_min = f"Should have at least {min_length} characters." 
    message_ht_max = f"Should have at most {max_length} characters." 
    name_regex='^[a-zA-Z ]+$' 
    name_message='The name accepts only letters!' 
    first_name = forms.CharField(validators=[ 
        validators.MinLengthValidator(min_length, message_lt_min), 
        validators.MaxLengthValidator(max_length, message_ht_max), 
        validators.RegexValidator(name_regex, name_message) ]) 
    last_name = forms.CharField(validators=[ 
        validators.MinLengthValidator(min_length), 
        validators.MaxLengthValidator(max_length), 
        validators.RegexValidator(name_regex, name_message) ]) 
        
    class Meta: 
        model = User 
        fields = [
            'username', 'first_name', 'last_name','email', 'password1', 'password2']