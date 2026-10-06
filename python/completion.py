#!/usr/bin/env python3
"""Tithika completion engine for the six remaining rule families.

The engine deliberately composes Tithika's existing Lahiri Panchang, festival,
Vrat, regional-calendar and planetary substrates.  Every mode exposes its rule
profile in the JSON response so UI and regression fixtures can audit selection.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import festival_rules
import lagna
import lunar_occurrences
import mahadwadashi
import panchang
import planetary
import regional_calendar
import sankranti
import vrat_rules

ENGINE_VERSION = "1.0.0"

MODE_TITLES = {
    "manvadi": "Manvadi Tithi",
    "yugadi-tithi": "Yugadi Tithi",
    "kalpadi": "Kalpadi Tithi",
    "kranti-samya": "Kranti Samya / Mahapata",
    "gowri": "Gowri Panchangam",
    "jain-pachchakkhan": "Jain Pachchakkhan",
    "pancha-pakshi": "Pancha Pakshi",
    "do-ghati": "Do Ghati Muhurat",
    "shubha-dates": "Shubha Dates",
    "iskcon-ekadashi": "ISKCON Ekadashi",
    "kalashtami": "Kalashtami",
    "chandra-darshan": "Chandra Darshan",
    "masik-janmashtami": "Masik Janmashtami",
    "ishti-anvadhan": "Ishti & Anvadhan",
    "shraddha": "Shraddha Dates",
    "purushottam-maas": "Purushottam Maas",
    "chaturmasa": "Chaturmasa",
    "festival-hindu": "Hindu Festival Calendar",
    "festival-tamil": "Tamil Festival Calendar",
    "festival-malayalam": "Malayalam Festival Calendar",
    "festival-month": "Lunar Month Festival Calendar",
    "festival-yearly": "Festival Yearly Calendar",
    "prashna-kundali": "Prashna Kundali",
    "gemstone": "Gemstone Calculator",
    "rudraksha": "Rudraksha Calculator",
    "baby-name": "Baby Name / Initials",
    "name-initials": "Name Initials",
    "rashi-by-name": "Rashi by Name",
    "sahasra-chandrodaya": "1000 Chandrodaya",
    "shraddha-tithi": "Shraddha Tithi",
    "planet-parallel": "Planetary Parallels",
    "ecliptic-crossings": "Ecliptic Crossings",
    "indian-seasons": "Indian Seasons",
}

MANVADI_RULES = [
    ("Brahma Savarni Manvadi", "Magha", 6),
    ("Savarni Manvadi", "Phalguna", 14),
    ("Swayambhuva Manvadi", "Chaitra", 2),
    ("Swarochisha Manvadi", "Chaitra", 14),
    ("Vaivaswata Manvadi", "Jyeshtha", 14),
    ("Raivata Manvadi", "Ashadha", 9),
    ("Chakshusha Manvadi", "Ashadha", 14),
    ("Indra Savarni Manvadi", "Bhadrapada", 22),
    ("Daiva Savarni Manvadi", "Bhadrapada", 29),
    ("Rudra Savarni Manvadi", "Bhadrapada", 2),
    ("Daksha Savarni Manvadi", "Ashwina", 8),
    ("Tamasa Manvadi", "Kartika", 11),
    ("Uttama Manvadi", "Kartika", 14),
    ("Dharma Savarni Manvadi", "Pausha", 10),
]
YUGADI_RULES = [
    ("Dwapara Yuga Diwas", "Phalguna", 29),
    ("Treta Yuga Diwas", "Vaishakha", 2),
    ("Kali Yuga Diwas", "Ashwina", 27),
    ("Satya Yuga Diwas", "Kartika", 8),
]
KALPADI_RULES = [
    ("Varaha Kalpadi", "Magha", 12),
    ("Brahma Kalpadi", "Chaitra", 17),
    ("Kurma Kalpadi First", "Chaitra", 0),
    ("Kurma Kalpadi Second", "Chaitra", 4),
    ("Parthiva Kalpadi", "Vaishakha", 2),
    ("Savitri Kalpadi", "Kartika", 6),
    ("Pralaya Kalpadi", "Margashirsha", 8),
]

GOWRI_DAY = {
    6:["Uthi","Amirdha","Rogam","Laabam","Dhanam","Sugam","Soram","Visham"],
    0:["Amirdha","Visham","Rogam","Laabam","Dhanam","Sugam","Soram","Uthi"],
    1:["Rogam","Laabam","Dhanam","Sugam","Soram","Uthi","Visham","Amirdha"],
    2:["Laabam","Dhanam","Sugam","Soram","Visham","Uthi","Amirdha","Rogam"],
    3:["Dhanam","Sugam","Soram","Uthi","Amirdha","Visham","Rogam","Laabam"],
    4:["Sugam","Soram","Uthi","Visham","Amirdha","Rogam","Laabam","Dhanam"],
    5:["Soram","Uthi","Visham","Amirdha","Rogam","Laabam","Dhanam","Sugam"],
}
GOWRI_NIGHT = {
    6:["Dhanam","Sugam","Soram","Visham","Uthi","Amirdha","Rogam","Laabam"],
    0:["Sugam","Soram","Uthi","Amirdha","Visham","Rogam","Laabam","Dhanam"],
    1:["Soram","Uthi","Visham","Amirdha","Rogam","Laabam","Dhanam","Sugam"],
    2:["Uthi","Amirdha","Rogam","Laabam","Dhanam","Sugam","Soram","Visham"],
    3:["Amirdha","Visham","Rogam","Laabam","Dhanam","Sugam","Soram","Uthi"],
    4:["Rogam","Laabam","Dhanam","Sugam","Soram","Uthi","Visham","Amirdha"],
    5:["Laabam","Dhanam","Sugam","Soram","Uthi","Visham","Amirdha","Rogam"],
}
GOWRI_GOOD = {"Amirdha","Dhanam","Uthi","Laabam","Sugam"}

DO_GHATI_NAMES = [
    ("Rudra",False),("Uraga",False),("Mitra",True),("Pitara",False),("Vasu",True),
    ("Ambu",True),("Vishwedeva",True),("Vidhi",True),("Brahma",True),("Indra",True),
    ("Indragni",False),("Daitya",False),("Varuna",True),("Aryama",True),("Bhaga",False),
    ("Ishwara",False),("Ajaikapada",False),("Ahirbudhnya",True),("Pusha",True),("Ashwini",True),
    ("Yama",False),("Agni",False),("Brahma",True),("Chandra",True),("Aditi",True),
    ("Brihaspati",True),("Vishnu",True),("Surya",True),("Tvashta",True),("Samirana",True),
]

BIRDS = ["Vulture","Owl","Crow","Cock","Peacock"]
BRIGHT_BIRD = {
    **{n:"Vulture" for n in panchang.NAKSHATRA_NAMES[0:5]},
    **{n:"Owl" for n in panchang.NAKSHATRA_NAMES[5:11]},
    **{n:"Crow" for n in panchang.NAKSHATRA_NAMES[11:16]},
    **{n:"Cock" for n in panchang.NAKSHATRA_NAMES[16:22]},
    **{n:"Peacock" for n in panchang.NAKSHATRA_NAMES[22:27]},
}
DARK_SWAP = {"Vulture":"Peacock","Owl":"Cock","Crow":"Crow","Cock":"Owl","Peacock":"Vulture"}
ACTIVITIES = ["Ruling","Eating","Walking","Sleeping","Dying"]
ACTIVITY_SCORE = {"Ruling":1.0,"Eating":0.8,"Walking":0.6,"Sleeping":0.4,"Dying":0.2}
# Published mirror-table day groups.  The base row is rotated per bird.
BRIGHT_GROUPS = {
    "A":["Eating","Walking","Ruling","Sleeping","Dying"],
    "B":["Ruling","Sleeping","Dying","Eating","Walking"],
    "C":["Sleeping","Dying","Eating","Walking","Ruling"],
    "D":["Walking","Ruling","Sleeping","Dying","Eating"],
}
DARK_GROUPS = {
    "A":["Walking","Ruling","Eating","Dying","Sleeping"],
    "B":["Eating","Dying","Sleeping","Ruling","Walking"],
    "C":["Ruling","Eating","Walking","Sleeping","Dying"],
    "D":["Sleeping","Walking","Dying","Eating","Ruling"],
    "E":["Dying","Sleeping","Ruling","Walking","Eating"],
}

NAME_SYLLABLES = {
    "Ashwini":["Chu","Che","Cho","La"],"Bharani":["Li","Lu","Le","Lo"],
    "Krittika":["A","I","U","E"],"Rohini":["O","Va","Vi","Vu"],
    "Mrigashira":["Ve","Vo","Ka","Ki"],"Ardra":["Ku","Gha","Na","Cha"],
    "Punarvasu":["Ke","Ko","Ha","Hi"],"Pushya":["Hu","He","Ho","Da"],
    "Ashlesha":["Di","Du","De","Do"],"Magha":["Ma","Mi","Mu","Me"],
    "Purva Phalguni":["Mo","Ta","Ti","Tu"],"Uttara Phalguni":["Te","To","Pa","Pi"],
    "Hasta":["Pu","Sha","Na","Tha"],"Chitra":["Pe","Po","Ra","Ri"],
    "Swati":["Ru","Re","Ro","Ta"],"Vishakha":["Ti","Tu","Te","To"],
    "Anuradha":["Na","Ni","Nu","Ne"],"Jyeshtha":["No","Ya","Yi","Yu"],
    "Mula":["Ye","Yo","Bha","Bhi"],"Purva Ashadha":["Bhu","Dha","Pha","Dha"],
    "Uttara Ashadha":["Bhe","Bho","Ja","Ji"],"Shravana":["Ju","Je","Jo","Khi"],
    "Dhanishta":["Ga","Gi","Gu","Ge"],"Shatabhisha":["Go","Sa","Si","Su"],
    "Purva Bhadrapada":["Se","So","Da","Di"],"Uttara Bhadrapada":["Du","Tha","Jha","Na"],
    "Revati":["De","Do","Cha","Chi"],
}
RASHI_INITIALS = {
    "Mesha":["A","L","E"],"Vrishabha":["B","V","U"],"Mithuna":["K","Chh","Gh"],
    "Karka":["D","H"],"Simha":["M","T"],"Kanya":["P","Th","N"],
    "Tula":["R","T"],"Vrishchika":["N","Y"],"Dhanu":["Bh","Dh","Ph"],
    "Makara":["Kh","J"],"Kumbha":["G","S","Sh"],"Meena":["D","Ch"