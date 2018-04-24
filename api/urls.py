from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .api_methods import accounting, puddles, messages, files

app_name = "api"

urlpatterns = [
	path("register", accounting.register, name="register"), # POST
	path("generateToken", accounting.generate_token, name="generate_token"), # GET
	path("terminateToken", accounting.terminate_token, name="terminate_token"), # POST
	path("getProfile", accounting.get_profile, name="get_profile"), # GET
	path("editProfile", accounting.edit_profile, name="edit_profile"), # POST
	path("setPassword", accounting.set_password, name="set_password"), # POST
	path("sendFriendRequest", accounting.send_friend_request, name="send_friend_request"), # POST
	path("acceptFriendRequest", accounting.accept_friend_request, name="accept_friend_request"), # POST
	path("rejectFriendRequest", accounting.cancel_friend_request, name="cancel_friend_request"), # POST
	path("cancelFriendRequest", accounting.reject_friend_request, name="reject_friend_request"), # POST
	path("removeFriends", accounting.remove_friends, name="remove_friends"), # POST

	path("createPuddle", puddles.create_puddle, name="create_puddle"), # POST
	path("deletePuddle", puddles.delete_puddle, name="delete_puddle"), # POST
	path("editPuddle", puddles.edit_puddle, name="edit_puddle"), # POST
	path("addUsersToPuddle", puddles.add_users_to_puddle, name="add_users_to_puddle"), # POST
	path("removeUsersFromPuddle", puddles.remove_users_from_puddle, name="remove_users_to_puddle"), # POST
	path("getPuddle", puddles.get_puddle, name="get_puddle"), # GET
	path("getPuddles", puddles.get_puddles, name="get_puddles"), # GET
	path("getPuddleMessages", puddles.get_puddle_messages, name="get_puddle_messages"), # GET

	path("uploadFile", files.upload_file, name="upload_file"), # GET
	path("downloadFile", files.download_file, name="download_file"), # GET
	
	path("sendMessage", messages.send_message, name="send_message"), # POST
	path("editMessage", messages.edit_message, name="edit_message"), # POST
	path("deleteMessage", messages.delete_message, name="delete_message"), # POST
	# path("getUnreaded", messages.get_unreaded, name="get_unreaded"), # GET
]