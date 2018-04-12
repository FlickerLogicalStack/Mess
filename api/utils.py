from django.apps import apps

from .models import Token

def base_validation(params, mandatory=[], optional=[]):
	ok, error = check_request_params(params, mandatory, optional)
	profile = profile_from_token(params["token"])

	return (error is None and profile is not None), error or "Wrong token", profile

def check_request_params(params, mandatory, optional):
	all_ = mandatory+optional

	for mandatory_param in mandatory:
		if mandatory_param not in params:
			return (False, f"No mandatory param: '{mandatory_param}'")

	for param in params:
		if param not in all_:
			return (False, f"Unknown param: '{param}'")

	return (True, None)

def profile_from_token(token):
	profiles_by_token = Token.objects.filter(token=token).filter()

	if profiles_by_token.count():
		return profiles_by_token.filter()[0:1].get().profile
	return None