from django import forms

class ElectricityForm(forms.Form):
    location = forms.ChoiceField(choices=[])  # This will be updated dynamically
    value = forms.DecimalField()
    unit = forms.ChoiceField(choices=[('kWh', 'kWh'), ('MWh', 'MWh')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The location field choices will be updated from the view
        self.fields['location'].choices = kwargs.get('country_choices', [])


class FlightForm(forms.Form):
    passengers = forms.IntegerField()
    departure_airport = forms.CharField(max_length=3)
    destination_airport = forms.CharField(max_length=3)

class ShippingForm(forms.Form):
    weight_value = forms.DecimalField()
    weight_unit = forms.ChoiceField(choices=[('kg', 'kg'), ('mt', 'mt')])
    distance_value = forms.DecimalField()
    distance_unit = forms.ChoiceField(choices=[('km', 'km'), ('mi', 'mi')])
    transport_method = forms.ChoiceField(choices=[('ship', 'Ship'), ('train', 'Train'), ('truck', 'Truck'), ('plane', 'Plane')])

class ActivityTypeForm(forms.Form):
    activity_type = forms.ChoiceField(choices=[
        ('electricity', 'Electricity'),
        ('flight', 'Flight'),
        ('shipping', 'Shipping'),
    ])