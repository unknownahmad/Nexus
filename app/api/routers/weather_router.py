from fastapi import APIRouter
import httpx

router = APIRouter()

@router.get("/check-weather")
async def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=41.3887&longitude=2.159&current_weather=true"
    
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(url)
        data = response.json()
        
    weather_code = data['current_weather']['weathercode']
    temperature = data['current_weather']['temperature'] # Extracting the temperature!
    
    if weather_code > 50:
        return {
            "safe": False, 
            "temperature": temperature,
            "message": f"It's {temperature}°C and raining! Outdoor gear booking is restricted."
        }
        
    return {
        "safe": True, 
        "temperature": temperature,
        "message": f"Weather is clear and {temperature}°C."
    }