<?php
declare(strict_types=1);

/**
 * Quality taxonomy for the 99 routes completed in the final six-phase program.
 * "calculated" = primary output is a deterministic astronomical/Panchang calculation.
 * "aggregated" = dates are assembled from already-verified calculated selectors.
 * "hybrid" = calculated dates where selectors exist plus explicitly undated reference rows.
 * "reference" = structured knowledge/reference surface; never presented as an independent calculator.
 */
$calculated = [
    'panchang/gowri','panchang/published','panchang/manvadi-tithi','panchang/yugadi-tithi','panchang/kalpadi-tithi','panchang/kranti-samya',
    'muhurat/gowri','muhurat/jain-pachchakkhan','muhurat/do-ghati','muhurat/shubha-dates','muhurat/pancha-pakshi',
    'vrat/vinayaka-chaturthi','vrat/shraddha','vrat/kalashtami','vrat/chandra-darshan','vrat/ishti-anvadhan','vrat/iskcon-ekadashi',
    'vrat/masik-janmashtami','vrat/purushottam-maas','vrat/chaturmasa','vrat/ashoka-ashtami','vrat/asha-dashami','vrat/durva-ashtami',
    'vrat/jivit-putrika','vrat/shitala-saptami',
    'jyotish/prashna-kundali','jyotish/pancha-pakshi','jyotish/baby-name','jyotish/sahasra-chandrodaya','jyotish/vedic-time','jyotish/shraddha-tithi',
    'planets/parallel','planets/ecliptic-crossings','astronomy/indian-seasons',
];
$aggregated = [
    'calendars/hindu','calendars/indian','calendars/purnima',
    'festivals/hindu','festivals/tamil','festivals/malayalam',
    'festivals/chaitra','festivals/vaishakha','festivals/jyeshtha','festivals/ashadha','festivals/shravana','festivals/bhadrapada',
    'festivals/ashwina','festivals/kartika','festivals/margashirsha','festivals/pausha','festivals/magha','festivals/phalguna',
];
$hybrid = [
    'calendars/diwali','calendars/durga-puja','calendars/onam','calendars/mysore-dasara','calendars/saraswati-puja','calendars/chhath',
    'calendars/navratri','calendars/shardiya-navratri','calendars/chaitra-navratri','calendars/dashavatara','calendars/dasha-mahavidya',
    'calendars/dwadasha-siddhividya','calendars/gujarati-diwali','calendars/dashain','calendars/tihar',
];
$reference = [
    'panchang/utilities',
    'vrat/top-10','vrat/navagraha-weekdays','vrat/deity-weekdays','vrat/dashavatara','vrat/katha','vrat/katha/satyanarayana',
    'vrat/katha/ekadashi','vrat/katha/karwa-chauth','vrat/katha/ahoi-ashtami',
    'festivals/top-10','festivals/top-20','festivals/top-25','festivals/gurus-saints','festivals/dashavatara','festivals/navdurga',
    'festivals/puja-vidhi','festivals/deities','festivals/regional-deities','festivals/pilgrim-places','festivals/vishnu-avatars',
    'festivals/puja/ganesha','festivals/puja/lakshmi','festivals/puja/shivaratri','festivals/puja/holi',
    'jyotish/gemstone','jyotish/rudraksha','jyotish/name-initials','jyotish/prashnavali','jyotish/rashi-by-name',
    'planets/sidereal-zodiac','planets/tropical-zodiac',
];

$out = [];
foreach (['calculated'=>$calculated,'aggregated'=>$aggregated,'hybrid'=>$hybrid,'reference'=>$reference] as $quality=>$slugs) {
    foreach ($slugs as $slug) $out[$slug] = $quality;
}
return $out;
