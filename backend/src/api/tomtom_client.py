import logging
import requests
from src.api.settings import settings

logger = logging.getLogger(__name__)

# URL base para Traffic Flow Segment (Flow Services)
# Retorna velocidad actual, velocidad libre, y tiempo de viaje para una coordenada.
TOMTOM_FLOW_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"

def get_flow_segment_data(lat: float, lon: float) -> dict:
    """
    Consulta la API de TomTom para obtener los datos de flujo de trafico en una coordenada especifica.
    """
    if not settings.tomtom_api_key or settings.tomtom_api_key == "your_tomtom_api_key_here":
        logger.warning("TomTom API Key no configurada. Retornando datos mock de sandbox.")
        return get_mock_tomtom_response()

    params = {
        "key": settings.tomtom_api_key,
        "point": f"{lat},{lon}"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        logger.info(f"Consultando TomTom API para {lat}, {lon}...")
        # Aumentamos timeout a 10s. verify=False previene bloqueos por firewalls corporativos que interceptan SSL.
        response = requests.get(TOMTOM_FLOW_URL, params=params, headers=headers, timeout=10.0, verify=False)
        
        # Si hay un error, intentamos parsear el mensaje de TomTom
        if not response.ok:
            try:
                error_data = response.json()
                return {"error": error_data.get("error", "API Error"), "message": error_data.get("detailedError", {}).get("message", "Error de TomTom")}
            except Exception:
                pass
                
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error consultando TomTom API: {e}")
        # En caso de error (ej. cuota excedida), retornar un error manejable
        return {"error": str(e), "message": "No se pudo obtener el trafico de TomTom."}


def get_mock_tomtom_response() -> dict:
    """
    Retorna un JSON simulando la respuesta de TomTom cuando no hay API Key, 
    para poder desarrollar y probar la UI del Sandbox.
    """
    return {
        "flowSegmentData": {
            "frc": "FRC3",
            "currentSpeed": 42,
            "freeFlowSpeed": 60,
            "currentTravelTime": 120,
            "freeFlowTravelTime": 84,
            "confidence": 1.0,
            "coordinates": {
                "coordinate": [
                    {"latitude": 14.62, "longitude": -90.53},
                    {"latitude": 14.63, "longitude": -90.54}
                ]
            }
        }
    }
