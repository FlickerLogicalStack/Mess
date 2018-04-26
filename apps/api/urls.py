from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .api_methods import accounting, puddles, messages, files

app_name = "api"

urlpatterns = [
    path("register", accounting.register, name="register"),
    path("generateToken", accounting.generate_token, name="generate_token"),
    path("terminateToken", accounting.terminate_token, name="terminate_token"),
    path("getProfile", accounting.get_profile, name="get_profile"),
    path("editProfile", accounting.edit_profile, name="edit_profile"),
    path("setPassword", accounting.set_password, name="set_password"),
    path("sendFriendRequest", accounting.send_friend_request, name="send_friend_request"), 
    path("acceptFriendRequest", accounting.accept_friend_request, name="accept_friend_request"),
    path("rejectFriendRequest", accounting.cancel_friend_request, name="cancel_friend_request"),
    path("cancelFriendRequest", accounting.reject_friend_request, name="reject_friend_request"),
    path("removeFriends", accounting.remove_friends, name="remove_friends"),

    path("createPuddle", puddles.create_puddle, name="create_puddle"),
    path("deletePuddle", puddles.delete_puddle, name="delete_puddle"),
    path("editPuddle", puddles.edit_puddle, name="edit_puddle"),
    path("addUsersToPuddle", puddles.add_users_to_puddle, name="add_users_to_puddle"),
    path("removeUsersFromPuddle", puddles.remove_users_from_puddle, name="remove_users_to_puddle"),
    path("getPuddle", puddles.get_puddle, name="get_puddle"),
    path("getPuddles", puddles.get_puddles, name="get_puddles"),
    path("getPuddleMessages", puddles.get_puddle_messages, name="get_puddle_messages"),
    path("transferPuddleRights", puddles.transfer_puddle_rights, name="transfer_puddle_rights"),

    path("uploadFile", files.upload_file, name="upload_file"),
    path("downloadFile", files.download_file, name="download_file"),
    
    path("sendMessage", messages.send_message, name="send_message"),
    path("editMessage", messages.edit_message, name="edit_message"),
    path("deleteMessage", messages.delete_message, name="delete_message"),
]