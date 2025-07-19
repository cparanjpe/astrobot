import swisseph as swe
from datetime import datetime

# ==== CONFIGURATION ====
swe.set_ephe_path('./ephe')
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ===== INPUTS =====
birth_utc = datetime(2003, 9, 19, 22, 7)  # UTC time
latitude = 19.3919
longitude = 72.8397
location_name = "Vasai"

planet_list = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': swe.MEAN_NODE  # Ketu opposite Rahu
}

zodiac_signs = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

nakshatras = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

# ===== Julian Day ====
jd = swe.julday(birth_utc.year, birth_utc.month, birth_utc.day,
                birth_utc.hour + birth_utc.minute / 60 + birth_utc.second / 3600)

# ===== Set location for house calculations ====
swe.set_topo(longitude, latitude, 0)

# ===== Calculate Ascendant and Houses (tropical!) =====
cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'W')  # 'W' = Whole sign houses
tropical_lagna_deg = ascmc[0]

# ===== Calculate Lahiri ayanamsa and sidereal Lagna =====
ayanamsa = swe.get_ayanamsa(jd)
sidereal_lagna_deg = (tropical_lagna_deg - ayanamsa) % 360
lagna_sign = int(sidereal_lagna_deg // 30)

# ===== Assign signs to houses starting from Lagna =====
house_signs = [(lagna_sign + i) % 12 for i in range(12)]

# ===== Calculate planetary positions (sidereal) =====
planet_positions = {}
for name, code in planet_list.items():
    pos, _ = swe.calc_ut(jd, code, swe.FLG_SIDEREAL)
    lon = pos[0]
    if name == 'Ketu':
        lon = (lon + 180) % 360  # Ketu opposite Rahu
    planet_positions[name] = lon

# ===== Assign planets to houses =====
house_chart = {i + 1: [] for i in range(12)}
for planet, lon in planet_positions.items():
    sign = int(lon // 30)
    house = ((sign - lagna_sign) % 12) + 1
    house_chart[house].append(planet)

# ===== Helper to calculate Nakshatra =====
def get_nakshatra(longitude):
    nak_len = 360 / 27
    index = int(longitude // nak_len)
    nak_name = nakshatras[index]
    deg_in_nak = longitude % nak_len
    return nak_name, deg_in_nak

# ===== OUTPUT =====
print(f"\n🪐 D-1 Rāśi Chart for {birth_utc.strftime('%Y-%m-%d %H:%M UTC')} in {location_name}\n")
print(f"Ascendant (Lagna): {zodiac_signs[lagna_sign]} ({sidereal_lagna_deg:.2f}°)")
nak, deg_in = get_nakshatra(sidereal_lagna_deg)
print(f"  Nakshatra: {nak} ({deg_in:.2f}°)\n")

print("== D-1 Chart (Rāśi Chart) ==")
for house in range(1, 13):
    sign = zodiac_signs[house_signs[house - 1]]
    planets = ', '.join(house_chart[house]) or '—'
    print(f"House {house:2} ({sign}): {planets}")

print("\nPlanet Positions with Nakshatras:")
for planet, lon in planet_positions.items():
    nak, deg_in = get_nakshatra(lon)
    sign = zodiac_signs[int(lon // 30)]
    print(f" {planet:7}: {lon:.2f}° {sign} | Nakshatra: {nak} ({deg_in:.2f}°)")
