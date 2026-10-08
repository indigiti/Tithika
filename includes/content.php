<?php
declare(strict_types=1);
require_once __DIR__ . '/devotion.php';

/**
 * Structured editorial content for Devotion, Gallery and Learn.
 *
 * Content is deliberately original and concise. It does not reproduce
 * copyrighted devotional editions or image collections. The purpose of this
 * layer is to make mapped routes useful, internally connected and ready for
 * later multilingual/editorial expansion.
 */

function tithika_learn_content(): array {
    return [
        'learn/tutorials' => [
            'intro' => 'Short guides for using Tithika calculations correctly: choose the right location, understand sunrise-based Hindu days, and distinguish astronomical events from observance rules.',
            'sections' => [
                ['title'=>'Start with local context','body'=>'Panchang and Muhurat values can change with latitude, longitude and timezone. Set the location first, then choose the civil date or birth date required by the tool.'],
                ['title'=>'Know what is calculated','body'=>'Tithika separates astronomy, Panchang state and religious observance rules. A Tithi transition is an astronomical result; an Ekadashi fasting date is a rule-based observance derived from that result.'],
                ['title'=>'Read evidence, not labels','body'=>'Calculation-backed pages expose Tithi, Nakshatra, Yoga, Karana, Dasha, transit or Muhurat evidence. Use those details when comparing traditions or validating a result.'],
            ],
            'links'=>['panchang/daily','muhurat/vivah','jyotish/janma-kundali'],
        ],
        'learn/panchang' => [
            'intro' => 'Panchang is a five-limb time framework built from Tithi, Vara, Nakshatra, Yoga and Karana. Tithika also presents sunrise, lunar month and supporting Muhurat periods around those five limbs.',
            'sections' => [
                ['title'=>'Tithi','body'=>'Tithi measures the angular separation of Moon and Sun in 12-degree steps. It can begin or end at any clock time, so the Tithi at local sunrise is important for many calendar rules.'],
                ['title'=>'Nakshatra','body'=>'Nakshatra divides the sidereal zodiac into 27 lunar mansions. The Moon’s sidereal longitude determines the active Nakshatra and Pada.'],
                ['title'=>'Yoga and Karana','body'=>'Yoga is based on the combined sidereal longitudes of Sun and Moon, while Karana is a half-Tithi division. Vishti Karana is also used for Bhadra calculations.'],
                ['title'=>'Sunrise-based day','body'=>'Many Hindu calendar decisions use the state at local sunrise rather than midnight. Tithika keeps civil dates visible while calculations explicitly expose the sunrise context.'],
            ],
            'links'=>['panchang/daily','panchang/month','panchang/nakshatra'],
        ],
        'learn/choghadiya' => [
            'intro' => 'Choghadiya divides day and night into eight unequal local periods based on sunrise and sunset. Each period receives a traditional quality such as Amrit, Shubh, Labh or Rog.',
            'sections' => [
                ['title'=>'Why location matters','body'=>'Because day and night lengths change by location and season, Choghadiya boundaries are calculated from local sunrise and sunset instead of fixed clock hours.'],
                ['title'=>'Day and night sequences','body'=>'The weekday determines the sequence used for daytime periods and the corresponding night sequence. Tithika calculates both and highlights the currently active period.'],
                ['title'=>'Use with other filters','body'=>'Choghadiya is one timing layer. Ceremony-specific Muhurat can also consider Tithi, Nakshatra, Bhadra, Rahu Kaal and other profile rules.'],
            ],
            'links'=>['muhurat/choghadiya','muhurat/rahu-kala','muhurat/abhijit'],
        ],
        'learn/muhurat' => [
            'intro' => 'Muhurat selection combines a suitable time window with the Panchang conditions required by a specific activity. There is no single universal “good time” that fits every ceremony.',
            'sections' => [
                ['title'=>'Common exclusions','body'=>'Tithika’s shared Muhurat substrate can subtract Rahu Kaal, Yamaganda, Gulika and Vishti/Bhadra before ceremony-specific rules are applied.'],
                ['title'=>'Ceremony profiles','body'=>'Vivah, Griha Pravesh, property, vehicle and Sanskar profiles use different weekday, Tithi and Nakshatra constraints. Some profiles also inspect Adhika month and Guru or Shukra combustion.'],
                ['title'=>'Evidence-first results','body'=>'Accepted windows expose the Panchang evidence used at that time. This makes the result auditable and easier to compare with a family or regional tradition.'],
            ],
            'links'=>['muhurat/vivah','muhurat/griha-pravesh','muhurat/vehicle'],
        ],
        'learn/nakshatra' => [
            'intro' => 'The 27 Nakshatras divide the sidereal zodiac into equal 13°20′ sectors. Each is further divided into four Padas of 3°20′.',
            'sections' => [
                ['title'=>'Janma Nakshatra','body'=>'The Moon’s sidereal longitude at birth determines Janma Nakshatra and Pada. It feeds several Jyotish and compatibility calculations.'],
                ['title'=>'Daily Nakshatra','body'=>'The Moon moves through roughly one Nakshatra per day, but transition times vary. Tithika resolves exact transitions rather than assuming a whole civil day.'],
                ['title'=>'Tarabalam','body'=>'Tarabalam compares Janma Nakshatra with the current Nakshatra through a repeating nine-Tara cycle. Tithika exposes the exact current relation and favourable positions.'],
            ],
            'links'=>['jyotish/birthstar','panchang/tarabalam','jyotish/nakshatra-compatibility'],
        ],
        'learn/rahu-kala' => [
            'intro' => 'Rahu Kaal is a daytime interval derived from local sunrise, sunset and weekday. It is commonly avoided for initiating important activities.',
            'sections' => [
                ['title'=>'How it is calculated','body'=>'The daylight span is divided into eight equal parts. The weekday selects which part is assigned to Rahu Kaal.'],
                ['title'=>'Not a fixed clock time','body'=>'Rahu Kaal changes with seasonal day length and location, so a fixed timetable can only be approximate. Tithika recalculates it for the selected location and date.'],
                ['title'=>'Muhurat integration','body'=>'The shared Muhurat engine removes Rahu Kaal before specialized ceremony filters are evaluated, keeping one consistent rule across supported profiles.'],
            ],
            'links'=>['panchang/rahu-kala','muhurat/rahu-kala','muhurat/vivah'],
        ],
        'learn/faq' => [
            'intro' => 'Answers to common questions about Tithika calculations, location handling and calendar conventions.',
            'sections' => [
                ['title'=>'Why can my date differ from another calendar?','body'=>'Different traditions can use different sunrise, lunar-month, regional or observance rules. Tithika exposes the engine profile and evidence so differences can be traced instead of hidden.'],
                ['title'=>'Which ayanamsha is used?','body'=>'The calculation stack uses Lahiri / Chitrapaksha sidereal positions unless a page explicitly states otherwise.'],
                ['title'=>'Does Tithika predict guaranteed events?','body'=>'No. Jyotish interpretation and timing pages describe astrological emphasis and evidence. They do not present event probabilities or guaranteed outcomes.'],
                ['title'=>'Is my location stored?','body'=>'The browser location is used to calculate local solar timing. The shared UI does not require an account to use location-aware calculations.'],
            ],
            'links'=>['panchang/daily','learn/panchang','learn/muhurat'],
        ],
        'learn/contact' => [
            'intro' => 'Use the project repository for calculation issues, reproducible discrepancies and implementation feedback. Include the page, date, location, timezone and expected result when reporting a calculation difference.',
            'sections' => [
                ['title'=>'Useful bug report','body'=>'Provide the exact route, date, city or coordinates, timezone, selected options and the value you expected. Screenshots help for visual issues but calculation evidence is more useful than appearance alone.'],
                ['title'=>'Tradition differences','body'=>'If a regional or Sampradaya rule differs from the implemented profile, identify the convention and a reliable rule reference so it can be versioned explicitly.'],
            ],
            'links'=>['learn/faq','learn/tutorials'],
        ],
        'learn/apps' => [
            'intro' => 'Tithika is designed as a responsive web application first. The same route and calculation architecture can later support installable mobile experiences without duplicating the astronomy engines.',
            'sections' => [
                ['title'=>'Current experience','body'=>'Responsive layouts, touch-friendly controls and shared location/date context are available directly in the browser.'],
                ['title'=>'Future packaging','body'=>'A native wrapper or installable PWA can reuse the same APIs after offline/cache behavior is defined for dynamic location-sensitive data.'],
            ],
            'links'=>['panchang/daily','muhurat/choghadiya','learn/faq'],
        ],
        'learn/wallpapers' => [
            'intro' => 'A lightweight visual collection surface for future Tithika wallpapers. The current release uses original generated collection cards and does not bundle third-party artwork.',
            'sections' => [
                ['title'=>'Asset policy','body'=>'Gallery and wallpaper surfaces are kept separate from calculation pages so large media does not block Panchang and Muhurat performance.'],
            ],
            'links'=>['gallery/hindu-symbols','gallery/rangoli','gallery/greetings'],
        ],
    ];
}

