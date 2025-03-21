from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ElectricityForm, FlightForm, ShippingForm, ActivityTypeForm, FuelCombustionForm, SettingsForm, VehicleForm
from carbon_footprint_cal.emissions.calculations import Calculations
from carbon_footprint_cal.data_storage.data_storage import DataStorage
from carbon_footprint_cal.data_validation.validation import Validation
from decimal import Decimal
from .utils import get_supported_countries, subscribe_email_to_sns_topic, upload_chart_to_s3, unsubscribe_email_from_sns_topic
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.conf import settings as django_settings
import numpy as np #import numpy
import os
import boto3
from datetime import datetime
import matplotlib.pyplot as plt
import io
from io import BytesIO
import base64
import csv
import json
import logging
import boto3

logger = logging.getLogger(__name__)

def get_secret():
    secret_name = "CARBON_INTERFACE_API_KEY" 
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except client.exceptions.ResourceNotFoundException:
        logger.error("The requested secret was not found")
        return None
    except client.exceptions.InvalidRequestException:
        logger.error("The request was invalid due to: invalid request")
        return None
    except client.exceptions.InvalidParameterException:
        logger.error("The request had invalid params")
        return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    else:
        # Handle binary secrets if needed.
        return json.loads(base64.b64decode(get_secret_value_response['SecretBinary']))

secrets = get_secret()

if secrets:
    api_key = secrets.get("api_key")
    if api_key:
        calculator = Calculations(api_key)
    else:
        logger.error("API Key not found in secrets")
        # Handle missing api key. Perhaps render an error page.
        calculator = None #or handle it another way.
else:
    logger.error("Could not retrieve secrets")
    calculator = None #or handle it another way.



