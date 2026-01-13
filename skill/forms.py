from django import forms 
from skill.models import Skill

class SkillForm(forms.ModelForm):

    class Meta:
        model = Skill
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-300',
                'placeholder': 'e.g. JavaScript, React, Python',
                'id': 'skill-name'
            })
        }



    
    def validate_unique(self):
        # Skip the unique check for name
        pass