function tithika_gallery_items(string $slug, string $title): array {
    $sets = [
        'gallery/rangoli'=>['Lotus geometry','Eight-petal mandala','Diya border','Conch spiral','Temple threshold','Festival dots'],
        'gallery/greetings'=>['Diwali greeting','Navratri greeting','Janmashtami greeting','Ganesh Chaturthi greeting','Holi greeting','New year blessing'],
        'gallery/mehandi'=>['Mandala palm','Peacock motif','Lotus trail','Geometric wrist','Festive vine','Minimal finger pattern'],
        'gallery/hindu-festivals'=>['Diwali','Navratri','Janmashtami','Ganesha Chaturthi','Holi','Makar Sankranti'],
        'gallery/indian-festivals'=>['Onam','Durga Puja','Pongal','Bihu','Chhath','Raksha Bandhan'],
        'gallery/krishna-miniature'=>['Flute study','Govardhan theme','Yamuna scene','Vrindavan grove','Peacock motif','Lotus portrait'],
        'gallery/bal-krishna'=>['Makhan theme','Flute theme','Crawling Krishna','Yashoda theme','Lotus seat','Vrindavan child'],
        'gallery/bal-hanuman'=>['Sunward leap','Gada motif','Mountain theme','Ram bhakti','Temple child','Strength symbol'],
        'gallery/bal-ganesha'=>['Modak theme','Mouse companion','Lotus seat','Writing motif','Festival child','Blessing pose'],
        'gallery/hindu-symbols'=>['Om','Swastika','Kalasha','Lotus','Trishula','Shankha'],
        'gallery/oil-paintings'=>['Temple light','River ghat','Lotus study','Sacred mountain','Festival lamps','Monsoon shrine'],
        'learn/wallpapers'=>['Om gradient','Lotus dawn','Temple dusk','Moon calendar','Festival lamps','Sacred geometry'],
    ];
    return $sets[$slug] ?? [$title.' I',$title.' II',$title.' III',$title.' IV',$title.' V',$title.' VI'];
}

