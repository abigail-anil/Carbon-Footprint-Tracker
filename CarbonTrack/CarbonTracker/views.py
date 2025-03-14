from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ElectricityForm, FlightForm, ShippingForm, ActivityTypeForm
from carbon_footprint_cal.emissions.calculations import Calculations
from carbon_footprint_cal.data_storage.data_storage import DataStorage
from carbon_footprint_cal.data_validation.validation import Validation
from decimal import Decimal
from .utils import get_supported_countries
import os
import boto3
import datetime

API_KEY = os.environ.get("CARBON_INTERFACE_API_KEY")
calculator = Calculations(API_KEY)
data_storage = DataStorage(table_name="CarbonFootprint")
validation = Validation()

@login_required
def calculate_emission(request):
    activity_form = ActivityTypeForm(request.GET or None)
    form = None
    result = None
    error = None

    # If the activity type is not already selected in the GET request, default to electricity
    if not request.GET.get('activity_type'):
        request.GET = request.GET.copy()
        request.GET['activity_type'] = 'electricity'

    activity_type = request.GET.get('activity_type', 'electricity')

    # Fetch supported countries from DynamoDB
    supported_countries = get_supported_countries()  # Fetch from DynamoDB 

    if request.method == 'POST':
        activity_form = ActivityTypeForm(request.POST)
        if activity_form.is_valid():
            activity_type = activity_form.cleaned_data['activity_type']

            if activity_type == 'electricity':
                # Create form here, passing the dynamic country choices.
                form = ElectricityForm(request.POST)
                form.fields['location'].choices = list(supported_countries.items())  # Dynamically update choices

            elif activity_type == 'flight':
                form = FlightForm(request.POST)
            elif activity_type == 'shipping':
                form = ShippingForm(request.POST)

            if form and form.is_valid():
                try:
                    # Calculate the emission
                    if activity_type == 'electricity':
                        country_code = form.cleaned_data['location']  # Get country code (e.g., 'US', 'IN')
                        value = form.cleaned_data['value']
                        unit = form.cleaned_data['unit']
                        api_data = {"location": country_code, "value": value, "unit": unit}
                        validation.validate_electricity_params(country_code, value, unit)
                        emission = calculator.calculate_electricity_emission(api_data)
                        input_params = {"location": country_code, "value": str(value), "unit": unit}

                    elif activity_type == 'flight':
                        passengers = form.cleaned_data['passengers']
                        legs = [{"departure_airport": form.cleaned_data['departure_airport'],
                                "destination_airport": form.cleaned_data['destination_airport']}]
                        validation.validate_flight_params(passengers, legs)
                        emission = calculator.calculate_flight_emission(passengers, legs)
                        input_params = {"passengers": passengers, "legs": legs}

                    elif activity_type == 'shipping':
                        weight_value = form.cleaned_data['weight_value']
                        weight_unit = form.cleaned_data['weight_unit']
                        distance_value = form.cleaned_data['distance_value']
                        distance_unit = form.cleaned_data['distance_unit']
                        transport_method = form.cleaned_data['transport_method']
                        validation.validate_shipping_params(weight_value, weight_unit, distance_value, distance_unit,
                                                            transport_method)
                        emission = calculator.calculate_shipping_emission(weight_value, weight_unit, distance_value,
                                                                         distance_unit, transport_method)
                        input_params = {"weight_value": str(weight_value), "weight_unit": weight_unit,
                                        "distance_value": str(distance_value), "distance_unit": distance_unit,
                                        "transport_method": transport_method}

                    else:
                        emission = None

                    if emission is not None:
                        data_storage.store_emission_data(request.user.username, activity_type, input_params, emission)
                        result = f"Emission: {emission:.2f} kg CO2e"
                    else:
                        error = "Emission calculation failed."
                except ValueError as e:
                    error = str(e)

    elif request.method == 'GET' and 'activity_type' in request.GET:
        activity_type = request.GET['activity_type']

        if activity_type == 'electricity':
            # Create form here with dynamically updated choices
            form = ElectricityForm()
            form.fields['location'].choices = list(supported_countries.items())  # Dynamically update choices
        elif activity_type == 'flight':
            form = FlightForm()
        elif activity_type == 'shipping':
            form = ShippingForm()

    return render(request, 'CarbonTracker/calculate.html', {
        'activity_form': activity_form,
        'form': form,
        'result': result,
        'error': error,
        'activity_type': activity_type
    })


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CarbonFootprint')

@login_required
def emission_reports(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    activity_type = request.GET.get('activity_type')

    # Convert ISO strings to datetime objects
    start_datetime = datetime.datetime.fromisoformat(start_date) if start_date else None
    end_datetime = datetime.datetime.fromisoformat(end_date) if end_date else None

    # DynamoDB filter expressions
    filter_expression = 'username = :username'
    expression_attribute_values = {':username': request.user.username}

    if start_datetime and end_datetime:
        # Convert datetime objects back to ISO strings for DynamoDB
        start_iso = start_datetime.isoformat()
        end_iso = end_datetime.isoformat()
        filter_expression += ' AND #ts BETWEEN :start_ts AND :end_ts'
        expression_attribute_values[':start_ts'] = start_iso
        expression_attribute_values[':end_ts'] = end_iso
        expression_attribute_names = {'#ts': 'timestamp'}

    if activity_type:
        filter_expression += ' AND activity_type = :activity_type'
        expression_attribute_values[':activity_type'] = activity_type

    response = table.scan(
        FilterExpression=filter_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names if start_datetime and end_datetime else None
    )

    emissions = []
    for item in response['Items']:
        emission = {
            'timestamp': datetime.datetime.fromisoformat(item['timestamp']),
            'activity_type': item['activityType'],
            'carbonKg': float(item['carbonKg']),
            'input_params': {},
        }

        input_params = item['inputParams']

        if item['activityType'] == 'electricity':
            emission['input_params'] = {
                'value': input_params['value']['S'],
                'location': input_params['location']['S'],
                'unit': input_params['unit']['S'],
            }
        elif item['activityType'] == 'flight':
            emission['input_params'] = {
                'passengers': input_params['passengers']['N'],
                'legs': [{
                    'departure_airport': leg['M']['departure_airport']['S'],
                    'destination_airport': leg['M']['destination_airport']['S'],
                } for leg in input_params['legs']['L']],
            }
        elif item['activityType'] == 'shipping':
            emission['input_params'] = {
                'transport_method': input_params['transport_method']['S'],
                'distance_value': input_params['distance_value']['S'],
                'weight_unit': input_params['weight_unit']['S'],
                'distance_unit': input_params['distance_unit']['S'],
                'weight_value': input_params['weight_value']['S'],
            }

        emissions.append(emission)

    total_emissions = sum(item['carbonKg'] for item in emissions)

    return render(request, 'CarbonTracker/emission_reports.html', {
        'emissions': emissions,
        'total_emissions': total_emissions,
        'start_date': start_date,
        'end_date': end_date,
        'activity_type': activity_type,
    })