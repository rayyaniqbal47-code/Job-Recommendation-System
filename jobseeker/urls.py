from django.urls import path
from jobseeker import views

urlpatterns = [
    path('profile/' , views.profile , name='profile'),
    path('edit_jobseekerprofile/' , views.edit_jobseekerprofile , name='edit_jobseekerprofile'),

    path('profile/add_experience/' , views.add_experience , name='add_experience'),
    path('profile/edit_experience/<int:pk>/' , views.edit_experience , name='edit_experience'),
    path('profile/delete_experience/<int:pk>/' , views.delete_experience , name='delete_experience'),

    path('profile/add_education/' , views.add_education , name='add_education'),
    path('profile/edit_education/<int:pk>/' , views.edit_education , name='edit_education'),
    path('profile/delete_education/<int:pk>/' , views.delete_education , name='delete_education'),

    path('profile/add_skill/' , views.add_skill , name='add_skill'),
    path('profile/delete_skill/<int:pk>/' , views.delete_skill , name='delete_skill'),

    path('profile/apply_job/<int:job_id>/' , views.apply_job , name='apply_job'),

    path('profile/list_bookmarks/' , views.list_bookmarks , name='list_bookmarks'),
    path('profile/bookmarks/add/<int:job_id>/', views.add_bookmark, name='add_bookmark'),
    path('profile/bookmarks/remove/<int:job_id>/', views.remove_bookmark, name='remove_bookmark'),

    path('profile/my_application/' , views.my_application , name='my_application'),

    path("profile/skills/autocomplete/", views.skill_autocomplete, name="skill_autocomplete"),




]




