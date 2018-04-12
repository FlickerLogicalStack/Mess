from django import forms

class LoginForm(forms.Form):
	username = forms.CharField(max_length=64,
		widget=forms.TextInput(
			attrs={
			"name": "username",
			"placeholder": "Username"})
		)
	password = forms.CharField(
		widget=forms.PasswordInput(
			attrs={
			"name": "password",
			"placeholder": "Password"})
		)

class RegisterForm(forms.Form):
	username = forms.CharField(max_length=64,
		widget=forms.TextInput(
			attrs={
			"placeholder": "Username"})
		)
	email = forms.EmailField(max_length=64,
		widget=forms.EmailInput(
			attrs={
			"placeholder": "Email"})
		)
	password = forms.CharField(
		widget=forms.PasswordInput(
			attrs={
			"placeholder": "Password"})
		)
	password_confirm = forms.CharField(
		widget=forms.PasswordInput(
			attrs={
			"placeholder": "Password Confirm"})
		)

class SendMessageForm(forms.Form):
	puddle_id = forms.IntegerField(widget=forms.HiddenInput())
	text = forms.CharField(widget=forms.Textarea(
		attrs={"class": "text-area"}))

	files = forms.FileField(required=False,
		widget=forms.ClearableFileInput(
			attrs={"multiple": True})
		)

class CreatePuddleForm(forms.Form):
	display_name = forms.CharField(required=False,
		widget=forms.TextInput(
			attrs={
			"placeholder": "Display Name",
			"name": "name"})
		)

	users_list = forms.ChoiceField(
		widget=forms.SelectMultiple(
			attrs={
			"name":"users"})
		)