data_storage = DataStorage(table_name="CarbonFootprint")
validation = Validation()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('VehicleModels')

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
    supported_countries = get_supported_countries()

    if request.method == 'POST':
        activity_form = ActivityTypeForm(request.POST)
        if activity_form.is_valid():
            activity_type = activity_form.cleaned_data['activity_type']

            if activity_type == 'electricity':
                form = ElectricityForm(request.POST)
                form.fields['location'].choices = list(supported_countries.items())

            elif activity_type == 'flight':
                form = FlightForm(request.POST)
            elif activity_type == 'shipping':
                form = ShippingForm(request.POST)
            
            elif activity_type == 'fuel_combustion':
                form = FuelCombustionForm(request.POST)
                fuel_sources = calculator.get_fuel_sources_from_dynamodb()
                fuel_source_types = list(set([item['fuel_source_type'] for item in fuel_sources]))
                form.fields['fuel_source_type'].choices = [(source, source) for source in fuel_source_types]

                if request.POST.get('fuel_source_type'):
                    selected_source_type = request.POST.get('fuel_source_type')
                    
                    available_units = calculator.get_units_by_fuel_type(selected_source_type)
                    form.fields['fuel_source_unit'].choices = [(unit, unit) for unit in available_units]
                    
            elif activity_type == 'vehicle':
                form = VehicleForm(request.POST)
                makes = calculator.get_vehicle_makes_from_dynamodb()

                if makes:
                    form.fields['vehicle_make'].choices = [(make, make) for make in makes]

                if request.POST.get('vehicle_make'):
                    vehicle_make = request.POST.get('vehicle_make')
                    models = calculator.get_vehicle_models_from_dynamodb(vehicle_make)
                    form.fields['vehicle_model'].choices = [(model['id'], model['name']) for model in models]

            
            if form and form.is_valid():
                try:
                    if activity_type == 'electricity':
                        country_code = form.cleaned_data['location']
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
                                        
                    elif activity_type == 'fuel_combustion':
                        fuel_source_type = form.cleaned_data['fuel_source_type']
                        fuel_source_unit = form.cleaned_data['fuel_source_unit']
                        fuel_source_value = int(form.cleaned_data['fuel_source_value']) 
                        validation.validate_fuel_combustion_params(fuel_source_value)
                        emission = calculator.calculate_fuel_combustion_emission(fuel_source_type, fuel_source_unit, fuel_source_value)

                        if emission is not None:
                            input_params = {
                                "fuel_source_type": fuel_source_type,
                                "fuel_source_unit": fuel_source_unit,
                                "fuel_source_value": str(fuel_source_value)
                            }
                    
                    elif activity_type == 'vehicle':
                        distance_value = form.cleaned_data['distance_value']
                        distance_unit = form.cleaned_data['distance_unit']
                        vehicle_model_id = form.cleaned_data['vehicle_model']
                        
                        emission = calculator.calculate_vehicle_emission(distance_value, distance_unit, vehicle_model_id)
                        
                        # Fetch the vehicle model name
                        vehicle_make = request.POST.get('vehicle_make')
                        models = calculator.get_vehicle_models_from_dynamodb(vehicle_make)
                        vehicle_model_name = None  # Initialize to None

                        for model in models:
                            if str(model['id']).strip() == str(vehicle_model_id).strip():
                                vehicle_model_name = model['name']  # Store the name directly
                                #print(f"vehicle_model_name = {vehicle_model_name}")
                                break  # Exit the loop once found

                        emission = calculator.calculate_vehicle_emission(distance_value, distance_unit, vehicle_model_id)
                        #print(f"vehicle_model_name = {vehicle_model_name}")
                        input_params = {
                        "distance_value": str(distance_value),
                        "distance_unit": distance_unit,
                        "vehicle_model": vehicle_model_name,  # Store the name
                        }
                        
                        #input_params = {"distance_value": str(distance_value), "distance_unit": distance_unit, "vehicle_model_id": vehicle_model_id}


                    else:
                        emission = None

                    if emission is not None:
                        data_storage.store_emission_data(request.user.username, activity_type, input_params, emission)
                        result = f"Emission: {emission:.2f} kg CO2e"
                    else:
                        error = "Emission calculation failed."
                except ValueError as e:
                    error = str(e)
                except AttributeError as e:
                    error = "API key retrieval or calculation failed. Please check logs."
                    logger.error(f"Attribute error during calculation: {e}")

    elif request.method == 'GET' and 'activity_type' in request.GET:
        activity_type = request.GET['activity_type']

        if activity_type == 'electricity':
            form = ElectricityForm()
            form.fields['location'].choices = list(supported_countries.items())
        elif activity_type == 'flight':
            form = FlightForm()
        elif activity_type == 'shipping':
            form = ShippingForm()
        elif activity_type == 'fuel_combustion':
            form = FuelCombustionForm()
            fuel_source_types = calculator.get_unique_fuel_source_types()
            form.fields['fuel_source_type'].choices = [(source, source) for source in fuel_source_types]

            if request.GET.get('fuel_source_type'):
                selected_source_type = request.GET.get('fuel_source_type')
                available_units = calculator.get_units_by_fuel_type(selected_source_type)
                form.fields['fuel_source_unit'].choices = [(unit, unit) for unit in available_units]
            else:
                if fuel_source_types:
                    selected_source_type = fuel_source_types[0]
                    available_units = calculator.get_units_by_fuel_type(selected_source_type)
                    form.fields['fuel_source_unit'].choices = [(unit, unit) for unit in available_units]
                    
        elif activity_type == 'vehicle':
            form = VehicleForm()
            makes = calculator.get_vehicle_makes_from_dynamodb()

            if makes:
                #form.fields['vehicle_make'].choices = [(make, make) for make in makes]
                form.fields['vehicle_make'].choices = [('', '---------')] + [(make, make) for make in makes] #added default option to make

                if request.GET.get('vehicle_make'):
                    vehicle_make = request.GET.get('vehicle_make')
                    models = calculator.get_vehicle_models_from_dynamodb(vehicle_make)
                    form.fields['vehicle_model'].choices = [('', '---------')] + [(model['id'], model['name']) for model in models]
                    #form.fields['vehicle_model'].choices = [(model['id'], model['name']) for model in models]
                else:
                    form.fields['vehicle_model'].choices = [('', '---------')] #set model choices to default if no make is selected.
			

    return render(request, 'CarbonTracker/calculate.html', {
        'activity_form': activity_form,
        'form': form,
        'result': result,
        'error': error,
        'activity_type': activity_type
    })

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CarbonFootprint')

