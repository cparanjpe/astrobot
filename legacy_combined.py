import swisseph as swe
from datetime import datetime

# ===== CONFIGURATION =====
swe.set_ephe_path('./ephe')
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ===== CONSTANTS =====
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
    'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE
}

# ===== INPUTS =====
birth_utc = datetime(2003, 9, 19, 22, 7)  # UTC time
latitude = 19.3919
longitude = 72.8397
location_name = "Vasai"

# ===== JULIAN DAY and LOCATION =====
jd = swe.julday(birth_utc.year, birth_utc.month, birth_utc.day,
                birth_utc.hour + birth_utc.minute / 60)
swe.set_topo(longitude, latitude, 0)

# ===== COMMON FUNCTIONS =====
def get_sidereal_lagna(jd, lat, lon):
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W')
    tropical_lagna_deg = ascmc[0] % 360
    ayanamsha = swe.get_ayanamsa(jd)
    sidereal_lagna_deg = (tropical_lagna_deg - ayanamsha) % 360
    lagna_sign_num = int(sidereal_lagna_deg // 30)
    return sidereal_lagna_deg, lagna_sign_num

def get_planet_positions(jd):
    positions = {}
    for name, code in PLANETS.items():
        pos, _ = swe.calc_ut(jd, code, swe.FLG_SIDEREAL)
        lon = pos[0] % 360
        if name == 'Ketu':
            lon = (lon + 180) % 360
        positions[name] = lon
    return positions

def get_nakshatra(lon):
    nak_len = 360 / 27
    index = int(lon // nak_len)
    deg_in_nak = lon % nak_len
    pada = int(deg_in_nak // (nak_len / 4)) + 1  # Padas 1 to 4
    return NAKSHATRAS[index], deg_in_nak, pada

def get_navamsa_sign(lon):
    sign = int(lon // 30)
    deg_in_sign = lon % 30
    nav_div = int(deg_in_sign // (30 / 9))
    nav_sign = (sign * 9 + nav_div) % 12
    return nav_sign

def get_vimsamsa_sign(lon):
    sign = int(lon // 30)
    deg_in_sign = lon % 30
    vimsamsa_div = int(deg_in_sign // (30 / 20))
    vimsamsa_sign = (sign * 20 + vimsamsa_div) % 12
    return vimsamsa_sign


def build_house_chart(lagna_sign, planet_positions, is_navamsa=False):
    house_chart = {i + 1: [] for i in range(12)}
    house_chart[1].append('Ascendant')

    for planet, lon in planet_positions.items():
        sign = get_navamsa_sign(lon) if is_navamsa else int(lon // 30)
        relative_house = ((sign - lagna_sign) % 12) + 1
        house_chart[relative_house].append(planet)

    return house_chart

# ===== D-1 CHART =====
d1_lagna_deg, d1_lagna_sign = get_sidereal_lagna(jd, latitude, longitude)
planet_positions = get_planet_positions(jd)
house_signs_d1 = [(d1_lagna_sign + i) % 12 for i in range(12)]
house_chart_d1 = build_house_chart(d1_lagna_sign, planet_positions, is_navamsa=False)

print(f"\n🪐 D-1 Rāśi Chart for {birth_utc.strftime('%Y-%m-%d %H:%M UTC')} in {location_name}")
print(f"Ascendant: {ZODIAC_SIGNS[d1_lagna_sign]} ({d1_lagna_deg:.2f}°) | Nakshatra: {get_nakshatra(d1_lagna_deg)[0]}")
print("== D-1 Houses ==")
for i in range(12):
    sign = ZODIAC_SIGNS[house_signs_d1[i]]
    planets = ', '.join(house_chart_d1[i + 1]) or '—'
    print(f"House {i+1:2} ({sign}): {planets}")

# ===== D-9 CHART =====
d9_lagna_sign = get_navamsa_sign(d1_lagna_deg)
house_signs_d9 = [(d9_lagna_sign + i) % 12 for i in range(12)]
house_chart_d9 = build_house_chart(d9_lagna_sign, planet_positions, is_navamsa=True)

print(f"\n🕉️ D-9 Navamsa Chart (Derived from same birth details)")
print(f"Ascendant: {ZODIAC_SIGNS[d9_lagna_sign]} Navamsa")
print("== D-9 Houses ==")
for i in range(12):
    sign = ZODIAC_SIGNS[house_signs_d9[i]]
    planets = ', '.join(house_chart_d9[i + 1]) or '—'
    print(f"House {i+1:2} ({sign} Navamsa): {planets}")

# ===== D-20 CHART =====
d20_lagna_sign = get_vimsamsa_sign(d1_lagna_deg)
house_signs_d20 = [(d20_lagna_sign + i) % 12 for i in range(12)]
house_chart_d20 = {i + 1: [] for i in range(12)}
house_chart_d20[1].append('Ascendant')

# Place planets in D20
for planet, lon in planet_positions.items():
    vimsamsa_sign = get_vimsamsa_sign(lon)
    relative_house = ((vimsamsa_sign - d20_lagna_sign) % 12) + 1
    house_chart_d20[relative_house].append(planet)

print(f"\n🕉️ D-20 Vimsamsa Chart (Derived from same birth details)")
print(f"Ascendant: {ZODIAC_SIGNS[d20_lagna_sign]} Vimsamsa")
print("== D-20 Houses ==")
for i in range(12):
    sign = ZODIAC_SIGNS[house_signs_d20[i]]
    planets = ', '.join(house_chart_d20[i + 1]) or '—'
    print(f"House {i+1:2} ({sign} Vimsamsa): {planets}")


    

# ===== Planet Details =====
print("\nPlanet Positions with Nakshatras and Padas:")
for planet, lon in planet_positions.items():
    nak, deg_in, pada = get_nakshatra(lon)
    sign = ZODIAC_SIGNS[int(lon // 30)]
    print(f"{planet:7}: {lon:.2f}° {sign} | Nakshatra: {nak} ({deg_in:.2f}°) | Pada: {pada}")



# ===== HOUSE LORDS TABLE =====
house_lords = {
    0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon',
    4: 'Sun', 5: 'Mercury', 6: 'Venus', 7: 'Mars',
    8: 'Jupiter', 9: 'Saturn', 10: 'Saturn', 11: 'Jupiter'
}

# ===== FUNCTION TO PRINT HOUSE LORDS =====
def print_house_lords(chart_name, house_signs, house_chart):
    print(f"\n== 🏠 {chart_name} House Lords and Their Positions ==")
    for i in range(12):
        house_num = i + 1
        sign_num = house_signs[i]
        sign_name = ZODIAC_SIGNS[sign_num]
        lord = house_lords[sign_num]

        # Find where lord planet sits
        lord_house = next((h for h, plist in house_chart.items() if lord in plist), "Not Found")

        print(f"House {house_num} ({sign_name}) → Lord: {lord} → Sits in House: {lord_house}")

# ===== CALL FOR D1 =====
print_house_lords("D-1 Rāśi Chart", house_signs_d1, house_chart_d1)

# ===== CALL FOR D9 =====
print_house_lords("D-9 Navamsa Chart", house_signs_d9, house_chart_d9)

# ===== CALL FOR D20 House Lords =====
print_house_lords("D-20 Vimsamsa Chart", house_signs_d20, house_chart_d20)
