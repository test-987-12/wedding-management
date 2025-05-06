from django import forms
from django.forms import inlineformset_factory
from .models import Checklist, ChecklistItem

class ChecklistForm(forms.ModelForm):
    """Form for creating and editing checklists"""
    class Meta:
        model = Checklist
        fields = ['title', 'description', 'is_template', 'wedding']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50', 'rows': 3}),
            'is_template': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50'}),
            'wedding': forms.Select(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # If user is admin, show all weddings they administer
            if user.profile.role == 'admin':
                self.fields['wedding'].queryset = user.administered_weddings.all()
            # If user is team member, show all weddings they're part of
            elif user.profile.role == 'team_member':
                wedding_ids = user.wedding_teams.values_list('wedding_id', flat=True)
                self.fields['wedding'].queryset = user.wedding_teams.values_list('wedding', flat=True)
            # If creating a template, wedding should be None
            if self.instance and self.instance.is_template:
                self.fields['wedding'].required = False
                self.fields['wedding'].widget = forms.HiddenInput()

class ChecklistItemForm(forms.ModelForm):
    """Form for creating and editing checklist items"""
    class Meta:
        model = ChecklistItem
        fields = ['title', 'description', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50', 'rows': 2}),
            'due_date': forms.DateInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50', 'type': 'date'}),
        }

# Create a formset for checklist items
ChecklistItemFormSet = inlineformset_factory(
    Checklist, 
    ChecklistItem,
    form=ChecklistItemForm,
    extra=3,
    can_delete=True
)
