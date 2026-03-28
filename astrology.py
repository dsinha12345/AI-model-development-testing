import swisseph as swe
from datetime import datetime
from geopy.geocoders import Nominatim

# Init
geolocator = Nominatim(user_agent="matrimony_app")

# 27 Nakshatras
NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira",
    "Ardra","Punarvasu","Pushya","Ashlesha","Magha",
    "Purva Phalguni","Uttara Phalguni","Hasta","Chitra",
    "Swati","Vishakha","Anuradha","Jyeshtha","Mula",
    "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta",
    "Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]

# Nadi groups
NADI = [0,1,2]*9

# Gana types
GANA = [
    "Deva","Manushya","Rakshasa","Manushya","Deva",
    "Manushya","Deva","Deva","Rakshasa","Rakshasa",
    "Manushya","Manushya","Deva","Rakshasa",
    "Deva","Rakshasa","Deva","Rakshasa","Rakshasa",
    "Manushya","Manushya","Deva","Rakshasa",
    "Rakshasa","Manushya","Manushya","Deva"
]

# Yoni types
YONI = [
    "Horse","Elephant","Sheep","Serpent","Dog",
    "Cat","Sheep","Ram","Cat","Rat",
    "Rat","Cow","Buffalo","Tiger",
    "Buffalo","Tiger","Deer","Deer","Dog",
    "Monkey","Monkey","Lion","Lion",
    "Horse","Cow","Elephant","Serpent"
]


def get_lat_lon(place):
    location = geolocator.geocode(place)
    return location.latitude, location.longitude


def get_kundli_features(dob, tob, lat, lon):
    dt = datetime.strptime(dob + " " + tob, "%d/%m/%Y %H:%M")

    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60)

    moon_long = swe.calc_ut(jd, swe.MOON)[0][0]

    rashi = int(moon_long / 30)
    nakshatra = int(moon_long / (360/27))

    return {
        "rashi": rashi,
        "nakshatra": nakshatra
    }


def is_manglik(dob, tob, lat, lon):
    dt = datetime.strptime(dob + " " + tob, "%d/%m/%Y %H:%M")

    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60)

    mars_long = swe.calc_ut(jd, swe.MARS)[0][0]

    houses, asc = swe.houses(jd, lat, lon)
    asc_deg = asc[0]

    house = int(((mars_long - asc_deg) % 360) / 30) + 1

    return house in [1, 2, 4, 7, 8, 12]


# -------- Koota Calculations -------- #

def varna_koota(r1, r2):
    return 1 if r1 <= r2 else 0


def vashya_koota(r1, r2):
    return 2 if r1 == r2 else 1


def tara_koota(n1, n2):
    diff = abs(n1 - n2)
    return 3 if diff % 9 in [0,1,2,4,6,8] else 0


def yoni_koota(n1, n2):
    return 4 if YONI[n1] == YONI[n2] else 2


def graha_maitri(r1, r2):
    return 5 if r1 == r2 else 3


def gana_koota(n1, n2):
    g1, g2 = GANA[n1], GANA[n2]
    if g1 == g2:
        return 6
    elif "Deva" in [g1, g2] and "Rakshasa" in [g1, g2]:
        return 1
    else:
        return 3


def bhakoot_koota(r1, r2):
    diff = abs(r1 - r2)
    if diff in [6, 8]:
        return 0
    return 7


def nadi_koota(n1, n2):
    return 0 if NADI[n1] == NADI[n2] else 8


# -------- MAIN GUN MILAN -------- #

def gun_milan(userA, userB):
    k1 = get_kundli_features(userA[2], userA[3], userA[5], userA[6])
    k2 = get_kundli_features(userB[2], userB[3], userB[5], userB[6])

    scores = {
        "varna": varna_koota(k1["rashi"], k2["rashi"]),
        "vashya": vashya_koota(k1["rashi"], k2["rashi"]),
        "tara": tara_koota(k1["nakshatra"], k2["nakshatra"]),
        "yoni": yoni_koota(k1["nakshatra"], k2["nakshatra"]),
        "graha_maitri": graha_maitri(k1["rashi"], k2["rashi"]),
        "gana": gana_koota(k1["nakshatra"], k2["nakshatra"]),
        "bhakoot": bhakoot_koota(k1["rashi"], k2["rashi"]),
        "nadi": nadi_koota(k1["nakshatra"], k2["nakshatra"])
    }

    total = sum(scores.values())

    # Dosha penalties
    if scores["nadi"] == 0:
        total -= 8

    if scores["bhakoot"] == 0:
        total -= 7

    mA = is_manglik(userA[2], userA[3], userA[5], userA[6])
    mB = is_manglik(userB[2], userB[3], userB[5], userB[6])

    if mA != mB:
        total -= 5

    scores["manglik_A"] = mA
    scores["manglik_B"] = mB
    scores["total"] = max(total, 0)

    return scores