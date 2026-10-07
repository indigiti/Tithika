# Tithika Page Map

The executable source of truth is `config/routes.php`.

Current mapped logical pages: **292**.

## Product families

### 1. Panchang
Daily/monthly Panchang, regional Panjika/Panchang variants, ISKCON and solar/Panchang utilities. Tarabalam, Chandrabalam, Panchak and Bhadra are engine-backed; Hindu Sunrise, Nakshatra, Ganda Moola, Abhijit Nakshatra, Vinchudo, Jwalamukhi Yoga, Sankalpa and Vedic Clock now reuse the verified Lahiri Panchang core. Hindi, Tamil, Telugu, Kannada, Malayalam, Gujarati, Marathi, Bengali, Odia, Assamese and ISKCON regional month views are backed by the shared regional calendar engine. Nepali Patro uses a dedicated offline Bikram Sambat adapter. Manvadi/Yugadi/Kalpadi are engine-backed; Kranti Samya remains quality-gated until its exact Mahapata interval formula is source-locked.

### 2. Calendars
Hindu/Indian and regional yearly calendars plus major festival calendars such as Diwali, Durga Puja, Navratri, Onam, Chhath, Sankranti, Dashain and Tihar. Tamil, Telugu, Kannada, Malayalam, Gujarati, Marathi, Bengali, Odia, Assamese and ISKCON regional calendar views now share the verified regional calendar engine; Nepali and Jain now use dedicated adapters: Bikram Sambat civil conversion for Nepali and Kartikadi Amanta Vikram/Veer Samvat for Jain.

### 3. Muhurat
Choghadiya, Hora, Vivah, Griha Pravesh, vehicle/property purchase, Lagna, Gowri, Jain Pachchakkhan, Rahu Kala, auspicious Yoga, Panchaka Rahita, Abhijit, Do Ghati, Shubha Dates and Pancha Pakshi. The shared substrate powers specialized Vivah/Griha/Property/Vehicle/Sanskar profiles. A second reuse engine now makes Shubha Hora, Panchaka Rahita, aggregate Auspicious Yogas, Sarvartha Siddhi, Amrit Siddhi, Guru/Ravi Pushya, Dwipushkar, Tripushkar and Ravi Yoga live with explicit rule tables. Gowri, Jain Pachchakkhan, corrected Do-Ghati and generic Shubha Dates are engine-backed. Pancha Pakshi remains quality-gated beyond its verified five-Yama solar framework.

### 4. Vrat & Upavas
Ekadashi, Pradosh, Sankashti, Dwadashi, Purnima, Amavasya, Shivaratri, Skanda Sashti, Karthigai, Shraddha, Durgashtami, Kalashtami, Chaturmasa and special Vrat collections. The verified recurrence layer now makes Satyanarayana/Purnima, Masik Durgashtami, Skanda Sashti, Karthigai, Rohini Vrat, Sawan Somwar and Mangala Gauri live. Shravana weekday observances expose separate Purnimanta/Amanta profiles. ISKCON Ekadashi uses the integrated Arunodaya/Vriddhi/Mahadwadashi/Hari-Vasara substrate; Kalashtami and solar-Nishita Masik Janmashtami are engine-backed. Chandra Darshan, Ishti/Anvadhan and Shraddha remain quality-gated.

### 5. Festivals
Popular collections, lunar-month festival lists, Tamil/Malayalam/Sankranti collections, Gurus/Saints, Navdurga, Dashavatara, Puja Vidhi, deities and pilgrimage content. The 13 verified major-festival calculations now run through one declarative festival rule registry with reusable local-time selectors.

### 6. Jyotish
Kundali, unified horoscope synthesis, evidence-backed interpretation, Dasha/transit timing timelines, personalized daily/weekly/monthly/yearly Rashifal, compatibility, Rashi, Birthstar, Lagna, Dosha, Shadbala, Ashtakavarga, Shodashavarga, Yogas, gemstone, Rudraksha, baby naming, Shani Sadesati, Pancha Pakshi, Shraddha Tithi and other calculator flows.

### 7. Planets & Astronomy
Positions, transit, combustion, retrograde, aspects, ecliptic events, Graha Yuddha, eclipses, seasons, equinoxes and solstices.

### 8. Devotion
Aarti, Chalisa, Stotram, Mantra, Namavali, Durga Saptashati, Ashtakam, Kavacham, Sundarkand, Hanuman Bahuk and Ramayana collections. Every mapped Devotion route now resolves through the structured editorial layer with practice context and related verified Tithika tools rather than a generic reading placeholder.

### 9. Gallery
Rangoli, greetings, Mehandi, festival/deity collections, Krishna art, Hindu symbols and paintings. Gallery routes now use lightweight original visual indexes, remain separate from calculation payloads and do not depend on third-party artwork.

### 10. Learn
Tutorials, Panchang concepts, Choghadiya, Muhurat, Nakshatra, Rahu Kala, FAQ and contact/reference content. These routes now contain structured original editorial guides with deep links into the verified calculation engines.

## Production certification

Current certified detail-route state:

- **218** verified/live calculation routes
- **62** structured editorial routes
- **1** canonical live redirect (`muhurat/choghadiya`)
- **281** production-quality/indexable detail routes
- **11** semantic quality-gated `noindex,follow` routes

The exact contract and promotion queue are documented in `docs/RELEASE_CERTIFICATION.md` and enforced by CI.

## SEO and release state

The 292-route map is intentionally larger than the set exposed to search engines. A centralized live-route registry plus structured editorial coverage determines which detail pages receive `index,follow`; unfinished mapped shells receive `noindex,follow`. The XML sitemap contains only production-quality routes plus family landing pages.

The shared shell now emits canonical/OpenGraph/Twitter metadata, JSON-LD and breadcrumbs; related links are topic-aware across families. The human site map labels routes as Live, Editorial or Mapped.

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