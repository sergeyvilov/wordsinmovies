from django.forms import widgets

class CosySelector(widgets.Select):
    template_name = 'widgets/CosySelector.html'
    # template_name = 'widgets/Selector_base.html'
