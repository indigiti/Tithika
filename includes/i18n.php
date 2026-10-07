<?php
declare(strict_types=1);

const TITHIKA_SUPPORTED_LOCALES = ['en','hi'];

function tithika_locale(): string {
    static $locale = null;
    if ($locale !== null) return $locale;
    $requested = strtolower(trim((string)($_GET['lang'] ?? '')));
    $cookie = strtolower(trim((string)($_COOKIE['tithika_lang'] ?? '')));
    $candidate = in_array($requested, TITHIKA_SUPPORTED_LOCALES, true) ? $requested : $cookie;
    $locale = in_array($candidate, TITHIKA_SUPPORTED_LOCALES, true) ? $candidate : 'en';
    if ($requested !== '' && in_array($requested, TITHIKA_SUPPORTED_LOCALES, true) && !headers_sent()) {
        setcookie('tithika_lang', $requested, [
            'expires'=>time()+31536000,
            'path'=>'/',
            'secure'=>(!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off'),
            'httponly'=>false,
            'samesite'=>'Lax',
        ]);
    }
    return $locale;
}

function tithika_dictionary(): array {
    static $dict = null;
    if ($dict !== null) return $dict;
    $dict = [
      'en'=>[
        'brand.tagline'=>'Vedic time, reimagined',
        'nav.all_tools'=>'All tools','nav.settings'=>'Settings','nav.primary'=>'Primary',
        'nav.panchang'=>'Panchang','nav.calendars'=>'Calendars','nav.muhurat'=>'Muhurat',
        'nav.vrat'=>'Vrat & Upavas','nav.festivals'=>'Festivals','nav.jyotish'=>'Jyotish',
        'skip.content'=>'Skip to content','location.label'=>'Location',
        'location.chooser'=>'Location chooser','location.search'=>'Search city or place',
        'location.use_current'=>'Use current location','location.privacy'=>'Your location is used only to calculate local solar timings.',
        'footer.tagline'=>'Traditional calendar conventions in a modern, evidence-first utility experience.',
        'footer.home'=>'Home','footer.sitemap'=>'Site map','footer.xml'=>'XML sitemap','footer.faq'=>'FAQ',
        'home.kicker'=>'Your daily Vedic dashboard','home.title'=>'Today, clearly.',
        'home.loading'=>'Loading verified Panchang, Muhurat and upcoming observances for your selected location…',
        'home.ask'=>'Ask Tithika Intelligence →','home.full_panchang'=>'Full Panchang','home.personalize'=>'Personalize',
        'home.selected_date'=>'Selected date','home.resolving'=>'Resolving location…','home.verified'=>'Verified engines',
        'home.tithi'=>'Tithi','home.nakshatra'=>'Nakshatra','home.yoga'=>'Yoga','home.lunar_month'=>'Lunar month',
        'home.sunrise'=>'Sunrise','home.sunset'=>'Sunset','home.moonrise'=>'Moonrise',
        'home.choghadiya'=>'Choghadiya','home.open_timeline'=>'Open timeline →',
        'home.abhijit'=>'Abhijit Muhurat','home.abhijit_note'=>'Deterministic local solar window','home.details'=>'Details →',
        'home.rahu'=>'Rahu Kaal','home.rahu_note'=>'Daily blocked-period reference',
        'home.upcoming'=>'Upcoming','home.next_days'=>'The next few days, already connected.',
        'home.upcoming_copy'=>'Vrat, Sankranti and planetary events are aggregated from their verified engines for the selected location and preference profile.',
        'home.ai_kicker'=>'New · Multi-engine intelligence','home.ai_title'=>'Don’t just read the Panchang. Ask what it means.',
        'home.ai_copy'=>'Use verified Panchang, Muhurat and Jyotish outputs with confidence and provenance attached to every synthesis.',
        'home.open_ai'=>'Open Tithika Intelligence',
        'home.page_title'=>'Modern Panchang, Muhurat & Jyotish','home.calculating'=>'Calculating…','home.local_sequence'=>'Local day/night sequence',
        'home.explore_kicker'=>'Explore Tithika','home.explore_title'=>'One platform, clear product families.','home.explore_copy'=>'Each family shares the same local context and calculation contracts, while specialized engines load only where they are needed.','home.production_routes'=>'{count} production-quality routes →',
        'groupdesc.panchang'=>'Daily, monthly and regional Panchang experiences with location-aware solar context.','groupdesc.calendars'=>'Regional, festival and yearly Vedic calendar views.','groupdesc.muhurat'=>'Daily and ceremony-specific auspicious timing utilities.','groupdesc.vrat'=>'Fasting dates, Parana windows and recurring observance calendars.','groupdesc.festivals'=>'Festival collections, month views, deity traditions and observance guides.','groupdesc.jyotish'=>'Birth, compatibility and traditional Jyotish calculators in focused flows.','groupdesc.planets'=>'Planetary positions, transits, aspects, eclipses and seasonal astronomy.','groupdesc.devotion'=>'Aarti, Chalisa, Stotram, Mantra and devotional reading collections.','groupdesc.gallery'=>'Visual collections for festivals, devotional art and traditional design.','groupdesc.learn'=>'Tutorials and explanatory content for Panchang, Muhurat and Vedic calendar concepts.',
        'home.stack_kicker'=>'Calculation stack','home.stack_title'=>'Built around evidence, not black boxes.','home.stack_copy'=>'Calculation pages keep astronomical state, observance rules, interpretation and timing layers inspectable.',
        'home.feature_intelligence_title'=>'Tithika Intelligence','home.feature_intelligence_copy'=>'Six explainable layers orchestrate Panchang, Muhurat and Jyotish engines with confidence, provenance, privacy-aware caching and cross-engine quality checks.','home.feature_intelligence_action'=>'Open Intelligence →',
        'home.feature_panchang_title'=>'Daily Panchang','home.feature_panchang_copy'=>'Tithi, Nakshatra, Yoga, Karana, lunar month and local solar context from the verified Lahiri Panchang engine.','home.feature_panchang_action'=>'Open Panchang →',
        'home.feature_muhurat_title'=>'Specialized Muhurat','home.feature_muhurat_copy'=>'Activity-specific windows with Panchang evidence, common blocked-period subtraction and versioned profiles.','home.feature_muhurat_action'=>'Find Muhurat →',
        'home.feature_jyotish_title'=>'Unified Jyotish','home.feature_jyotish_copy'=>'Kundali, Vargas, Shadbala, Ashtakavarga, Yogas, Dasha, interpretation and timing in one connected stack.','home.feature_jyotish_action'=>'Open analysis →',
        'home.feature_festival_title'=>'Festival rules','home.feature_festival_copy'=>'Major observances resolve exact Tithi windows through reusable sunrise, Madhyahna, Pradosh and Nishita selectors.','home.feature_festival_action'=>'Browse festivals →',
        'home.reference_kicker'=>'Reference & devotion','home.reference_title'=>'Content stays separate from calculation logic.','home.reference_copy'=>'Learn, Devotion and Gallery routes use a structured editorial layer, making them useful without embedding third-party text or media into the core engine.',
        'home.feature_learn_title'=>'Learn Panchang','home.feature_learn_copy'=>'Understand the five limbs, sunrise-state conventions and how Tithika separates astronomy from observance rules.','home.feature_learn_action'=>'Read guide →',
        'home.feature_devotion_title'=>'Devotion library','home.feature_devotion_copy'=>'Structured devotional taxonomy with practice context and links back to relevant festival and timing tools.','home.feature_devotion_action'=>'Open library →',
        'home.feature_gallery_title'=>'Visual index','home.feature_gallery_copy'=>'Lightweight original gallery surfaces that do not slow calculation-heavy pages or depend on external artwork.','home.feature_gallery_action'=>'Open gallery →',
        'home.feature_map_title'=>'Complete product map','home.feature_map_copy'=>'Browse all {count} mapped routes and see which parts of the platform are calculation, content, calendar or reference surfaces.','home.feature_map_action'=>'Open site map →',
        'settings.title'=>'Settings & Profile','settings.kicker'=>'Local-first preferences','settings.hero'=>'Make Tithika yours.',
        'settings.intro'=>'Choose your visual theme, time format, lunar-month convention, preferred tradition, language and default location. Settings stay in this browser; no account or database is required.',
        'settings.privacy'=>'Privacy model','settings.local'=>'Stored locally.',
        'settings.privacy_copy'=>'Birth data is not stored here. Only explicit product preferences and an optional saved location are retained in browser storage.',
        'settings.appearance'=>'Appearance','settings.theme'=>'Theme','settings.system'=>'System','settings.system_note'=>'Follow device appearance',
        'settings.light'=>'Light','settings.light_note'=>'Bright editorial interface','settings.dark'=>'Dark','settings.dark_note'=>'Low-light premium interface',
        'settings.time'=>'Time display','settings.clock'=>'Clock','settings.12'=>'12-hour','settings.24'=>'24-hour',
        'settings.lunar'=>'Lunar calendar','settings.month'=>'Month convention','settings.amanta'=>'Amanta','settings.amanta_note'=>'Month ends at Amavasya',
        'settings.purnimanta'=>'Purnimanta','settings.purnimanta_note'=>'Month ends at Purnima',
        'settings.observance'=>'Observance preference','settings.tradition'=>'Tradition','settings.smarta'=>'Smarta',
        'settings.smarta_note'=>'General household convention','settings.vaishnava'=>'Vaishnava','settings.vaishnava_note'=>'Vaishnava observance profile',
        'settings.iskcon'=>'ISKCON','settings.iskcon_note'=>'ISKCON-compatible Ekadashi profile',
        'settings.language'=>'Language','settings.language_title'=>'Interface language','settings.english'=>'English','settings.hindi'=>'हिन्दी',
        'settings.language_note'=>'Shared navigation, dashboard and settings translate without duplicating product routes.','settings.english_note'=>'English interface','settings.hindi_note'=>'Hindi interface',
        'settings.numerals'=>'Numerals','settings.numerals_title'=>'Number display','settings.latin'=>'Latin','settings.latin_note'=>'0 1 2 3 · standard digits','settings.devanagari'=>'Devanagari','settings.devanagari_note'=>'० १ २ ३ · Indic digits',
        'settings.context'=>'Default context','settings.saved_location'=>'Saved location','settings.no_location'=>'No saved location',
        'settings.location_fallback'=>'Tithika will continue using geolocation or the standard fallback.',
        'settings.save_location'=>'Save current selected location','settings.clear'=>'Clear',
        'settings.future'=>'Designed for future localization.',
        'settings.future_copy'=>'The locale contract supports additional dictionaries without duplicating calculation pages. Hindi is the first production locale.',
        'dynamic.today'=>'Today','dynamic.tomorrow'=>'Tomorrow','dynamic.days_away'=>'days away',
        'dynamic.current_location'=>'Selected location','dynamic.no_events'=>'No major tracked events fall inside this dashboard horizon. Open the full calendars for the complete year.',
        'dynamic.dashboard_error'=>'Daily dashboard could not refresh. The individual Panchang and Muhurat tools remain available.','dynamic.dashboard_lead'=>'For {location}, {tithi} aligns with {nakshatra}. The dashboard keeps timing, observances and planet events in one local context.','dynamic.amanta'=>'Amanta','dynamic.purnimanta'=>'Purnimanta','dynamic.location_saved'=>'Default location saved on this device.',
        'dynamic.moon'=>'Moon','dynamic.karana'=>'Karana','dynamic.preference'=>'preference','dynamic.next'=>'Next','dynamic.no_active'=>'No active period','dynamic.open_timeline'=>'Open the full timeline for all periods','dynamic.view_details'=>'View details →','dynamic.upcoming_event'=>'Upcoming event','dynamic.verified_event'=>'Verified Tithika event','dynamic.unable_feed'=>'Unable to load the aggregated event feed right now.',
      ],
      'hi'=>[
        'brand.tagline'=>'वैदिक समय, नए रूप में',
        'nav.all_tools'=>'सभी साधन','nav.settings'=>'सेटिंग्स','nav.primary'=>'मुख्य',
        'nav.panchang'=>'पंचांग','nav.calendars'=>'कैलेंडर','nav.muhurat'=>'मुहूर्त',
        'nav.vrat'=>'व्रत और उपवास','nav.festivals'=>'त्योहार','nav.jyotish'=>'ज्योतिष',
        'skip.content'=>'मुख्य सामग्री पर जाएँ','location.label'=>'स्थान',
        'location.chooser'=>'स्थान चुनें','location.search'=>'शहर या स्थान खोजें',
        'location.use_current'=>'वर्तमान स्थान उपयोग करें','location.privacy'=>'आपके स्थान का उपयोग केवल स्थानीय सौर समय की गणना के लिए किया जाता है।',
        'footer.tagline'=>'आधुनिक, प्रमाण-आधारित अनुभव में पारंपरिक कैलेंडर परंपराएँ।',
        'footer.home'=>'मुखपृष्ठ','footer.sitemap'=>'साइट मानचित्र','footer.xml'=>'XML साइटमैप','footer.faq'=>'सामान्य प्रश्न',
        'home.kicker'=>'आपका दैनिक वैदिक डैशबोर्ड','home.title'=>'आज, स्पष्ट रूप से।',
        'home.loading'=>'आपके चुने हुए स्थान के लिए सत्यापित पंचांग, मुहूर्त और आगामी पर्व लोड हो रहे हैं…',
        'home.ask'=>'तिथिका इंटेलिजेंस से पूछें →','home.full_panchang'=>'पूरा पंचांग','home.personalize'=>'व्यक्तिगत बनाएँ',
        'home.selected_date'=>'चुनी हुई तिथि','home.resolving'=>'स्थान निर्धारित हो रहा है…','home.verified'=>'सत्यापित इंजन',
        'home.tithi'=>'तिथि','home.nakshatra'=>'नक्षत्र','home.yoga'=>'योग','home.lunar_month'=>'चंद्र मास',
        'home.sunrise'=>'सूर्योदय','home.sunset'=>'सूर्यास्त','home.moonrise'=>'चंद्रोदय',
        'home.choghadiya'=>'चौघड़िया','home.open_timeline'=>'समयरेखा खोलें →',
        'home.abhijit'=>'अभिजित मुहूर्त','home.abhijit_note'=>'स्थानीय सौर समय पर आधारित निश्चित अवधि','home.details'=>'विवरण →',
        'home.rahu'=>'राहु काल','home.rahu_note'=>'दैनिक वर्जित अवधि संदर्भ',
        'home.upcoming'=>'आगामी','home.next_days'=>'अगले कुछ दिन, एक ही स्थान पर।',
        'home.upcoming_copy'=>'व्रत, संक्रांति और ग्रह घटनाएँ चुने गए स्थान और परंपरा के अनुसार सत्यापित इंजनों से एकत्र की जाती हैं।',
        'home.ai_kicker'=>'नया · मल्टी-इंजन इंटेलिजेंस','home.ai_title'=>'सिर्फ पंचांग न पढ़ें। उसका अर्थ पूछें।',
        'home.ai_copy'=>'सत्यापित पंचांग, मुहूर्त और ज्योतिष परिणामों को विश्वास स्तर और स्रोत के साथ समझें।',
        'home.open_ai'=>'तिथिका इंटेलिजेंस खोलें',
        'home.page_title'=>'आधुनिक पंचांग, मुहूर्त और ज्योतिष','home.calculating'=>'गणना हो रही है…','home.local_sequence'=>'स्थानीय दिन/रात्रि क्रम',
        'home.explore_kicker'=>'तिथिका देखें','home.explore_title'=>'एक मंच, स्पष्ट उत्पाद समूह।','home.explore_copy'=>'हर समूह एक ही स्थानीय संदर्भ और गणना अनुबंध साझा करता है, जबकि विशेष इंजन केवल आवश्यकता होने पर लोड होते हैं।','home.production_routes'=>'{count} उत्पादन-स्तरीय रूट →',
        'groupdesc.panchang'=>'स्थान-आधारित सौर संदर्भ के साथ दैनिक, मासिक और क्षेत्रीय पंचांग अनुभव।','groupdesc.calendars'=>'क्षेत्रीय, पर्व और वार्षिक वैदिक कैलेंडर दृश्य।','groupdesc.muhurat'=>'दैनिक और संस्कार-विशिष्ट शुभ समय उपयोगिताएँ।','groupdesc.vrat'=>'उपवास तिथियाँ, पारण अवधि और आवर्ती व्रत कैलेंडर।','groupdesc.festivals'=>'त्योहार संग्रह, मासिक दृश्य, देव परंपराएँ और अनुष्ठान मार्गदर्शिकाएँ।','groupdesc.jyotish'=>'जन्म, अनुकूलता और पारंपरिक ज्योतिष गणनाएँ।','groupdesc.planets'=>'ग्रह स्थितियाँ, गोचर, दृष्टियाँ, ग्रहण और ऋतु खगोल।','groupdesc.devotion'=>'आरती, चालीसा, स्तोत्र, मंत्र और भक्ति पाठ संग्रह।','groupdesc.gallery'=>'त्योहार, भक्ति कला और पारंपरिक डिज़ाइन के दृश्य संग्रह।','groupdesc.learn'=>'पंचांग, मुहूर्त और वैदिक कैलेंडर के ट्यूटोरियल और व्याख्याएँ।',
        'home.stack_kicker'=>'गणना संरचना','home.stack_title'=>'ब्लैक बॉक्स नहीं, प्रमाण पर आधारित।','home.stack_copy'=>'गणना पृष्ठ खगोलीय स्थिति, अनुष्ठान नियम, व्याख्या और समय परतों को निरीक्षण योग्य रखते हैं।',
        'home.feature_intelligence_title'=>'तिथिका इंटेलिजेंस','home.feature_intelligence_copy'=>'छह व्याख्येय परतें पंचांग, मुहूर्त और ज्योतिष इंजनों को विश्वास स्तर, स्रोत, गोपनीयता-अनुकूल कैशिंग और क्रॉस-इंजन गुणवत्ता जांच के साथ जोड़ती हैं।','home.feature_intelligence_action'=>'इंटेलिजेंस खोलें →',
        'home.feature_panchang_title'=>'दैनिक पंचांग','home.feature_panchang_copy'=>'सत्यापित लाहिड़ी पंचांग इंजन से तिथि, नक्षत्र, योग, करण, चंद्र मास और स्थानीय सौर संदर्भ।','home.feature_panchang_action'=>'पंचांग खोलें →',
        'home.feature_muhurat_title'=>'विशेष मुहूर्त','home.feature_muhurat_copy'=>'पंचांग प्रमाण, वर्जित अवधियों को हटाने और संस्करणित प्रोफ़ाइल के साथ कार्य-विशिष्ट शुभ समय।','home.feature_muhurat_action'=>'मुहूर्त खोजें →',
        'home.feature_jyotish_title'=>'एकीकृत ज्योतिष','home.feature_jyotish_copy'=>'कुंडली, वर्ग, षड्बल, अष्टकवर्ग, योग, दशा, व्याख्या और समय—एक जुड़े हुए तंत्र में।','home.feature_jyotish_action'=>'विश्लेषण खोलें →',
        'home.feature_festival_title'=>'त्योहार नियम','home.feature_festival_copy'=>'मुख्य पर्व पुनः उपयोग योग्य सूर्योदय, मध्याह्न, प्रदोष और निशीथ चयनकर्ताओं से सटीक तिथि-अवधि निर्धारित करते हैं।','home.feature_festival_action'=>'त्योहार देखें →',
        'home.reference_kicker'=>'संदर्भ और भक्ति','home.reference_title'=>'सामग्री गणना तर्क से अलग रहती है।','home.reference_copy'=>'सीखें, भक्ति और गैलरी रूट संरचित संपादकीय परत का उपयोग करते हैं, इसलिए कोर इंजन में तृतीय-पक्ष पाठ या मीडिया जोड़ने की आवश्यकता नहीं होती।',
        'home.feature_learn_title'=>'पंचांग सीखें','home.feature_learn_copy'=>'पंचांग के पाँच अंग, सूर्योदय-स्थिति परंपराएँ और खगोल को अनुष्ठान नियमों से अलग रखने की तिथिका पद्धति समझें।','home.feature_learn_action'=>'मार्गदर्शिका पढ़ें →',
        'home.feature_devotion_title'=>'भक्ति पुस्तकालय','home.feature_devotion_copy'=>'अनुष्ठान संदर्भ और संबंधित त्योहार/समय साधनों के लिंक के साथ संरचित भक्ति वर्गीकरण।','home.feature_devotion_action'=>'पुस्तकालय खोलें →',
        'home.feature_gallery_title'=>'दृश्य सूची','home.feature_gallery_copy'=>'हल्के मूल गैलरी पृष्ठ जो गणना-भारी पृष्ठों को धीमा नहीं करते और बाहरी कलाकृति पर निर्भर नहीं हैं।','home.feature_gallery_action'=>'गैलरी खोलें →',
        'home.feature_map_title'=>'पूरा उत्पाद मानचित्र','home.feature_map_copy'=>'सभी {count} मैप किए गए रूट देखें और समझें कि कौन से भाग गणना, सामग्री, कैलेंडर या संदर्भ पृष्ठ हैं।','home.feature_map_action'=>'साइट मानचित्र खोलें →',
        'settings.title'=>'सेटिंग्स और प्रोफ़ाइल','settings.kicker'=>'स्थानीय प्राथमिकताएँ','settings.hero'=>'तिथिका को अपने अनुसार बनाएँ।',
        'settings.intro'=>'थीम, समय प्रारूप, चंद्र मास पद्धति, परंपरा, भाषा और डिफ़ॉल्ट स्थान चुनें। ये सेटिंग्स इसी ब्राउज़र में रहती हैं; खाता या डेटाबेस आवश्यक नहीं है।',
        'settings.privacy'=>'गोपनीयता मॉडल','settings.local'=>'स्थानीय रूप से संग्रहीत।',
        'settings.privacy_copy'=>'जन्म डेटा यहाँ संग्रहीत नहीं होता। केवल आपकी स्पष्ट प्राथमिकताएँ और वैकल्पिक डिफ़ॉल्ट स्थान ब्राउज़र में रखे जाते हैं।',
        'settings.appearance'=>'रूप','settings.theme'=>'थीम','settings.system'=>'सिस्टम','settings.system_note'=>'डिवाइस की थीम अपनाएँ',
        'settings.light'=>'लाइट','settings.light_note'=>'उज्ज्वल संपादकीय इंटरफ़ेस','settings.dark'=>'डार्क','settings.dark_note'=>'कम रोशनी के लिए इंटरफ़ेस',
        'settings.time'=>'समय प्रदर्शन','settings.clock'=>'घड़ी','settings.12'=>'12-घंटे','settings.24'=>'24-घंटे',
        'settings.lunar'=>'चंद्र कैलेंडर','settings.month'=>'मास पद्धति','settings.amanta'=>'अमांत','settings.amanta_note'=>'मास अमावस्या पर समाप्त',
        'settings.purnimanta'=>'पूर्णिमांत','settings.purnimanta_note'=>'मास पूर्णिमा पर समाप्त',
        'settings.observance'=>'अनुष्ठान प्राथमिकता','settings.tradition'=>'परंपरा','settings.smarta'=>'स्मार्त',
        'settings.smarta_note'=>'सामान्य गृहस्थ परंपरा','settings.vaishnava'=>'वैष्णव','settings.vaishnava_note'=>'वैष्णव व्रत पद्धति',
        'settings.iskcon'=>'ISKCON','settings.iskcon_note'=>'ISKCON-अनुकूल एकादशी पद्धति',
        'settings.language'=>'भाषा','settings.language_title'=>'इंटरफ़ेस भाषा','settings.english'=>'English','settings.hindi'=>'हिन्दी',
        'settings.language_note'=>'मुख्य नेविगेशन, डैशबोर्ड और सेटिंग्स उत्पाद पृष्ठों की नकल किए बिना अनुवादित होते हैं।','settings.english_note'=>'अंग्रेज़ी इंटरफ़ेस','settings.hindi_note'=>'हिन्दी इंटरफ़ेस',
        'settings.numerals'=>'अंक','settings.numerals_title'=>'संख्या प्रदर्शन','settings.latin'=>'लैटिन','settings.latin_note'=>'0 1 2 3 · मानक अंक','settings.devanagari'=>'देवनागरी','settings.devanagari_note'=>'० १ २ ३ · भारतीय अंक',
        'settings.context'=>'डिफ़ॉल्ट संदर्भ','settings.saved_location'=>'सहेजा स्थान','settings.no_location'=>'कोई सहेजा स्थान नहीं',
        'settings.location_fallback'=>'तिथिका जियोलोकेशन या मानक डिफ़ॉल्ट का उपयोग जारी रखेगा।',
        'settings.save_location'=>'वर्तमान चुना स्थान सहेजें','settings.clear'=>'हटाएँ',
        'settings.future'=>'भविष्य के स्थानीयकरण के लिए तैयार।',
        'settings.future_copy'=>'लोकेल प्रणाली अतिरिक्त भाषाएँ जोड़ सकती है, बिना गणना पृष्ठों की नकल किए। हिन्दी पहला उत्पादन लोकेल है।',
        'dynamic.today'=>'आज','dynamic.tomorrow'=>'कल','dynamic.days_away'=>'दिन बाद',
        'dynamic.current_location'=>'चुना स्थान','dynamic.no_events'=>'इस अवधि में कोई प्रमुख ट्रैक की गई घटना नहीं मिली। पूरे वर्ष के लिए कैलेंडर खोलें।',
        'dynamic.dashboard_error'=>'दैनिक डैशबोर्ड रीफ़्रेश नहीं हो सका। अलग-अलग पंचांग और मुहूर्त साधन उपलब्ध हैं।','dynamic.dashboard_lead'=>'{location} के लिए {tithi} का संबंध {nakshatra} से है। यह डैशबोर्ड समय, व्रत-पर्व और ग्रह घटनाओं को एक ही स्थानीय संदर्भ में दिखाता है।','dynamic.amanta'=>'अमांत','dynamic.purnimanta'=>'पूर्णिमांत','dynamic.location_saved'=>'डिफ़ॉल्ट स्थान इस डिवाइस पर सहेजा गया।',
        'dynamic.moon'=>'चंद्र','dynamic.karana'=>'करण','dynamic.preference'=>'प्राथमिकता','dynamic.next'=>'अगला','dynamic.no_active'=>'कोई सक्रिय अवधि नहीं','dynamic.open_timeline'=>'सभी अवधियों की समयरेखा खोलें','dynamic.view_details'=>'विवरण देखें →','dynamic.upcoming_event'=>'आगामी घटना','dynamic.verified_event'=>'सत्यापित तिथिका घटना','dynamic.unable_feed'=>'समेकित घटना सूची अभी लोड नहीं हो सकी।',
      ],
    ];
    return $dict;
}

function tithika_t(string $key, ?string $fallback = null, array $vars = []): string {
    $dict = tithika_dictionary();
    $locale = tithika_locale();
    $value = $dict[$locale][$key] ?? $dict['en'][$key] ?? $fallback ?? $key;
    foreach ($vars as $name=>$replacement) {
        $value = str_replace('{'.$name.'}', (string)$replacement, $value);
    }
    return $value;
}

function tithika_client_messages(): array {
    $dict = tithika_dictionary();
    $locale = tithika_locale();
    return [
        'locale'=>$locale,
        'messages'=>$dict[$locale] ?? $dict['en'],
    ];
}
