from django.urls import path
from .views import *

urlpatterns = [


    path('medicine-POST/', medicine_post), #used to add medicine
    path('medicine-GET/', medicine_get),
    path('medicine-update/', medicine_update),
    path('add_brestfeeding_record',add_brestfeeding_record),
    path('get_breastfeeding_records/', get_breastfeeding_records, name='get_breastfeeding_records'),
    path('submit_breastfeeding_records/', submit_breastfeeding_record, name='submit_breastfeeding_record'),

    # for exercise
    path('add_cal_burnt',add_calories_burnt),
    path('get_exercise/',get_exercises),
    path('add_exercise/',post_exercise),
    path('patch_exercise/',patch_exercise),

    #for diet tracker the cal data list is on antinatal

    path('diet-tracker-GET/', diet_tracker_get),
    path('diet-tracker-add-POST/', diet_tracker_post),
    path('add-meal',add_meal),

    #vaccination

    path('add-vaccine-admin',add_vaccine),        #admin
    path('get-vaccine',get_vaccine),
    path('post-vaccine',post_vaccine),

    #baby branin stimulation
    
    path('post-brain-stimulation',post_brain_stimulation),
    path('get-brain-stimulation',get_brain_stimulation),
    path('patch-babybrain',patch_baby_brain),
    path('post-diaper',post_diaper),
    path('post-sleep-pattern',post_Sleep_pattern),
    
]