def generate_chart(emissions, chart_type="line"):
    plt.figure(figsize=(12, 6))

    if not emissions:
        print(f"No emissions data available for {chart_type} chart")
        return None

    if chart_type == "line":
        emissions.sort(key=lambda x: x["timestamp"])
        timestamps = [e["timestamp"] for e in emissions]
        emissions_values = [e["carbonKg"] for e in emissions]

        plt.plot(timestamps, emissions_values, marker="o", linestyle="-", color="b")
        plt.xlabel("Date")
        plt.ylabel("Emissions (kg CO2e)")
        plt.xticks(rotation=45)
        plt.grid(True)

    elif chart_type == "bar":
        activity_types = [e["activity_type"] for e in emissions]
        emissions_values = [e["carbonKg"] for e in emissions]

        plt.bar(activity_types, emissions_values, color="b")
        plt.xlabel("Activity Type")
        plt.ylabel("Emissions (kg CO2e)")

    elif chart_type == "pie":
        activity_totals = {}
        for e in emissions:
            activity = e["activity_type"]
            carbon = e["carbonKg"]
            activity_totals[activity] = activity_totals.get(activity, 0) + carbon

        total_emissions = sum(activity_totals.values())
        if total_emissions == 0:
            return None

        labels = list(activity_totals.keys())
        values = list(activity_totals.values())

        plt.figure(figsize=(8, 6))
        wedges, texts, autotexts = plt.pie(values, autopct='%1.3f%%', textprops={'fontsize': 10})
        plt.axis('equal')

        legend_labels = [f"{label} ({value / total_emissions * 100:.3f}%)" for label, value in activity_totals.items()]
        plt.legend(wedges, legend_labels, loc="best")

    else:
        return None

    # Save and return the chart for all chart types
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    chart_image = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    plt.clf()

    return chart_image
    
def filter_and_sort_emissions(emissions, start_date, end_date, activity_type, sort_by, sort_order):
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    filtered_emissions = []
    for emission in emissions:
        timestamp_str = emission["timestamp"]
        timestamp_dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f").date()

        print(f"Timestamp: {timestamp_dt}, Start: {start_date}, End: {end_date}")

        if start_date and timestamp_dt < start_date:
            continue
        #modified line to be less than or equal to.
        if end_date and timestamp_dt > end_date:
            continue

        print(f"Activity: {emission['activityType']}, Filter: {activity_type}")

        if activity_type and emission["activityType"] != activity_type:
            continue

        emission["carbonKg"] = float(emission["carbonKg"]) if isinstance(emission["carbonKg"], Decimal) else emission["carbonKg"]
        filtered_emissions.append(emission)

    print(f"Filtered records count: {len(filtered_emissions)}")

    reverse = sort_order == "desc"
    filtered_emissions.sort(key=lambda x: x["timestamp"])  # Always sort by timestamp


    return filtered_emissions
    
s3_client = boto3.client('s3')

