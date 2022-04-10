from django import forms
from allauth.account.forms import SignupForm

from .models import Profile

class RegistrationForm(SignupForm):

    first_name = forms.CharField(max_length = 70 , required = True, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length = 70 , required = True, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))

    avatar = forms.ImageField(required=False)

    def save(self, request):

        user = super(RegistrationForm, self).save(request)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        avatar = request.FILES.get('avatar')

        if avatar is not None:
            Profile.objects.create(user=user, avatar=avatar)
        else:
            Profile.objects.create(user=user)
        
        user.save()

        return user
