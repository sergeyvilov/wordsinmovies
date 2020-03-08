from django import forms
from .widgets import CosySelector
#from dal import autocomplete

class SearchForm(forms.Form):

    lang1 = forms.ChoiceField(label='Input language', choices=(('en','English'),('ru','Russian'), ('fr','French')),
        widget=CosySelector( attrs={'id': 'first_language'}))

    lang2 = forms.ChoiceField(label='Output language', choices=(('ru','Russian'),('en','English'), ('fr','French'),),
        widget=CosySelector( attrs={'id': 'second_language'}))

    # res_per_page = forms.ChoiceField(label='Results per page:', choices=((10,10),(25,25), (50,50), (75,75), (100,100),),
    #     widget=forms.Select( attrs={'id': 'res_per_pages_selector'}))

    res_per_page = forms.ChoiceField(label='Results per page:', choices=((10,10),(25,25), (50,50), (75,75), (100,100),),
         widget=CosySelector( attrs={'id': 'res_per_pages_selector'}))

    # sci_mode = forms.BooleanField(label='Scientific mode', required=False)

    pos_tags = forms.BooleanField(label='Show POS tags', required=False)

    query = forms.CharField(label='', max_length=100, required=False)
