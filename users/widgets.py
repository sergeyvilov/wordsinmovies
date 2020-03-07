from django.forms import DateInput

#datetimepicker for profile page
class FengyuanChenDatePickerInput(DateInput):
    template_name = 'widgets/fengyuanchen_datepicker.html'
