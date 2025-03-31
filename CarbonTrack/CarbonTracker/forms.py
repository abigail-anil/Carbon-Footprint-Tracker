from django import forms
from django.core.validators import MinValueValidator

class ElectricityForm(forms.Form):
    """Form for electricity-related emissions."""
    location = forms.ChoiceField(choices=[])  # This will be updated dynamically
    value = forms.DecimalField()
    unit = forms.ChoiceField(choices=[('kWh', 'kWh'), ('MWh', 'MWh')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The location field choices will be updated from the view
        self.fields['location'].choices = kwargs.get('country_choices', [])


class FlightForm(forms.Form):
    """Form for flight-related emissions."""
    passengers = forms.IntegerField()
    departure_airport = forms.CharField(max_length=3)
    destination_airport = forms.CharField(max_length=3)

class ShippingForm(forms.Form):
    """Form for shipping-related emissions."""
    weight_value = forms.DecimalField()
    weight_unit = forms.ChoiceField(choices=[('kg', 'kg'), ('mt', 'mt')])
    distance_value = forms.DecimalField()
    distance_unit = forms.ChoiceField(choices=[('km', 'km'), ('mi', 'mi')])
    transport_method = forms.ChoiceField(choices=[('ship', 'Ship'), ('train', 'Train'), ('truck', 'Truck'), ('plane', 'Plane')])

class ActivityTypeForm(forms.Form):
    """Form for selecting the activity type"""
    activity_type = forms.ChoiceField(choices=[
        ('electricity', 'Electricity'),
        ('flight', 'Flight'),
        ('shipping', 'Shipping'),
        ('fuel_combustion', 'Fuel Combustion'),
        ('vehicle', 'Vehicle'),
    ])
    
    
class FuelCombustionForm(forms.Form):
    """Form for fuel combustion -related emissions."""
    fuel_source_type = forms.ChoiceField(label="Fuel Source Type")
    fuel_source_unit = forms.ChoiceField(label="Fuel Source Unit")
    fuel_source_value = forms.DecimalField(label="Fuel Source Value")
    
class SettingsForm(forms.Form):
    """Form for editing settings """
    electricity_threshold = forms.IntegerField(min_value=0, required=True)
    flight_threshold = forms.IntegerField(min_value=0, required=True)
    shipping_threshold = forms.IntegerField(min_value=0, required=True)
    fuel_threshold = forms.IntegerField(min_value=0, required=True)
    vehicle_threshold = forms.IntegerField(min_value=0, required=True)
    emission_check_frequency = forms.ChoiceField(choices=[('Never', 'Never'), ('Monthly', 'Monthly')], required=True)
    

class VehicleForm(forms.Form):
    """Form for vehicle-related emissions."""
    vehicle_make = forms.ChoiceField(choices=[], label="Vehicle Make")  # Populated dynamically
    vehicle_model = forms.ChoiceField(choices=[], label="Vehicle Model")  # Populated dynamically
    distance_value = forms.DecimalField(min_value=0, label="Distance Traveled")
    distance_unit = forms.ChoiceField(choices=[('km', 'Kilometers'), ('mi', 'Miles')], label="Distance Unit")

    def __init__(self, *args, **kwargs):
        # Populate vehicle_make and vehicle_model choices dynamically
        makes = kwargs.pop('makes', [])  # Pass makes from the view
        models = kwargs.pop('models', [])  # Pass models from the view
        super(VehicleForm, self).__init__(*args, **kwargs)

        # Update choices for vehicle_make and vehicle_model
        self.fields['vehicle_make'].choices = makes
        self.fields['vehicle_model'].choices = models