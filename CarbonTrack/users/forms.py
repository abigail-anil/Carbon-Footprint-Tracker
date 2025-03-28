from django import forms 
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm 
from django.core import validators 

class UserSignUpForm(UserCreationForm):
    # Define additional fields with custom validators
    email = forms.EmailField(validators=[validators.validate_email])
    min_length = 2 
    max_length = 30 
    message_lt_min = f"Should have at least {min_length} characters."
    message_ht_max = f"Should have at most {max_length} characters."
    name_regex = '^[a-zA-Z ]+$'
    name_message = 'The name accepts only letters!'
    first_name = forms.CharField(validators=[
        validators.MinLengthValidator(min_length, message_lt_min),
        validators.MaxLengthValidator(max_length, message_ht_max),
        validators.RegexValidator(name_regex, name_message)
    ])
    last_name = forms.CharField(validators=[
        validators.MinLengthValidator(min_length),
        validators.MaxLengthValidator(max_length),
        validators.RegexValidator(name_regex, name_message)
    ])

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        # Initialize the form with standard behavior
        super(UserSignUpForm, self).__init__(*args, **kwargs)
        # Remove default inline help texts from fields
        self.fields['username'].help_text = ""
        self.fields['password1'].help_text = ""
        self.fields['password2'].help_text = ""
        # Add a tooltip for the username field
        self.fields['username'].widget.attrs.update({
            'title': "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        })
        # Add a tooltip for the first password field
        self.fields['password1'].widget.attrs.update({
            'title': (
                "Your password can't be too similar to your other personal information. "
                "Your password must contain at least 8 characters. "
                "Your password can't be a commonly used password. "
                "Your password can't be entirely numeric."
            )
        })
        # Add a tooltip for the second password (confirmation) field
        self.fields['password2'].widget.attrs.update({
            'title': "Enter the same password as before, for verification."
        })
