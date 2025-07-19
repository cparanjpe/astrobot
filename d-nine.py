import swisseph as swe

# --------------------------
# Birth Details (Change Here)
# --------------------------
year, month, day = 2003, 9, 20
hour, minute = 3, 37
latitude = 19.3910      # Vasai
longitude = 72.8258
timezone = 5.5          # IST

# --------------------------
# Julian Day (Universal Time)
# --------------------------
ut_hour = hour + minute / 60 - timezone
jd = swe.julday(year, month, day, ut_hour)

# Lahiri Ayanamsha globally
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Zodiac signs
zodiac_signs = {
    0: "Aries", 1: "Taurus", 2: "Gemini", 3: "Cancer",
    4: "Leo", 5: "Virgo", 6: "Libra", 7: "Scorpio",
    8: "Sagittarius", 9: "Capricorn", 10: "Aquarius", 11: "Pisces"
}

# --------------------------
# Navamsa calculation function
# --------------------------
def get_navamsa_sign_num(lon):
    sign_num = int(lon // 30)
    deg_in_sign = lon % 30
    nav_div = int(deg_in_sign // (30 / 9))
    nav_sign = (sign_num * 9 + nav_div) % 12
    return nav_sign

# --------------------------
# Ascendant Calculation (your format)
# --------------------------
cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'W')  # 'W' for whole sign
tropical_lagna_deg = ascmc[0] % 360
ayanamsa = swe.get_ayanamsa(jd)
sidereal_lagna_deg = (tropical_lagna_deg - ayanamsa) % 360
lagna_sign_num = int(sidereal_lagna_deg // 30)
lagna_navamsa_sign = get_navamsa_sign_num(sidereal_lagna_deg)

# --------------------------
# Planets Sidereal Positions
# --------------------------
planets = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
    'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE
}

planet_positions = {}
for pname, pid in planets.items():
    pos,_ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
    lon = pos[0]
    lon = lon % 360
    if pname == 'Ketu':
        lon = (lon + 180) % 360
    planet_positions[pname] = lon

# --------------------------
# Place Planets in D9 Houses (your D1 style)
# --------------------------
house_chart = {i: [] for i in range(1, 13)}
house_chart[1].append('Ascendant')

for pname, plon in planet_positions.items():
    nav_sign = get_navamsa_sign_num(plon)
    relative_house = ((nav_sign - lagna_navamsa_sign) + 12) % 12 + 1
    house_chart[relative_house].append(pname)

# --------------------------
# Print Chart (with house numbers and signs)
# --------------------------
print("== 🕉️ D-9 Navamsa Chart (Same Format as D1) ==")
for hnum in range(1, 13):
    sign_num = (lagna_navamsa_sign + hnum - 1) % 12
    sign_name = zodiac_signs[sign_num]
    occupants = ", ".join(house_chart[hnum]) if house_chart[hnum] else "—"
    print(f"House {hnum} ({sign_name} Navamsa): {occupants}")
