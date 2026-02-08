from django import forms
from datetime import date

class FindReplaceForm(forms.Form):
    FIELD_CHOICES = [
        ('store_name', 'Store Name'),
        ('item_product', 'Item/Product Name'),
        ('package_unit_type', 'Package/Unit Type'),
        ('date_of_purchase', 'Date of Purchase'),
    ]
    
    field_to_search = forms.ChoiceField(
        choices=FIELD_CHOICES,
        label='Field to Search In',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    find_value = forms.CharField(
        max_length=255,
        label='Find',
        help_text='The value to search for (leave blank to find empty/null values)',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Value to find...'
        })
    )
    
    replace_value = forms.CharField(
        max_length=255,
        label='Replace With',
        help_text='The new value to replace with',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'New value...'
        })
    )
    
    case_sensitive = forms.BooleanField(
        required=False,
        initial=False,
        label='Case Sensitive',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    preview_only = forms.BooleanField(
        required=False,
        initial=True,
        label='Preview Only (don\'t apply changes)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        field = cleaned_data.get('field_to_search')
        find_val = cleaned_data.get('find_value')
        replace_val = cleaned_data.get('replace_value')
        
        # For date fields, validate date format
        if field == 'date_of_purchase':
            if find_val:
                try:
                    date.fromisoformat(find_val)
                except ValueError:
                    raise forms.ValidationError({
                        'find_value': 'Please enter date in YYYY-MM-DD format (e.g., 2026-02-08)'
                    })
            
            if replace_val:
                try:
                    date.fromisoformat(replace_val)
                except ValueError:
                    raise forms.ValidationError({
                        'replace_value': 'Please enter date in YYYY-MM-DD format (e.g., 2026-02-08)'
                    })
        
        return cleaned_data