function tithika_devotion_subject(array $page): array {
    $registry = tithika_devotion_registry();
    $entry = $registry[$page['slug']] ?? null;

    if (!$entry) {
        return [
            'intro'=>$page['title'].' is part of Tithika’s devotional reference library.',
            'kind'=>'reference',
            'sections'=>[
                ['title'=>'Practice context','body'=>'This subject requires route-specific editorial review before sacred source text is published.'],
                ['title'=>'Calendar connection','body'=>'Use the related Panchang, festival or Muhurat tools for local date and timing context.'],
            ],
            'items'=>[],
            'source'=>[
                'editorial'=>'original-tithika',
                'sacred_text'=>'not-embedded',
                'policy'=>'No full sacred text is published without verified public-domain or licensed sourcing.',
            ],
            'links'=>['panchang/daily'],
        ];
    }

    return [
        'intro'=>$entry['summary'],
        'kind'=>$entry['kind'],
        'sections'=>[
            ['title'=>'Practice context','body'=>$entry['practice']],
            ['title'=>'Calendar connection','body'=>$entry['observance']],
        ],
        'items'=>$entry['items'],
        'source'=>$entry['source'],
        'links'=>$entry['links'],
    ];
}

function tithika_editorial_content(array $page): ?array {
    $group = $page['group'] ?? '';
    if ($group === 'learn') {
        $learn = tithika_learn_content();
        $entry = $learn[$page['slug']] ?? null;
        if (!$entry) return null;
        return ['type'=>'article'] + $entry;
    }

    if ($group === 'devotion') {
        return ['type'=>'article'] + tithika_devotion_subject($page);
    }

    if ($group === 'gallery' || $page['slug'] === 'learn/wallpapers') {
        return [
            'type'=>'gallery',
            'intro'=>$page['title'].' is presented as an original lightweight visual index. Full-resolution third-party artwork is intentionally not embedded in the calculation bundle.',
            'items'=>tithika_gallery_items($page['slug'], $page['title']),
            'links'=>['festivals/hindu','devotion/aarti','learn/tutorials'],
        ];
    }

    return null;
}

