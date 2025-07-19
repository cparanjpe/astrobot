import swisseph as swe

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

HOUSE_LORDS = {
    0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon',
    4: 'Sun', 5: 'Mercury', 6: 'Venus', 7: 'Mars',
    8: 'Jupiter', 9: 'Saturn', 10: 'Saturn', 11: 'Jupiter'
}

# ===== FUNCTIONS =====
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
    pada = int(deg_in_nak // (nak_len / 4)) + 1
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

def build_house_signs(lagna_sign):
    return [(lagna_sign + i) % 12 for i in range(12)]

def build_chart(lagna_sign, planet_positions, division_func=None):
    chart = {i + 1: [] for i in range(12)}
    chart[1].append('Ascendant')

    for planet, lon in planet_positions.items():
        sign = division_func(lon) if division_func else int(lon // 30)
        relative_house = ((sign - lagna_sign) % 12) + 1
        chart[relative_house].append(planet)

    return chart

def get_house_lords(house_signs, chart):
    lords = {}
    for i, sign_num in enumerate(house_signs):
        house_num = i + 1
        lord = HOUSE_LORDS[sign_num]
        # Find house where this lord is placed
        placed_in_house = next((h for h, plist in chart.items() if lord in plist), "Not Found")
        lords[house_num] = {"sign": ZODIAC_SIGNS[sign_num], "lord": lord, "placed_in": placed_in_house}
    return lords
