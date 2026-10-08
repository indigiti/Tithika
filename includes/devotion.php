<?php
declare(strict_types=1);

/**
 * Source-aware Devotion corpus.
 *
 * All prose in this registry is original Tithika editorial content. Sacred
 * source texts are not reproduced here unless a specific public-domain or
 * licensed edition is separately verified and attributed.
 */

function tithika_devotion_entry(
    string $summary,
    string $practice,
    string $observance,
    array $items = [],
    array $links = [],
    string $kind = 'reference'
): array {
    return [
        'kind'=>$kind,
        'summary'=>$summary,
        'practice'=>$practice,
        'observance'=>$observance,
        'items'=>$items,
        'links'=>$links,
        'source'=>[
            'editorial'=>'original-tithika',
            'sacred_text'=>'not-embedded',
            'policy'=>'Route metadata and explanatory prose are original. Any full hymn, mantra or scripture edition requires verified public-domain or licensed sourcing before publication.',
        ],
    ];
}

function tithika_devotion_registry(): array {
    return [
        'devotion/aarti'=>tithika_devotion_entry(
            'Aarti is a light-offering tradition used in household and temple worship. This collection organizes deity-specific Aarti subjects without treating one regional sequence as universal.',
            'Aarti commonly follows Puja or Darshan and may use lamps, incense, bells and sung praise. Language and sequence vary by household, temple and Sampradaya.',
            'Use local festival and Puja timings when the Aarti belongs to a date-specific observance; daily household Aarti is not assigned a universal clock time.',
            ['Ganesha Aarti','Lakshmi Aarti','Shiva Aarti','Hanuman Aarti','Durga Aarti','Krishna Aarti'],
            ['devotion/marathi-aarti','festivals/diwali','festivals/ganesha-chaturthi','panchang/daily'],
            'collection'
        ),
        'devotion/chalisa'=>tithika_devotion_entry(
            'Chalisa literature is a family of forty-verse devotional compositions dedicated to particular deities. Tithika indexes the tradition while keeping edition-specific wording outside the generic corpus.',
            'Recitation practice depends on the chosen composition, language and lineage. A complete text should always identify its edition or source.',
            'Chalisa recitation can be daily or associated with deity weekdays, festivals and Vratas; timing is contextual rather than fixed by the composition form itself.',
            ['Hanuman Chalisa','Durga Chalisa','Shiva Chalisa','Ganesha Chalisa','Lakshmi Chalisa','Saraswati Chalisa'],
            ['devotion/gods/lord-ganesha','devotion/gods/lord-shiva','devotion/goddesses/saraswati','panchang/daily'],
            'collection'
        ),
        'devotion/stotram'=>tithika_devotion_entry(
            'Stotra is a broad hymn tradition spanning praise, philosophical contemplation and deity-specific liturgy. This index separates named works from generic devotional prose.',
            'Pronunciation, metre and textual recension matter. Tithika therefore treats each full Stotra as a source-controlled edition rather than auto-generating missing verses.',
            'Some Stotras are linked to festivals or deity weekdays, while many are recited independently of a calendar event.',
            ['Shiva Tandava Stotram','Kanakadhara Stotram','Ganesha Pancharatnam','Aditya Hridayam','Mahishasura Mardini Stotram','Vishnu Stotra traditions'],
            ['devotion/ashtakam','devotion/kavacham','devotion/gods/lord-vishnu','devotion/gods/lord-shiva'],
            'collection'
        ),
        'devotion/mantra'=>tithika_devotion_entry(
            'Mantra practice ranges from Vedic recitation to deity-specific Nama and Bija traditions. This collection emphasizes source, pronunciation and practice context rather than presenting every formula as interchangeable.',
            'Traditional Mantra practice can involve initiation, prescribed counts, Nyasa or specific pronunciation rules. Those requirements differ by tradition and should not be inferred from a generic page.',
            'Calendar timing may matter for a particular Puja or vrata, but many daily Mantras are not restricted to one Muhurat.',
            ['Gayatri traditions','Ganesha Mantras','Mahalakshmi Mantras','Shanti Path','Navagraha Mantras','Festival Mantras'],
            ['devotion/mantra/gayatri','devotion/mantra/ganesha','devotion/mantra/mahalakshmi','devotion/mantra/shanti-path'],
            'collection'
        ),
        'devotion/namavali'=>tithika_devotion_entry(
            'Namavali practice invokes a deity through a sequence of sacred names. Counts such as 108 or 1000 belong to specific texts and traditions and should be identified explicitly.',
            'A Namavali may be recited independently or offered name-by-name with flowers, Akshata or other Puja materials.',
            'Use the related deity festival or Puja timing when the Namavali is part of a scheduled observance; otherwise it can be part of regular worship.',
            ['Ganesha Namavali','Vishnu Namavali','Shiva Namavali','Lakshmi Namavali','Saraswati Namavali','Durga Namavali'],
            ['devotion/gods/lord-ganesha','devotion/gods/lord-vishnu','devotion/gods/lord-shiva','devotion/goddesses/mahalakshmi'],
            'collection'
        ),
        'devotion/durga-saptashati'=>tithika_devotion_entry(
            'Durga Saptashati, also known through the Devi Mahatmya tradition, is a major Shakta scripture associated especially with Navratri and Chandi worship.',
            'Recitation traditions can include preliminary and concluding auxiliaries as well as the core chapters. Sequence and ritual requirements vary by lineage.',
            'Navratri is the most prominent calendar connection; use Tithika festival dates for the local observance rather than assuming a fixed Gregorian period.',
            ['Devi Mahatmya core chapters','Kavacha tradition','Argala tradition','Kilaka tradition','Navratri recitation cycle'],
            ['festivals/navratri','calendars/navratri','devotion/kavacham','devotion/goddesses/dasha-mahavidya'],
            'scripture-reference'
        ),
        'devotion/marathi-aarti'=>tithika_devotion_entry(
            'Marathi Aarti traditions form a distinctive household and temple repertoire across Maharashtra. This index keeps the regional context visible instead of collapsing the works into a generic Hindi-language collection.',
            'Melody, wording and order can vary by family and temple. A published text edition should preserve its Marathi source and orthography.',
            'Many Marathi Aartis are used daily and during Ganeshotsav, Navratri, Datta worship, Vitthal worship and other regional observances.',
            ['Sukhakarta Dukhaharta tradition','Vitthal Aarti traditions','Devi Aarti traditions','Shiva Aarti traditions','Datta Aarti traditions','Maruti Aarti traditions'],
            ['devotion/aarti','festivals/ganesha-chaturthi','festivals/navratri','panchang/marathi'],
            'collection'
        ),
        'devotion/ashtakam'=>tithika_devotion_entry(
            'Ashtakam is an eight-verse hymn form used across Shaiva, Vaishnava, Shakta and other devotional traditions.',
            'The eight-verse form does not imply one ritual method. Each named Ashtakam should retain its own attribution, recension and pronunciation notes.',
            'Ashtakams can be recited daily or on deity-specific observances; the calendar connection comes from the selected deity or festival, not from the verse count.',
            ['Lingashtakam','Kalabhairava Ashtakam','Madhurashtakam','Achyutashtakam','Bilvashtakam','Mahalakshmi Ashtakam'],
            ['devotion/stotram','devotion/gods/lord-shiva','devotion/goddesses/mahalakshmi','panchang/daily'],
            'collection'
        ),
        'devotion/shatkam'=>tithika_devotion_entry(
            'Shatkam denotes a six-verse composition form found in devotional and philosophical hymn traditions.',
            'Because attribution and textual recension vary across named Shatkams, Tithika keeps this page as a source-aware index until each edition is separately verified.',
            'The form itself has no universal festival date or Muhurat requirement.',
            ['Six-verse philosophical hymns','Six-verse deity hymns','Teacher-attributed recitation traditions'],
            ['devotion/stotram','learn/tutorials','panchang/daily'],
            'collection'
        ),
        'devotion/kavacham'=>tithika_devotion_entry(
            'Kavacha literature presents protective hymn and invocation traditions associated with particular deities.',
            'Some Kavachas are embedded in larger scriptures and can carry Nyasa, viniyoga or lineage-specific preliminaries. A complete edition must identify that context.',
            'Kavacha recitation may be daily or associated with Navratri, deity weekdays and special Puja observances.',
            ['Devi Kavacha traditions','Narayana Kavacha traditions','Hanuman Kavacha traditions','Ganesha Kavacha traditions','Navagraha protective traditions'],
            ['devotion/durga-saptashati','devotion/gods/navagraha','festivals/navratri','panchang/daily'],
            'collection'
        ),
        'devotion/sundarkand'=>tithika_devotion_entry(
            'Sundarkand is the Ramayana section centered on Hanuman’s journey to Lanka, the search for Sita and the delivery of Rama’s message.',
            'Recitation practice differs by Ramayana edition, language and regional tradition. Tithika does not mix verses from different recensions.',
            'Sundarkand is often recited as a regular devotional practice or on Hanuman-associated days; the text itself does not require one universal Muhurat.',
            ['Hanuman’s leap toward Lanka','Search in Lanka','Meeting with Sita','Return with the message'],
            ['devotion/hanuman-bahuk','festivals/hanuman-jayanti','devotion/nama-ramayanam','panchang/daily'],
            'scripture-reference'
        ),
        'devotion/hanuman-bahuk'=>tithika_devotion_entry(
            'Hanuman Bahuk is a devotional composition traditionally associated with Tulsidas and Hanuman worship.',
            'Published editions can differ in orthography and commentary. Tithika keeps the work’s identity and practice context separate from any unverified text transcription.',
            'It is commonly connected with Hanuman devotion and Tuesday or Saturday practice, without a single mandatory clock-time rule.',
            ['Hanuman devotion','Tulsidas tradition','Hindi devotional recitation'],
            ['festivals/hanuman-jayanti','devotion/sundarkand','devotion/chalisa','panchang/daily'],
            'work-reference'
        ),
        'devotion/nama-ramayanam'=>tithika_devotion_entry(
            'Nama Ramayanam retells the Ramayana through a compact sequence of sacred names and episode references.',
            'Versions differ by language and lineage, so the sequence should be sourced as a named edition rather than reconstructed automatically.',
            'It can be used in regular Rama devotion and around Rama Navami observance.',
            ['Bala Kanda names','Ayodhya Kanda names','Aranya Kanda names','Kishkindha Kanda names','Sundara Kanda names','Yuddha Kanda names'],
            ['festivals/rama-navami','devotion/sundarkand','devotion/eka-shloki-ramayana','panchang/daily'],
            'work-reference'
        ),
        'devotion/eka-shloki-ramayana'=>tithika_devotion_entry(
            'Eka Shloki Ramayana is a one-verse synopsis tradition that compresses the major Ramayana narrative into a mnemonic devotional form.',
            'The verse should be published only from a verified Sanskrit edition with transliteration and translation kept as separate editorial fields.',
            'It is suitable as a compact Rama devotional reference and can be linked to Rama Navami without implying a festival-only use.',
            ['One-verse Ramayana synopsis','Sanskrit edition slot','Transliteration slot','Meaning and episode map'],
            ['festivals/rama-navami','devotion/nama-ramayanam','devotion/sundarkand'],
            'work-reference'
        ),
        'devotion/yantra'=>tithika_devotion_entry(
            'Yantra traditions use sacred geometry as a ritual and contemplative support. Geometry, deity association and consecration practice should remain explicitly sourced.',
            'A diagram alone is not equivalent to a consecrated Yantra. Installation, Nyasa and Puja requirements vary by tradition.',
            'Some Yantras are installed or worshipped on festival or Muhurat dates; use the relevant calculation page for local timing.',
            ['Sri Yantra traditions','Ganesha Yantra','Kubera Yantra','Lakshmi-Ganesha Yantra','Mahavidya Yantras'],
            ['devotion/yantra/puja','devotion/yantra/ganesha','devotion/yantra/kubera','devotion/yantra/mahavidya'],
            'collection'
        ),
        'devotion/gods/ashta-vinayaka'=>tithika_devotion_entry(
            'Ashta Vinayaka refers to the eight celebrated Ganesha temple forms of Maharashtra and the pilgrimage tradition connecting them.',
            'Temple order and pilgrimage custom are regional practices distinct from generic Ganesha Puja.',
            'Ganesh Chaturthi is an important related festival, while individual temple visits follow their own schedules.',
            ['Mayureshwar','Siddhivinayak','Ballaleshwar','Varadvinayak','Chintamani','Girijatmaj','Vighneshwar','Mahaganapati'],
            ['festivals/ganesha-chaturthi','devotion/gods/lord-ganesha','devotion/mantra/ganesha','panchang/marathi'],
            'deity-reference'
        ),
        'devotion/gods/lord-vishnu'=>tithika_devotion_entry(
            'Vishnu devotion spans temple worship, Nama traditions, Ekadashi observance and multiple Vaishnava Sampradayas.',
            'Practice can include Archana, Nama Japa, Stotra and scripture reading. Sampradaya-specific requirements should remain explicit.',
            'Ekadashi, Vaishnava festival dates and Vishnu-avatar observances are the main calendar connections.',
            ['Vishnu Nama traditions','Dashavatara context','Ekadashi observance','Vaishnava temple worship'],
            ['vrat/ekadashi','festivals/vishnu-avatars','devotion/namavali','devotion/stotram'],
            'deity-reference'
        ),
        'devotion/gods/navagraha'=>tithika_devotion_entry(
            'Navagraha worship addresses the nine traditional Grahas as a ritual system distinct from astronomical planet-position calculation.',
            'Mantra, Dana, Puja and temple customs vary by Graha and tradition. Tithika keeps ritual reference separate from predictive claims.',
            'Weekday fasting and Graha-specific observances can be linked to current planetary calculations without treating astronomy as ritual prescription.',
            ['Surya','Chandra','Mangala','Budha','Guru','Shukra','Shani','Rahu','Ketu'],
            ['vrat/navagraha-weekdays','planets/positions','devotion/mantra','panchang/daily'],
            'deity-reference'
        ),
        'devotion/gods/lord-kubera'=>tithika_devotion_entry(
            'Kubera is associated with wealth guardianship in Hindu, Buddhist and Jain traditions, with distinct ritual contexts.',
            'Kubera Puja, Mantra and Yantra practices should identify the tradition being followed rather than combining them into one universal procedure.',
            'Dhanteras and Diwali are common popular associations; local Puja timing should come from the relevant festival calculation.',
            ['Kubera Puja context','Kubera Mantra traditions','Kubera Yantra traditions'],
            ['devotion/yantra/kubera','festivals/diwali','devotion/mantra/diwali'],
            'deity-reference'
        ),
        'devotion/gods/lord-ganesha'=>tithika_devotion_entry(
            'Ganesha worship is widely associated with beginnings, obstacle removal, learning and auspicious initiation.',
            'Practice ranges from simple household Archana to temple and festival Puja. Regional forms and Mantras should remain separately identified.',
            'Ganesh Chaturthi, Sankashti Chaturthi and Vinayaka Chaturthi are the main recurring calendar connections.',
            ['Ganesha Puja','Sankashti tradition','Ganesha Mantra','Ashta Vinayaka'],
            ['festivals/ganesha-chaturthi','vrat/sankashti-chaturthi','vrat/vinayaka-chaturthi','devotion/mantra/ganesha'],
            'deity-reference'
        ),
        'devotion/gods/lord-shiva'=>tithika_devotion_entry(
            'Shiva devotion includes Linga worship, Nama Japa, Stotra, Abhisheka and Shaiva festival observances.',
            'Temple, household and Sampradaya practices differ; a ritual guide should state whether it is general, Agamic or lineage-specific.',
            'Maha Shivaratri, Masik Shivaratri and Pradosha are key calendar connections.',
            ['Shiva Puja','Linga worship','Shiva Stotra','Pradosha context'],
            ['festivals/maha-shivaratri','vrat/masik-shivaratri','vrat/pradosham','devotion/ashtakam'],
            'deity-reference'
        ),
        'devotion/goddesses/mahalakshmi'=>tithika_devotion_entry(
            'Mahalakshmi devotion centers on prosperity, auspiciousness and household well-being across multiple regional traditions.',
            'Archana, Stotra, Mantra and Lakshmi Puja forms vary by region and festival context.',
            'Diwali Lakshmi Puja and other Lakshmi Vratas are key calendar associations.',
            ['Lakshmi Puja','Mahalakshmi Mantras','Lakshmi Namavali','Ashta Lakshmi'],
            ['festivals/diwali','devotion/mantra/mahalakshmi','devotion/goddesses/ashta-lakshmi','devotion/namavali'],
            'deity-reference'
        ),
        'devotion/goddesses/ashta-lakshmi'=>tithika_devotion_entry(
            'Ashta Lakshmi is a devotional grouping of eight Lakshmi forms representing distinct dimensions of abundance and well-being.',
            'Names and iconographic details can vary by published tradition; the grouping should be sourced consistently.',
            'The forms are often invoked in Lakshmi worship and festival contexts rather than assigned separate universal calendar dates.',
            ['Adi Lakshmi','Dhana Lakshmi','Dhanya Lakshmi','Gaja Lakshmi','Santana Lakshmi','Veera Lakshmi','Vijaya Lakshmi','Vidya Lakshmi'],
            ['devotion/goddesses/mahalakshmi','festivals/diwali','devotion/mantra/mahalakshmi'],
            'deity-reference'
        ),
        'devotion/goddesses/dasha-mahavidya'=>tithika_devotion_entry(
            'Dasha Mahavidya refers to a major Shakta grouping of ten goddess forms, each with distinct theological and Tantric traditions.',
            'Mantra, Yantra and ritual details can be initiation-dependent and should never be generalized from another Mahavidya.',
            'Some traditions maintain Mahavidya-specific observances; Tithika keeps those separate from the general festival calendar until individually sourced.',
            ['Kali','Tara','Tripurasundari','Bhuvaneshwari','Bhairavi','Chhinnamasta','Dhumavati','Bagalamukhi','Matangi','Kamala'],
            ['calendars/dasha-mahavidya','devotion/yantra/mahavidya','festivals/navratri'],
            'deity-reference'
        ),
        'devotion/goddesses/saraswati'=>tithika_devotion_entry(
            'Saraswati is associated with learning, speech, music and knowledge traditions.',
            'Worship can include simple Archana, study-related prayers, Mantra and festival Puja.',
            'Vasant Panchami and regional Saraswati Puja observances are important calendar connections.',
            ['Saraswati Puja','Saraswati Mantra traditions','Study invocation','Music and learning context'],
            ['calendars/saraswati-puja','devotion/mantra','devotion/namavali'],
            'deity-reference'
        ),
        'devotion/goddesses/gayatri'=>tithika_devotion_entry(
            'Gayatri is both a Vedic metre and a major devotional identity associated especially with the Savitri-Gayatri tradition.',
            'Vedic recitation has pronunciation and lineage requirements. Tithika separates a Mantra edition from general deity-reference content.',
            'Sandhya practice is a major traditional context; exact daily solar times can be derived from the local Panchang.',
            ['Gayatri deity context','Savitri-Gayatri tradition','Sandhya connection','Gayatri Mantra reference'],
            ['devotion/mantra/gayatri','panchang/sunrise','panchang/daily'],
            'deity-reference'
        ),
        'devotion/mantra/mahalakshmi'=>tithika_devotion_entry(
            'Mahalakshmi Mantra traditions include Nama, Stotra-linked and ritual formulas used in different Lakshmi worship contexts.',
            'A complete Mantra entry should identify its Sanskrit source or lineage, transliteration scheme and whether initiation is traditionally required.',
            'Diwali and Lakshmi Puja are major calendar contexts, but daily Lakshmi devotion is also common.',
            ['Mahalakshmi invocation index','Lakshmi Nama practice','Diwali Puja context'],
            ['devotion/goddesses/mahalakshmi','festivals/diwali','devotion/namavali'],
            'mantra-reference'
        ),
        'devotion/mantra/diwali'=>tithika_devotion_entry(
            'Diwali Mantras are not one single canonical text; households may use Ganesha, Lakshmi, Kubera and other invocations during the festival.',
            'The Mantra set should follow the chosen Puja tradition and source instead of combining unrelated formulas into an invented universal sequence.',
            'Use the local Diwali and Lakshmi Puja timings for the selected location.',
            ['Ganesha invocation context','Lakshmi invocation context','Kubera invocation context','Shanti prayer context'],
            ['festivals/diwali','calendars/diwali','devotion/gods/lord-kubera','devotion/goddesses/mahalakshmi'],
            'mantra-reference'
        ),
        'devotion/mantra/ganesha'=>tithika_devotion_entry(
            'Ganesha Mantra practice includes widely used Nama and invocation formulas as well as lineage-specific Bija traditions.',
            'Bija and Tantric forms should not be presented as interchangeable with public devotional Nama Mantras.',
            'Ganesh Chaturthi, Sankashti and the start of auspicious activities are common practice contexts.',
            ['Public Ganesha invocation index','Nama Japa context','Festival Puja context'],
            ['devotion/gods/lord-ganesha','festivals/ganesha-chaturthi','vrat/sankashti-chaturthi'],
            'mantra-reference'
        ),
        'devotion/mantra/gayatri'=>tithika_devotion_entry(
            'The Savitri-Gayatri Mantra is one of the best-known Vedic recitation traditions and requires careful source and pronunciation handling.',
            'A production text edition should provide verified Devanagari, transliteration, accent/pronunciation guidance where appropriate, and source attribution.',
            'Traditional Sandhya practice links recitation with dawn, midday and dusk; Tithika can calculate the local solar context.',
            ['Verified Sanskrit edition slot','Transliteration slot','Meaning slot','Sandhya timing link'],
            ['devotion/goddesses/gayatri','panchang/sunrise','panchang/daily'],
            'mantra-reference'
        ),
        'devotion/mantra/shanti-path'=>tithika_devotion_entry(
            'Shanti Path is a category of peace invocations found in multiple Upanishadic and Vedic recitation traditions rather than one universal verse.',
            'Each Shanti invocation must identify its textual source; formulas from different Vedic schools should remain distinct.',
            'Shanti recitation can frame study, ritual or daily prayer and is not tied to one festival date.',
            ['Upanishadic Shanti invocations','Study-opening context','Ritual-opening context'],
            ['devotion/mantra','learn/tutorials','panchang/daily'],
            'mantra-reference'
        ),
        'devotion/yantra/puja'=>tithika_devotion_entry(
            'Yantra Puja combines a specific sacred diagram with deity, Mantra and consecration traditions.',
            'Generic instructions cannot substitute for a lineage-specific Prana Pratishtha or Nyasa procedure. Tithika keeps this page as orientation and timing context.',
            'Installation or special Puja may use an auspicious Muhurat selected for the specific tradition.',
            ['Preparation context','Placement context','Puja sequence metadata','Source-controlled ritual slot'],
            ['devotion/yantra','muhurat/abhijit','muhurat/shubha-dates'],
            'ritual-reference'
        ),
        'devotion/yantra/lakshmi-ganesha'=>tithika_devotion_entry(
            'Lakshmi-Ganesha Yantra traditions combine auspiciousness, prosperity and obstacle-removal symbolism in a single worship context.',
            'Geometry and consecration method should be taken from a named tradition or published source rather than generated from a generic pattern.',
            'Diwali and Lakshmi Puja are common popular contexts for this combined form.',
            ['Lakshmi association','Ganesha association','Installation context'],
            ['festivals/diwali','devotion/goddesses/mahalakshmi','devotion/gods/lord-ganesha','devotion/yantra/puja'],
            'yantra-reference'
        ),
        'devotion/yantra/ganesha'=>tithika_devotion_entry(
            'Ganesha Yantra is a sacred-geometry tradition associated with Ganesha worship and auspicious beginnings.',
            'A production diagram should preserve the verified geometry and source tradition; decorative approximations should not be labelled as a ritual Yantra.',
            'Ganesh Chaturthi and activity-start Muhurats are natural related contexts.',
            ['Geometry source slot','Ganesha worship context','Installation timing'],
            ['festivals/ganesha-chaturthi','devotion/gods/lord-ganesha','devotion/yantra/puja'],
            'yantra-reference'
        ),
        'devotion/yantra/kubera'=>tithika_devotion_entry(
            'Kubera Yantra traditions are associated with Kubera worship and prosperity symbolism.',
            'The exact diagram and ritual procedure should come from a named source tradition; Tithika does not infer sacred geometry from decorative motifs.',
            'Dhanteras and Diwali are common popular contexts, with local timing supplied by festival calculations.',
            ['Geometry source slot','Kubera worship context','Festival timing context'],
            ['devotion/gods/lord-kubera','festivals/diwali','devotion/yantra/puja'],
            'yantra-reference'
        ),
        'devotion/yantra/mahavidya'=>tithika_devotion_entry(
            'Mahavidya Yantras belong to distinct goddess traditions and should not be collapsed into one generic diagram.',
            'Mantra, Yantra and ritual practice can be initiation-dependent. Each Mahavidya requires its own source-controlled entry.',
            'Calendar associations vary by the selected Mahavidya and tradition.',
            ['Kali Yantra reference','Tara Yantra reference','Tripurasundari Sri Chakra context','Bagalamukhi Yantra reference','Other Mahavidya source slots'],
            ['devotion/goddesses/dasha-mahavidya','calendars/dasha-mahavidya','devotion/yantra/puja'],
            'yantra-reference'
        ),
        'devotion/rituals/kumbha-mela'=>tithika_devotion_entry(
            'Kumbha Mela is a major pilgrimage and bathing-festival tradition whose location and cycle depend on specific astronomical and calendrical combinations.',
            'Ritual practice centers on pilgrimage, Snana and Akhara traditions. Event-specific administration and bathing schedules require authoritative contemporary sources.',
            'Dates are event- and location-specific; Tithika should not extrapolate a future Mela schedule from a generic festival rule.',
            ['Pilgrimage context','Sacred bathing context','Akhara tradition','Event-specific schedule slot'],
            ['festivals/pilgrim-places','panchang/daily','learn/tutorials'],
            'ritual-reference'
        ),
        'devotion/rituals/shraddha-karma'=>tithika_devotion_entry(
            'Shraddha Karma covers ancestral rites performed under family, regional and Shastra-based traditions.',
            'Procedure, eligible Tithi and performer rules vary significantly. Tithika keeps ritual explanation separate from its calculated Shraddha date engine.',
            'Pitru Paksha, Amavasya, Sankranti and other supported Shraddha classes are calculated on the dedicated date page.',
            ['Pitru Paksha context','Amavasya Shraddha','Tithi-based ancestral observance','Regional procedure note'],
            ['vrat/shraddha','vrat/amavasya','panchang/daily'],
            'ritual-reference'
        ),
        'devotion/rituals/vivah-sanskar'=>tithika_devotion_entry(
            'Vivah Sanskar is the Hindu marriage sacrament with substantial regional, Vedic-school and community variation.',
            'Ceremonial sequence should be sourced to the family or priestly tradition being followed; Tithika does not present one sequence as universal.',
            'Use the Vivah Muhurat engine for date/time selection and keep ritual procedure as a separate editorial layer.',
            ['Pre-wedding rites','Vivah fire ritual context','Saptapadi context','Regional custom notes'],
            ['muhurat/vivah','jyotish/horoscope-match','jyotish/marriage-analysis'],
            'ritual-reference'
        ),
        'devotion/rituals/upakarma'=>tithika_devotion_entry(
            'Upakarma is a Vedic study-renewal observance whose date and procedure vary by Veda, Shakha and regional tradition.',
            'A generic procedure is insufficient because mantras and sequence depend on the Vedic school.',
            'The annual date must be identified by the relevant Shakha and regional calendar rule rather than inferred from a universal civil date.',
            ['Rigveda tradition context','Yajurveda tradition context','Samaveda tradition context','Shakha-specific source slot'],
            ['panchang/daily','calendars/hindu','learn/panchang'],
            'ritual-reference'
        ),
        'devotion/rituals/namakarana'=>tithika_devotion_entry(
            'Namakarana is the traditional naming Samskara, with timing and procedure varying by family and regional custom.',
            'The ritual can involve Sankalpa, deity invocation, horoscope/name considerations and family-specific rites.',
            'Use a supported Samskara or Shubha-date timing profile rather than treating the ritual text itself as a timing rule.',
            ['Naming Samskara context','Sankalpa context','Nakshatra/name connection','Family tradition note'],
            ['jyotish/baby-name','jyotish/name-initials','muhurat/shubha-dates','panchang/sankalpa'],
            'ritual-reference'
        ),
    ];
}
