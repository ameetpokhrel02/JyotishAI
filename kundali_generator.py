# kundali_generator.py - Real Vedic Kundali using PyEphem (Python 3.12 Compatible)
import ephem
from datetime import datetime
import math

# Rashi & Nakshatra
RASHI_NAMES = ["मेष", "वृष", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]
NAKSHATRA_NAMES = [
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा", "पुनर्वसु", "पुष्य", "आश्लेषा",
    "मघा", "पूर्वा फाल्गुनी", "उत्तरा फाल्गुनी", "हस्त", "चित्रा", "स्वाति", "विशाखा", "अनुराधा",
    "ज्येष्ठा", "मूल", "पूर्वाषाढा", "उत्तराषाढा", "श्रवण", "धनिष्ठा", "शतभिषा", "पूर्वभाद्रपदा",
    "उत्तरभाद्रपदा", "रेवती"
]

def deg_to_rashi(deg):
    deg = deg % 360
    rashi_idx = int(deg // 30)
    deg_in_rashi = deg % 30
    return RASHI_NAMES[rashi_idx], deg_in_rashi

def get_nakshatra(moon_deg):
    nak_deg = moon_deg % 360
    nak_idx = int(nak_deg / 13.3333)
    return NAKSHATRA_NAMES[nak_idx]

def generate_kundali(name, dob, tob, lat=27.7172, lon=85.3240):
    # Parse date/time
    year, month, day = map(int, dob.split('-'))
    hour, minute = map(int, tob.split(':'))
    
    # Create observer
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = datetime(year, month, day, hour, minute)
    
    # Calculate Sun
    sun = ephem.Sun(observer)
    sun_deg = sun.ra * 15  # RA to degrees
    sun_rashi, sun_deg = deg_to_rashi(sun_deg)
    
    # Calculate Moon
    moon = ephem.Moon(observer)
    moon_deg = moon.ra * 15
    moon_rashi, moon_deg = deg_to_rashi(moon_deg)
    moon_nakshatra = get_nakshatra(moon_deg)
    
    # Calculate Ascendant (Lagna) - Simplified
    # Real lagna needs sidereal time calculation
    sidereal_time = observer.sidereal_time()
    lagna_deg = (sidereal_time * 15) % 360
    lagna_rashi, lagna_deg = deg_to_rashi(lagna_deg)
    
    # Other planets (simplified)
    planets = {
        "सूर्य": {"rashi": sun_rashi, "degree": round(sun_deg, 2)},
        "चन्द्र": {"rashi": moon_rashi, "degree": round(moon_deg, 2), "nakshatra": moon_nakshatra},
        "लग्न": {"rashi": lagna_rashi, "degree": round(lagna_deg, 2)}
    }
    
    return {
        "name": name,
        "dob": dob,
        "tob": tob,
        "place": "Kathmandu",
        "lagna": planets["लग्न"],
        "planets": planets,
        "nakshatra": moon_nakshatra
    }

# Test
if __name__ == "__main__":
    k = generate_kundali("Amit Sharma", "1999-05-15", "14:30")
    print(f"नाम: {k['name']}")
    print(f"लग्न: {k['lagna']['rashi']} {k['lagna']['degree']:.2f}°")
    print(f"सूर्य: {k['planets']['सूर्य']['rashi']} {k['planets']['सूर्य']['degree']:.2f}°")
    print(f"चन्द्र: {k['planets']['चन्द्र']['rashi']} {k['planets']['चन्द्र']['degree']:.2f}° ({k['nakshatra']})")
