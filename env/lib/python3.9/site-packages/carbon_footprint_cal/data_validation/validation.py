import logging
from decimal import Decimal, InvalidOperation
from .utils import get_supported_countries

logger = logging.getLogger(__name__)

class Validation:
    def validate_electricity_params(self, location, value, unit):
        """Validates electricity parameters."""
        logger.info(f"Validating electricity: location={location}, value={value}, unit={unit}")

        # Validate location: Ensure it's a valid country code
        supported_countries = get_supported_countries() # Get the supported countries from the utility function.
        if location not in supported_countries:
            logger.error(f"Validation failed: Location '{location}' is not supported.")
            raise ValueError(f"Location '{location}' is not supported.")

        #validating electricity value entered by user
        try:
            value = Decimal(str(value).strip())  # Convert to Decimal and remove whitespace
            if value <= 0:
                logger.error("Validation failed: Electricity value must be positive.") 
                raise ValueError("Electricity value must be a positive number.")
        except (ValueError, InvalidOperation):
            logger.error("Validation failed: Electricity value must be a valid number.")
            raise ValueError("Electricity value must be a valid number.")

        if unit.lower() not in ["kwh", "mwh"]: #validating electricity unit
            logger.error("Validation failed: Invalid electricity unit.")
            raise ValueError("Invalid electricity unit. Must be 'kwh' or 'mwh'.")

        logger.info("Electricity validation successful.")
        return True

    
    def validate_flight_params(self, passengers, legs):
        """Validates flight parameters."""
        logger.info(f"Validating flight: passengers={passengers}, legs={legs}")

        if not isinstance(passengers, int) or passengers <= 0: #validating number of passengers
            logger.error("Validation failed: Number of passengers must be a positive integer.")
            raise ValueError("Number of passengers must be a positive integer.")

        #validating whether departure and destination airports are provided
        if not isinstance(legs, list) or not all(isinstance(leg, dict) for leg in legs):
            logger.error("Validation failed: Legs must be a list of dictionaries.")
            raise ValueError("Legs must be a list of dictionaries.")

        for leg in legs:
            if "departure_airport" not in leg or "destination_airport" not in leg:
                logger.error("Validation failed: Each leg must have 'departure_airport' and 'destination_airport'.")
                raise ValueError("Each leg must have 'departure_airport' and 'destination_airport'.")

        logger.info("Flight validation successful.")
        return True
    
    
    def validate_shipping_params(self, weight_value, weight_unit, distance_value, distance_unit, transport_method):
        """Validates shipping parameters."""
        try:
            weight_value = Decimal(str(weight_value).strip()) # Convert weight value to decimal and remove whitespace.
            distance_value = Decimal(str(distance_value).strip()) # Convert distance value to decimal and remove whitespace.

            if weight_value <= 0: #validating weight of shipment
                raise ValueError("Weight value must be a positive number.")

            if weight_unit not in ["g", "lb", "kg", "mt"]: #validating the unit of weight
                raise ValueError("Invalid weight unit. Must be 'g', 'lb', 'kg', or 'mt'.")

            if distance_value <= 0: #validating the distance covered by the shipment
                raise ValueError("Distance value must be a positive number.")

            if distance_unit not in ["mi", "km"]: #validating the distance unit
                raise ValueError("Invalid distance unit. Must be 'mi' or 'km'.")

            if transport_method.lower() not in ["ship", "train", "truck", "plane"]: #validating the transport method
                raise ValueError("Invalid transport method.")

            logger.info(f"Shipping validation successful: weight_value={weight_value}, weight_unit={weight_unit}, distance_value={distance_value}, distance_unit={distance_unit}, transport_method={transport_method}")
            return True

        except (ValueError, InvalidOperation) as e:
            logger.error(f"Validation failed: {e}")
            raise ValueError(f"Validation failed: {e}")