def generate_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object"""
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except Exception as e:
        logging.error(e)
        return None
    return response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CarbonFootprint')

@login_required
def emission_reports(request):
    start_date = request.GET.get('start_date', '')  # Default to empty string
    end_date = request.GET.get('end_date', '')    # Default to empty string
    activity_type = request.GET.get('activity_type', '')
    sort_by = request.GET.get('sort_by', 'timestamp')
    sort_order = request.GET.get('sort_order', 'asc')

    emissions_display = []
    total_emissions = 0
    chart_image_line = None
    chart_image_bar = None
    chart_image_pie = None

    s3_line_url = None
    s3_bar_url = None
    s3_pie_url = None

    if start_date and end_date: # MODIFIED: Check if both start_date and end_date are provided
        # User has selected dates, proceed with filtering
        filter_expression = 'userId = :user_id'
        expression_attribute_values = {':user_id': request.user.username}
        expression_attribute_names = None

        print(f"Start Date String: {start_date}")
        print(f"End Date String: {end_date}")

        try:
            #start_datetime = datetime.fromisoformat(start_date)
            start_datetime = datetime.fromisoformat(start_date) if start_date else None
            #end_datetime = datetime.fromisoformat(end_date)
            end_datetime = datetime.fromisoformat(end_date) if end_date else None
            print(f"Start Date isoString: {start_datetime}")
            print(f"End Date isoString: {end_datetime}")
            if end_datetime:
                # Extend the end date to 23:59:59 to include the whole day
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
    
            start_iso = start_datetime.isoformat()
            end_iso = end_datetime.isoformat()
            filter_expression += ' AND #ts BETWEEN :start_ts AND :end_ts'
            expression_attribute_values[':start_ts'] = start_iso
            expression_attribute_values[':end_ts'] = end_iso
            expression_attribute_names = {'#ts': 'timestamp'}
        except ValueError:
            pass

        scan_params = {
            "FilterExpression": filter_expression,
            "ExpressionAttributeValues": expression_attribute_values,
        }

        if expression_attribute_names:
            scan_params["ExpressionAttributeNames"] = expression_attribute_names

        response = table.scan(**scan_params)
        emissions_data = response.get('Items', [])

        emissions = []
        for item in emissions_data:
            emission = {
                'timestamp': item.get('timestamp', 'N/A'),
                'activityType': item.get('activityType', 'N/A'),
                'carbonKg': item.get('carbonKg', 'N/A'),
                'inputParams': item.get('inputParams', None)
            }

            if isinstance(emission['inputParams'], str):
                try:
                    emission['inputParams'] = json.loads(emission['inputParams'])
                except json.JSONDecodeError:
                    emission['inputParams'] = {}

            emissions.append(emission)

        filtered_emissions = filter_and_sort_emissions(emissions, start_date, end_date, activity_type, sort_by, sort_order)

        for item in filtered_emissions:
            emission = {
                'timestamp': datetime.fromisoformat(item['timestamp']),
                'activity_type': item['activityType'],
                #'carbonKg': float(item['carbonKg']),
                'carbonKg': round(float(item['carbonKg']), 2),
                'input_params': {},
            }

            input_params = item.get('inputParams', {})

            if item['activityType'] == 'electricity':
                emission['input_params'] = {
                    'value': input_params.get('value', 'N/A'),
                    'location': input_params.get('location', 'N/A'),
                    'unit': input_params.get('unit', 'N/A'),
                }
            elif item['activityType'] == 'flight':
                emission['input_params'] = {
                    'passengers': input_params.get('passengers', 'N/A'),
                    'legs': [{
                        'departure_airport': leg.get('departure_airport', 'N/A'),
                        'destination_airport': leg.get('destination_airport', 'N/A'),
                    } for leg in input_params.get('legs', [])],
                }
            elif item['activityType'] == 'shipping':
                emission['input_params'] = {
                    'transport_method': input_params.get('transport_method', 'N/A'),
                    'distance_value': input_params.get('distance_value', 'N/A'),
                    'weight_unit': input_params.get('weight_unit', 'N/A'),
                    'distance_unit': input_params.get('distance_unit', 'N/A'),
                    'weight_value': input_params.get('weight_value', 'N/A'),
                }
            elif item['activityType'] == 'fuel_combustion':
                emission['input_params'] = {
                    'fuel_source_type': input_params.get('fuel_source_type', 'N/A'),
                    'fuel_source_unit': input_params.get('fuel_source_unit', 'N/A'),
                    'fuel_source_value': input_params.get('fuel_source_value', 'N/A'),
                }
            elif item['activityType'] == 'vehicle':
                
                emission['input_params'] = {
                    'distance_value': input_params.get('distance_value', 'N/A'),
                    'distance_unit': input_params.get('distance_unit', 'N/A'),
                    'vehicle_model': input_params.get('vehicle_model', 'N/A'),
                }
            emissions_display.append(emission)

        #total_emissions = sum(item['carbonKg'] for item in emissions_display)
        total_emissions = round(sum(item['carbonKg'] for item in emissions_display), 2)
        chart_image_line = generate_chart(emissions_display, "line")
        chart_image_bar = generate_chart(emissions_display, "bar")
        chart_image_pie = generate_chart(emissions_display, "pie")
        
        if chart_image_line:
            object_key = f"{request.user.username}/emissions_line.png"
            s3_line_url = generate_presigned_url(settings.S3_BUCKET_NAME, object_key)
            upload_chart_to_s3(request.user.username, chart_image_line, "emissions_line") #uploading line chart


        if chart_image_bar:
            object_key = f"{request.user.username}/emissions_bar.png"
            s3_bar_url = generate_presigned_url(settings.S3_BUCKET_NAME, object_key)
            upload_chart_to_s3(request.user.username, chart_image_bar, "emissions_bar") #uploading bar chart

            

        if chart_image_pie:
            object_key = f"{request.user.username}/emissions_pie.png"
            s3_pie_url = generate_presigned_url(settings.S3_BUCKET_NAME, object_key)
            upload_chart_to_s3(request.user.username, chart_image_pie, "emissions_pie") #uploading pie chart

    # If no dates are selected, emissions_display will be empty, total_emissions will be 0, and chart_image will be None (MODIFIED: No else block, allowing default values to remain)

    return render(request, 'CarbonTracker/emission_reports.html', {
        'emissions': emissions_display,
        'total_emissions': total_emissions,
        'start_date': start_date,
        'end_date': end_date,
        'activity_type': activity_type,
        'chart_image_line': chart_image_line,
        'chart_image_bar': chart_image_bar,
        'chart_image_pie': chart_image_pie,
        's3_line_url': s3_line_url,
        's3_bar_url': s3_bar_url,
        's3_pie_url': s3_pie_url,
        'sort_by': sort_by,
        'sort_order': sort_order,
    })


    
@login_required
def export_csv(request):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    activity_type = request.GET.get('activity_type', '')
    sort_by = request.GET.get('sort_by', 'timestamp')
    sort_order = request.GET.get('sort_order', 'asc')

    emissions_display = []
    total_emissions = 0

    if start_date and end_date:
        filter_expression = 'userId = :user_id'
        expression_attribute_values = {':user_id': request.user.username}
        expression_attribute_names = None

        try:
            start_datetime = datetime.fromisoformat(start_date) if start_date else None
            end_datetime = datetime.fromisoformat(end_date) if end_date else None

            if end_datetime:
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)

            start_iso = start_datetime.isoformat()
            end_iso = end_datetime.isoformat()
            filter_expression += ' AND #ts BETWEEN :start_ts AND :end_ts'
            expression_attribute_values[':start_ts'] = start_iso
            expression_attribute_values[':end_ts'] = end_iso
            expression_attribute_names = {'#ts': 'timestamp'}
        except ValueError:
            pass

        scan_params = {
            "FilterExpression": filter_expression,
            "ExpressionAttributeValues": expression_attribute_values,
        }

        if expression_attribute_names:
            scan_params["ExpressionAttributeNames"] = expression_attribute_names

        response = table.scan(**scan_params)
        emissions_data = response.get('Items', [])

        emissions = []
        for item in emissions_data:
            emission = {
                'timestamp': item.get('timestamp', 'N/A'),
                'activityType': item.get('activityType', 'N/A'),
                'carbonKg': item.get('carbonKg', 'N/A'),
                'inputParams': item.get('inputParams', None)
            }

            input_params = emission.get('inputParams', None)

            if isinstance(input_params, str):
                try:
                    input_params = json.loads(input_params)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON for item: {item}")
                    input_params = {}
            elif input_params is None:
                input_params = {}

            emission['inputParams'] = input_params

            emissions.append(emission)

        filtered_emissions = filter_and_sort_emissions(emissions, start_date, end_date, activity_type, sort_by, sort_order)

        for item in filtered_emissions:
            emission = {
                'timestamp': datetime.fromisoformat(item['timestamp']),
                'activity_type': item['activityType'],
                'carbonKg': round(float(item['carbonKg']), 2),
                'input_params': {},
            }

            input_params = item.get('inputParams', {})

            if item['activityType'] == 'electricity':
                emission['input_params'] = {
                    'value': input_params.get('value', 'N/A'),
                    'location': input_params.get('location', 'N/A'),
                    'unit': input_params.get('unit', 'N/A'),
                }
            elif item['activityType'] == 'flight':
                emission['input_params'] = {
                    'passengers': input_params.get('passengers', 'N/A'),
                    'legs': [{
                        'departure_airport': leg.get('departure_airport', 'N/A'),
                        'destination_airport': leg.get('destination_airport', 'N/A'),
                    } for leg in input_params.get('legs', [])],
                }
            elif item['activityType'] == 'shipping':
                emission['input_params'] = {
                    'transport_method': input_params.get('transport_method', 'N/A'),
                    'distance_value': input_params.get('distance_value', 'N/A'),
                    'weight_unit': input_params.get('weight_unit', 'N/A'),
                    'distance_unit': input_params.get('distance_unit', 'N/A'),
                    'weight_value': input_params.get('weight_value', 'N/A'),
                }
            elif item['activityType'] == 'fuel_combustion':
                emission['input_params'] = {
                    'transport_method': input_params.get('transport_method', 'N/A'),
                    'distance_value': input_params.get('distance_value', 'N/A'),
                    'weight_unit': input_params.get('weight_unit', 'N/A'),
                    'distance_unit': input_params.get('distance_unit', 'N/A'),
                    'weight_value': input_params.get('weight_value', 'N/A'),
                }
            elif item['activityType'] == 'vehicle':
                emission['input_params'] = {
                    'distance_value': input_params.get('distance_value', 'N/A'),
                    'distance_unit': input_params.get('distance_unit', 'N/A'),
                    'vehicle_model_id': input_params.get('vehicle_model_id', 'N/A'),
                }
            emissions_display.append(emission)

    if not emissions_display:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="emissions_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['No data found'])
        return response

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="emissions_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Activity Type', 'Input Parameters', 'Emission (kg CO2e)'])
    for emission in emissions_display:
        writer.writerow([
            emission['timestamp'].isoformat(),
            emission['activity_type'],
            str(emission['input_params']),
            f"{emission['carbonKg']:.2f}",
        ])
        
        total_emissions += emission['carbonKg']  # Accumulate emissions

    # Append the total emissions row
    writer.writerow(['', '', 'Total Emissions:', f"{total_emissions:.2f}"])
    return response
    
settings_table = dynamodb.Table('user_settings')

@login_required
def settings_view(request):
    user_id = request.user.username

    try:
        settings_response = settings_table.get_item(Key={'userId': user_id})
        settings_data = settings_response.get('Item', {
            'electricity_threshold': 0,
            'flight_threshold': 0,
            'shipping_threshold': 0,
            'fuel_threshold': 0,
            'vehicle_threshold': 0,
            'emission_check_frequency': 'Never',
            'subscribed': False
        })

        if request.method == 'POST':
            if 'subscribe' in request.POST:
                topic_arn = django_settings.SNS_TOPIC_ARN
                email = request.user.email

                if topic_arn and email:
                    subscribe_email_to_sns_topic(topic_arn, email)
                    settings_table.update_item(
                        Key={'userId': user_id},
                        UpdateExpression="SET subscribed = :s",
                        ExpressionAttributeValues={':s': True}
                    )
                    settings_data['subscribed'] = True
                    message = 'Subscription successful! Please check your email to confirm your subscription.'
                else:
                    message = 'Subscription failed. SNS topic or email not configured.'
                return render(request, 'CarbonTracker/settings.html', {'settings': settings_data, 'message': message})

            elif 'unsubscribe' in request.POST:
                topic_arn = django_settings.SNS_TOPIC_ARN
                email = request.user.email

                if topic_arn and email:
                    unsubscribe_email_from_sns_topic(topic_arn, email)
                    settings_table.update_item(
                        Key={'userId': user_id},
                        UpdateExpression="SET subscribed = :s",
                        ExpressionAttributeValues={':s': False}
                    )
                    settings_data['subscribed'] = False
                    message = 'Unsubscription successful.'
                else:
                    message = 'Unsubscription failed. SNS topic or email not configured.'

                form = SettingsForm(initial=settings_data)
                return render(request, 'CarbonTracker/settings.html', {'settings': settings_data, 'message': message, 'form': form})

            else:
                form = SettingsForm(request.POST)
                if form.is_valid():
                    cleaned_data = form.cleaned_data
                    settings_table.update_item(
                        Key={'userId': user_id},
                        UpdateExpression="set electricity_threshold = :e, flight_threshold = :f, shipping_threshold = :s, emission_check_frequency = :c, fuel_threshold = :fu, vehicle_threshold =:v",
                        ExpressionAttributeValues={
                            ':e': cleaned_data['electricity_threshold'],
                            ':f': cleaned_data['flight_threshold'],
                            ':s': cleaned_data['shipping_threshold'],
                            ':fu': cleaned_data['fuel_threshold'],
                            ':v': cleaned_data['vehicle_threshold'],
                            ':c': cleaned_data['emission_check_frequency']
                        },
                        ReturnValues="UPDATED_NEW"
                    )
                    settings_data.update(cleaned_data)
                    message = 'Settings saved successfully.'
                    return render(request, 'CarbonTracker/settings.html', {'form': SettingsForm(initial=settings_data), 'settings': settings_data, 'message': message})

                else:
                    return render(request, 'CarbonTracker/settings.html', {'form': form, 'settings': settings_data, 'form_errors': form.errors})

        form = SettingsForm(initial=settings_data)
        return render(request, 'CarbonTracker/settings.html', {'form': form, 'settings': settings_data})

    except Exception as e:
        logger.error(f"Settings error: {e}")
        return render(request, 'CarbonTracker/settings.html', {'error': 'An unexpected error occurred.'})