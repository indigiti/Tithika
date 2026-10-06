# Tithika Page Map

The executable source of truth is `config/routes.php`.

Current mapped logical pages: **292**.

## Product families

### 1. Panchang
Daily/monthly Panchang, regional Panjika/Panchang variants, ISKCON, solar/Panchang utilities, Chandrabalam, Tarabalam, Panchak, Bhadra, Ganda Moola, Nakshatra and Sankalpa.

### 2. Calendars
Hindu/Indian and regional yearly calendars plus major festival calendars such as Diwali, Durga Puja, Navratri, Onam, Chhath, Sankranti, Dashain and Tihar.

### 3. Muhurat
Choghadiya, Hora, Vivah, Griha Pravesh, vehicle/property purchase, Lagna, Gowri, Jain Pachchakkhan, Rahu Kala, auspicious Yoga, Panchaka Rahita, Abhijit, Do Ghati, Shubha Dates and Pancha Pakshi.

### 4. Vrat & Upavas
Ekadashi, Pradosh, Sankashti, Dwadashi, Purnima, Amavasya, Shivaratri, Skanda Sashti, Karthigai, Shraddha, Durgashtami, Kalashtami, Chaturmasa and special Vrat collections.

### 5. Festivals
Popular collections, lunar-month festival lists, Tamil/Malayalam/Sankranti collections, Gurus/Saints, Navdurga, Dashavatara, Puja Vidhi, deities and pilgrimage content.

### 6. Jyotish
Kundali, unified horoscope synthesis, evidence-backed interpretation, Dasha/transit timing timelines, personalized daily/weekly/monthly/yearly Rashifal, compatibility, Rashi, Birthstar, Lagna, Dosha, Shadbala, Ashtakavarga, Shodashavarga, Yogas, gemstone, Rudraksha, baby naming, Shani Sadesati, Pancha Pakshi, Shraddha Tithi and other calculator flows.

### 7. Planets & Astronomy
Positions, transit, combustion, retrograde, aspects, ecliptic events, Graha Yuddha, eclipses, seasons, equinoxes and solstices.

### 8. Devotion
Aarti, Chalisa, Stotram, Mantra, Namavali, Durga Saptashati, Ashtakam, Kavacham, Sundarkand, Hanuman Bahuk and Ramayana collections.

### 9. Gallery
Rangoli, greetings, Mehandi, festival/deity collections, Krishna art, Hindu symbols and paintings.

### 10. Learn
Tutorials, Panchang concepts, Choghadiya, Muhurat, Nakshatra, Rahu Kala, FAQ and contact/reference content.

## Rendering templates

| Template | Used for |
| --- | --- |
| `daily` | daily solar/Panchang views |
| `calendar` | month/year/date grids |
| `muhurat` | timing windows |
| `festival` | observance calendars |
| `calculator` | birth/input driven tools |
| `astronomy` | planetary event timelines |
| `devotion` | reading experiences |
| `gallery` | visual collections |
| `article` | explanatory references |
| `list` | searchable date/event lists |
| `collection` | category hubs |

## Route behavior

Family landing:
`/panchang/`

Detail page:
`/panchang/daily/`

All routes are resolved by the shared `page.php` renderer through Apache rewrite rules. This creates one maintainable page system while preserving distinct URLs for each utility.

## Implementation status convention

- **Live**: backed by a verified calculation/content engine.
- **Mapped**: production URL and UI shell exist; engine/content adapter still needs implementation.
- **Verified**: calculation rules have fixtures and cross-source tests.
- **Released**: engine + UI + SEO + mobile + accessibility audit passed.

The existing Choghadiya engine is preserved as the first live timing module.