function tithika_has_editorial_content(array $page): bool {
    return tithika_editorial_content($page) !== null;
}

function tithika_render_editorial_content(array $page): void {
    $content = tithika_editorial_content($page);
    if (!$content) return;

    if ($content['type'] === 'gallery') {
        ?>
        <span class="tk-card-tag">Curated visual index</span>
        <h3><?= htmlspecialchars($page['title']) ?></h3>
        <p><?= htmlspecialchars($content['intro']) ?></p>
        <div class="tk-content-gallery">
          <?php foreach ($content['items'] as $i=>$item): ?>
            <figure class="tk-content-gallery-item" role="img" aria-label="<?= htmlspecialchars($item) ?>">
              <div class="tk-content-art art-<?= ($i % 6) + 1 ?>"><span><?= htmlspecialchars(mb_substr($item,0,1)) ?></span></div>
              <figcaption><?= htmlspecialchars($item) ?></figcaption>
            </figure>
          <?php endforeach; ?>
        </div>
        <?php
        return;
    }

    ?>
    <article class="tk-editorial">
      <header>
        <span class="tk-card-tag">Editorial reference</span>
        <p class="tk-editorial-lead"><?= htmlspecialchars($content['intro']) ?></p>
      </header>
      <?php foreach ($content['sections'] as $section): ?>
        <section>
          <h3><?= htmlspecialchars($section['title']) ?></h3>
          <p><?= htmlspecialchars($section['body']) ?></p>
        </section>
      <?php endforeach; ?>
      <?php if (($page['group'] ?? '') === 'devotion' && !empty($content['items'])): ?>
        <section>
          <h3>Corpus index</h3>
          <div class="tk-devotion-index">
            <?php foreach ($content['items'] as $item): ?>
              <span><?= htmlspecialchars((string)$item) ?></span>
            <?php endforeach; ?>
          </div>
        </section>
      <?php endif; ?>
      <?php if (($page['group'] ?? '') === 'devotion' && !empty($content['source'])): ?>
        <aside class="tk-devotion-source">
          <b>Source & edition policy</b>
          <span><?= htmlspecialchars((string)($content['source']['editorial'] ?? 'original-tithika')) ?> · <?= htmlspecialchars((string)($content['source']['sacred_text'] ?? 'not-embedded')) ?></span>
          <p><?= htmlspecialchars((string)($content['source']['policy'] ?? '')) ?></p>
        </aside>
      <?php endif; ?>
      <?php if (!empty($content['links'])): ?>
        <nav class="tk-editorial-links" aria-label="Related Tithika tools">
          <?php foreach ($content['links'] as $slug): $linked = tithika_find_page($slug); if (!$linked) continue; ?>
            <a href="<?= htmlspecialchars(tithika_pretty_url($slug)) ?>"><?= htmlspecialchars($linked['title']) ?> <span>→</span></a>
          <?php endforeach; ?>
        </nav>
      <?php endif; ?>
    </article>
    <?php
}
