
import boto3
def store_vehicle_models_in_dynamodb(vehicle_models):
    """
    Stores a list of vehicle model dictionaries in DynamoDB.

    Args:
        vehicle_models: A list of dictionaries, where each dictionary represents a vehicle model.
    """

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('VehicleModels')  # Replace 'VehicleModels' with your table name

    with table.batch_writer() as batch:
        for model in vehicle_models:
            model_data = model['data']
            model_id = model_data['id']
            attributes = model_data['attributes']

            item = {
                'model_id': model_id,
                'name': attributes['name'],
                'year': attributes['year'],
                'vehicle_make': attributes['vehicle_make']
            }

            batch.put_item(Item=item)

models_data = [{'data': {'id': '6338b19b-b92c-4fb5-baff-f35934820d7d', 'type': 'vehicle_model', 'attributes': {'name': 'GLA250 4matic', 'year': 2021, 'vehicle_make': 'Mercedes-Benz'}}},{'data': {'id': '78aa095a-acb5-4ffb-8552-a127cc512663', 'type': 'vehicle_model', 'attributes': {'name': 'AMG GLE63 S 4matic Plus', 'year': 2021, 'vehicle_make': 'Mercedes-Benz'}}}, {'data': {'id': 'fc877f7a-0fbf-4845-9d9f-f525c0ddb784', 'type': 'vehicle_model', 'attributes': {'name': 'CLA250 4matic', 'year': 2021, 'vehicle_make': 'Mercedes-Benz'}}},  {'data': {'id': 'c7780380-f172-4cfa-8925-373cc652b84e', 'type': 'vehicle_model', 'attributes': {'name': 'GLE350 4matic', 'year': 2021, 'vehicle_make': 'Mercedes-Benz'}}},  {'data': {'id': 'd83f91cb-c3f5-4be0-ab2b-17ff38d33fd2', 'type': 'vehicle_model', 'attributes': {'name': 'A220', 'year': 2021, 'vehicle_make': 'Mercedes-Benz'}}}, {'data': {'id': '2f4c456b-1db3-48f1-9230-17825d0a669b', 'type': 'vehicle_model', 'attributes': {'name': 'AMG GLA35 4matic', 'year': 2021, 'vehicle_make': 'Mercedes-Benz'}}},{'data': {'id': '636dd60c-f03c-4284-8799-3df641aea715', 'type': 'vehicle_model', 'attributes': {'name': 'AMG GLC63 4matic Plus Coupe', 'year': 2020, 'vehicle_make': 'Mercedes-Benz'}}}, {'data': {'id': 'd0f68424-38c7-497a-be91-a0497147c46a', 'type': 'vehicle_model', 'attributes': {'name': 'S60 AWD', 'year': 2020, 'vehicle_make': 'Volvo'}}},  {'data': {'id': 'b4671a22-0e29-4d3a-a28d-9a5064ff542c', 'type': 'vehicle_model', 'attributes': {'name': 'XC90 AWD', 'year': 2020, 'vehicle_make': 'Volvo'}}}, {'data': {'id': '3ad9144e-b543-41ce-bcab-253fdd3f08c1', 'type': 'vehicle_model', 'attributes': {'name': 'S60 AWD PHEV', 'year': 2020, 'vehicle_make': 'Volvo'}}}, {'data': {'id': '10986c16-775d-4c32-8027-0265ed4ce3d4', 'type': 'vehicle_model', 'attributes': {'name': 'V60 AWD PHEV', 'year': 2020, 'vehicle_make': 'Volvo'}}}, {'data': {'id': '0912e876-d070-4ee9-b216-8058c931722f', 'type': 'vehicle_model', 'attributes': {'name': 'XC60 AWD PHEV', 'year': 2020, 'vehicle_make': 'Volvo'}}},  {'data': {'id': 'c84e3874-469e-4e91-a0fe-ad6809b89f8d', 'type': 'vehicle_model', 'attributes': {'name': 'S60 FWD', 'year': 2021, 'vehicle_make': 'Volvo'}}}, {'data': {'id': 'f4f0cc1b-7c0e-4a5c-9f8c-653018a3d93a', 'type': 'vehicle_model', 'attributes': {'name': '428i Coupe', 'year': 2014, 'vehicle_make': 'BMW'}}},  {'data': {'id': '0d3acae2-34a4-402b-9463-80ab5183d02d', 'type': 'vehicle_model', 'attributes': {'name': 'M8 Competition Gran Coupe', 'year': 2021, 'vehicle_make': 'BMW'}}}, {'data': {'id': '7f03ce38-b06c-44b6-b4a9-1db57077f6a5', 'type': 'vehicle_model', 'attributes': {'name': 'Z4 M40i', 'year': 2020, 'vehicle_make': 'BMW'}}}, {'data': {'id': '365b3a0b-9a89-4208-81f2-5644ccad273f', 'type': 'vehicle_model', 'attributes': {'name': '230i Convertible', 'year': 2020, 'vehicle_make': 'BMW'}}}, {'data': {'id': 'cfc8c2f0-8974-4d1a-b718-ec7a9fbfae7c', 'type': 'vehicle_model', 'attributes': {'name': '530i xDrive', 'year': 2020, 'vehicle_make': 'BMW'}}},  {'data': {'id': 'a68ac6e4-2a59-4836-b6a2-819ab201e722', 'type': 'vehicle_model', 'attributes': {'name': 'M5', 'year': 2019, 'vehicle_make': 'BMW'}}}, {'data': {'id': 'bfc2abae-1908-4188-bd8d-d0e2a12a288d', 'type': 'vehicle_model', 'attributes': {'name': 'Sonata Hybrid', 'year': 2014, 'vehicle_make': 'Hyundai'}}},  {'data': {'id': 'fc123681-b144-414e-bb21-62f683a0d50a', 'type': 'vehicle_model', 'attributes': {'name': 'Veloster', 'year': 2019, 'vehicle_make': 'Hyundai'}}}, {'data': {'id': '78791984-0ea3-45ad-b8e4-0f1750bf0ca7', 'type': 'vehicle_model', 'attributes': {'name': 'Accent', 'year': 2016, 'vehicle_make': 'Hyundai'}}}, {'data': {'id': '3a44e877-df84-497e-8838-393b947c9010', 'type': 'vehicle_model', 'attributes': {'name': 'Highlander Hybrid AWD', 'year': 2018, 'vehicle_make': 'Toyota'}}},  {'data': {'id': '424ab8a6-0628-4a21-b3a2-c51a544e4119', 'type': 'vehicle_model', 'attributes': {'name': 'Camry Hybrid XLE/SE', 'year': 2018, 'vehicle_make': 'Toyota'}}}, {'data': {'id': '75f00824-3d85-42b9-8be0-30f479632bae', 'type': 'vehicle_model', 'attributes': {'name': 'Prius Prime', 'year': 2019, 'vehicle_make': 'Toyota'}}}, {'data': {'id': '6abcf192-ea59-42ca-917a-dae47edc035b', 'type': 'vehicle_model', 'attributes': {'name': 'Corolla Hatchback XSE', 'year': 2020, 'vehicle_make': 'Toyota'}}}, {'data': {'id': '84e3181e-8f6c-4e67-97a6-ba9553411180', 'type': 'vehicle_model', 'attributes': {'name': 'Tundra 2WD', 'year': 2019, 'vehicle_make': 'Toyota'}}},  {'data': {'id': '7bd3b1c7-f8a3-43de-ae7a-3b1ba948fe29', 'type': 'vehicle_model', 'attributes': {'name': 'Yaris', 'year': 2019, 'vehicle_make': 'Toyota'}}}]

store_vehicle_models_in_dynamodb(models_data)






