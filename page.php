<?php
declare(strict_types=1);
require __DIR__ . '/includes/site.php';

$slug = trim((string)($_GET['slug'] ?? ''), '/');
$routes = tithika_routes();

if ($slug === '') {
    header('Location: ' . tithika_url());
    exit;
}

if (isset($routes[$slug])) {
    $group = $routes[$slug];
    tithika_render_header($group['title']);
    ?>
    <section class="tk-group-hero">
      <div class="tk-group-icon"><?= htmlspecialchars($group['icon']) ?></div>
      <h1><?= htmlspecialchars($group['title']) ?></h1>
      <p><?= htmlspecialchars($group['description']) ?></p>
    </section>
    <section class="tk-group-grid">
      <?php foreach ($group['pages'] as $item): ?>
        <a class="tk-tool-tile" href="<?= htmlspecialchars(tithika_pretty_url($item['slug'])) ?>">
          <span><?= htmlspecialchars(tithika_template_label($item['template'])) ?></span>
          <h2><?= htmlspecialchars($item['title']) ?></h2>
          <p><?= htmlspecialchars(tithika_template_copy($item['template'], $item['title'])) ?></p>
        </a>
      <?php endforeach; ?>
    </section>
    <?php
    tithika_render_footer();
    exit;
}

$page = tithika_find_page($slug);
if (!$page) {
    http_response_code(404);
    tithika_render_header('Page not found');
    ?>
    <section class="tk-group-hero">
      <div class="tk-group-icon">?</div>
      <h1>Page not found</h1>
      <p>This Tithika route is not in the current product map.</p>
    </section>
    <section class="tk-content"><a class="tk-primary" style="display:inline-grid;place-items:center;padding:0 18px" href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>">Open site map</a></section>
    <?php
    tithika_render_footer();
    exit;
}

if (!empty($page['live']) && $page['live'] === 'choghadiya.php') {
    header('Location: ' . tithika_url('choghadiya.php'), true, 302);
    exit;
}

$group = $routes[$page['group']];
$related = tithika_related($page);
$isComputed = in_array($page['slug'], ['panchang/month','panchang/daily','panchang/moonrise-moonset','panchang/rahu-kala','muhurat/rahu-kala','muhurat/abhijit','muhurat/lagna','panchang/lagna-kundali','vrat/ekadashi','vrat/purnima','vrat/amavasya','vrat/pradosham','vrat/sankashti-chaturthi','vrat/masik-shivaratri','festivals/maha-shivaratri','festivals/diwali','festivals/karwa-chauth','festivals/janmashtami','festivals/rama-navami','festivals/hanuman-jayanti','festivals/akshaya-tritiya','festivals/vat-savitri','festivals/durga-puja','festivals/holi','festivals/dussehra','festivals/navratri','festivals/raksha-bandhan','festivals/ganesha-chaturthi','vrat/mahadwadashi','vrat/dwadashi','vrat/sankranti','calendars/sankranti','festivals/sankranti','festivals/makar-sankranti','astronomy/vernal-equinox','astronomy/summer-solstice','astronomy/autumnal-equinox','astronomy/winter-solstice','planets/positions','planets/transit','planets/combustion','planets/retrograde','jyotish/birthstar','jyotish/janma-lagna','jyotish/moonsign','jyotish/sunsign','jyotish/janma-kundali','jyotish/horoscope-analysis','jyotish/interpretation-report','jyotish/timing-timeline','jyotish/rashifal','jyotish/rashifal/daily','jyotish/rashifal/weekly','jyotish/rashifal/monthly','jyotish/rashifal/yearly','planets/mutual-aspects','planets/lunar-aspects','planets/conjunctions','planets/graha-yuddha','astronomy/eclipses','astronomy/solar-eclipse','astronomy/lunar-eclipse','jyotish/vimshottari-dasha','jyotish/mangal-dosha','jyotish/kalasarpa','jyotish/shani-sadesati','jyotish/ashtakavarga','jyotish/shadbala','jyotish/horoscope-match','jyotish/marriage-analysis','jyotish/nakshatra-compatibility','jyotish/divisional-charts','jyotish/yogas'], true);
tithika_render_header($page['title'], $page);
echo '<script>window.TITHIKA_PAGE_SLUG=' . json_encode($page['slug'], JSON_UNESCAPED_SLASHES) . ';</script>';
?>
<section class="tk-page-hero">
  <div class="tk-hero-inner">
    <div>
      <div class="tk-breadcrumbs">
        <a href="<?= htmlspecialchars(tithika_url()) ?>">Home</a><span>›</span>
        <a href="<?= htmlspecialchars(tithika_pretty_url($page['group'])) ?>"><?= htmlspecialchars($group['title']) ?></a><span>›</span>
        <span><?= htmlspecialchars($page['title']) ?></span>
      </div>
      <span class="tk-kicker"><?= htmlspecialchars($group['icon']) ?> <?= htmlspecialchars(tithika_template_label($page['template'])) ?></span>
      <h1><?= htmlspecialchars($page['title']) ?></h1>
      <p><?= htmlspecialchars(tithika_template_copy($page['template'], $page['title'])) ?></p>
    </div>
    <aside class="tk-context-card">
      <header><span>Local context</span><span class="tk-live-dot">● Live solar data</span></header>
      <div class="tk-context-date" id="tkContextDate">Loading today…</div>
      <div class="tk-context-location" id="tkContextLocation">Finding your location…</div>
      <div class="tk-context-grid">
        <div class="tk-stat"><small>Sunrise</small><strong id="tkSunrise">--</strong></div>
        <div class="tk-stat"><small>Sunset</small><strong id="tkSunset">--</strong></div>
        <div class="tk-stat"><small>Current</small><strong id="tkCurrent">--</strong></div>
        <div class="tk-stat"><small>Rahu Kaal</small><strong id="tkRahu">--</strong></div>
      </div>
      <div class="tk-context-location" id="tkCurrentRange">Local solar engine ready</div>
      <div class="tk-progress"><i id="tkContextProgress"></i></div>
    </aside>
  </div>
</section>

<div class="tk-toolbar-wrap">
  <div class="tk-toolbar">
    <button type="button" data-shift-date="-1" aria-label="Previous day">‹</button>
    <input id="tkDate" class="tk-date" type="date">
    <button id="tkToday" type="button">Today</button>
    <button type="button" data-shift-date="1" aria-label="Next day">›</button>
    <span class="tk-spacer"></span>
    <a href="<?= htmlspecialchars(tithika_pretty_url($page['group'])) ?>">All <?= htmlspecialchars($group['title']) ?></a>
    <span class="tk-engine-state<?= $isComputed ? ' is-live' : '' ?>"><?= in_array($page['slug'], ['panchang/daily','panchang/month'], true) ? 'Panchang engine live' : ($isComputed ? 'Solar calculation live' : 'Page shell mapped') ?></span>
  </div>
</div>

<section class="tk-content">
  <div class="tk-section-head">
    <div>
      <span>Tithika <?= htmlspecialchars(tithika_template_label($page['template'])) ?></span>
      <h2><?= htmlspecialchars($page['title']) ?></h2>
      <p>The visual system and URL are production-mapped. Specialized astronomical/Panchang outputs are only shown after their calculation module is verified.</p>
    </div>
  </div>

  <div class="tk-grid">
    <div class="tk-card span-8">
      <?php if ($page['slug'] === 'panchang/month'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Live month engine</span>
            <h3 id="tkMonthTitle">Month Panchang</h3>
            <p>Each civil date shows the Panchang state at local sunrise. Select any day to move the shared Tithika date context.</p>
          </div>
          <div class="tk-panchang-engine" id="tkMonthEngine">Astronomy Engine · Lahiri</div>
        </div>
        <div id="tkMonthLoading" class="tk-panchang-loading">Building month Panchang…</div>
        <div class="tk-month-weekdays" aria-hidden="true">
          <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
        </div>
        <div id="tkMonthGrid" class="tk-month-grid" aria-live="polite"></div>
        <div class="tk-month-legend">
          <span><i class="ekadashi"></i>Ekadashi</span>
          <span><i class="purnima"></i>Purnima</span>
          <span><i class="amavasya"></i>Amavasya</span>
        </div>
        <div class="tk-month-actions">
          <span id="tkMonthSelection">Select a day for details</span>
          <a id="tkMonthDailyLink" href="<?= htmlspecialchars(tithika_pretty_url('panchang/daily')) ?>">Open selected day in Daily Panchang →</a>
        </div>
      <?php elseif ($page['slug'] === 'panchang/daily'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Verified astronomy</span>
            <h3>Daily Panchang at sunrise</h3>
            <p>Sidereal Sun and Moon positions use Lahiri ayanamsha. Each row shows the state at local sunrise and its next transition.</p>
          </div>
          <div class="tk-panchang-engine" id="tkEngineMeta">Astronomy Engine · Lahiri</div>
        </div>

        <div id="tkPanchangLoading" class="tk-panchang-loading">Calculating sidereal Panchang…</div>

        <div class="tk-panchang-summary">
          <div class="tk-panchang-metric"><small>Tithi</small><strong id="tkTithiName">—</strong><span id="tkTithiMeta">—</span></div>
          <div class="tk-panchang-metric"><small>Nakshatra</small><strong id="tkNakshatraName">—</strong><span>Moon's sidereal mansion</span></div>
          <div class="tk-panchang-metric"><small>Yoga</small><strong id="tkYogaName">—</strong><span>Sun + Moon longitude</span></div>
          <div class="tk-panchang-metric"><small>Karana</small><strong id="tkKaranaName">—</strong><span>Half-Tithi division</span></div>
          <div class="tk-panchang-metric"><small>Paksha</small><strong id="tkPakshaName">—</strong><span>Waxing / waning half</span></div>
          <div class="tk-panchang-metric"><small>Moon Rashi</small><strong id="tkMoonRashi">—</strong><span>Sidereal Moon sign</span></div>
          <div class="tk-panchang-metric"><small>Sun Rashi</small><strong id="tkSunRashi">—</strong><span>Sidereal Sun sign</span></div>
          <div class="tk-panchang-metric"><small>Amanta Month</small><strong id="tkAmantaMonth">—</strong><span>Lunar month</span></div>
          <div class="tk-panchang-metric"><small>Purnimanta Month</small><strong id="tkPurnimantaMonth">—</strong><span>Lunar month</span></div>
          <div class="tk-panchang-metric"><small>Moonrise</small><strong id="tkMoonrise">—</strong><span>Within Hindu day</span></div>
          <div class="tk-panchang-metric"><small>Moonset</small><strong id="tkMoonset">—</strong><span>Within Hindu day</span></div>
        </div>

        <div class="tk-panchang-columns">
          <section class="tk-panchang-block"><header><span>◐</span><div><small>Lunar day</small><h4>Tithi</h4></div></header><div id="tkTithiTransitions"></div></section>
          <section class="tk-panchang-block"><header><span>✦</span><div><small>Lunar mansion</small><h4>Nakshatra</h4></div></header><div id="tkNakshatraTransitions"></div></section>
          <section class="tk-panchang-block"><header><span>◎</span><div><small>Combined longitude</small><h4>Yoga</h4></div></header><div id="tkYogaTransitions"></div></section>
          <section class="tk-panchang-block"><header><span>◇</span><div><small>Half lunar day</small><h4>Karana</h4></div></header><div id="tkKaranaTransitions"></div></section>
        </div>

        <div class="tk-panchang-subhead">
          <div><small>Daily Muhurat</small><h3>Auspicious & caution windows</h3></div>
          <span>Sunrise-derived</span>
        </div>
        <div class="tk-muhurat-grid">
          <div class="tk-muhurat-item good"><small>Abhijit</small><strong id="tkMuhuratAbhijit">—</strong></div>
          <div class="tk-muhurat-item good"><small>Vijaya</small><strong id="tkMuhuratVijaya">—</strong></div>
          <div class="tk-muhurat-item good"><small>Brahma</small><strong id="tkMuhuratBrahma">—</strong></div>
          <div class="tk-muhurat-item good"><small>Godhuli</small><strong id="tkMuhuratGodhuli">—</strong></div>
          <div class="tk-muhurat-item"><small>Pratah Sandhya</small><strong id="tkMuhuratPratah">—</strong></div>
          <div class="tk-muhurat-item"><small>Sayahna Sandhya</small><strong id="tkMuhuratSayahna">—</strong></div>
          <div class="tk-muhurat-item"><small>Nishita</small><strong id="tkMuhuratNishita">—</strong></div>
          <div class="tk-muhurat-item avoid"><small>Yamaganda</small><strong id="tkMuhuratYamaganda">—</strong></div>
          <div class="tk-muhurat-item avoid"><small>Gulika</small><strong id="tkMuhuratGulika">—</strong></div>
        </div>
      <?php elseif (in_array($page['slug'], ['planets/mutual-aspects','planets/lunar-aspects','planets/conjunctions','planets/graha-yuddha'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Planetary relationship engine</span>
            <h3 id="tkAspectTitle"><?= htmlspecialchars($page['title']) ?></h3>
            <p>Exact sidereal longitude relationships are scan-bracketed and refined. Graha Yuddha uses the classical same-Rashi one-degree rule.</p>
          </div>
          <div class="tk-panchang-engine">Lahiri · geocentric longitude</div>
        </div>
        <div id="tkAspectLoading" class="tk-panchang-loading">Calculating planetary relationships…</div>
        <div id="tkAspectNote" class="tk-lunar-note"></div>
        <div id="tkAspectResult" class="tk-planetary-result"></div>
      <?php elseif (in_array($page['slug'], ['astronomy/eclipses','astronomy/solar-eclipse','astronomy/lunar-eclipse'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Physical eclipse engine</span>
            <h3 id="tkEclipseTitle"><?= htmlspecialchars($page['title']) ?></h3>
            <p>Global eclipse geometry comes from the Astronomy Engine; selected-location solar contacts and lunar altitude determine local visibility.</p>
          </div>
          <div class="tk-panchang-engine">Shadow geometry · local horizon</div>
        </div>
        <div id="tkEclipseLoading" class="tk-panchang-loading">Calculating eclipse events…</div>
        <div id="tkEclipseNote" class="tk-lunar-note"></div>
        <div id="tkEclipseResult" class="tk-eclipse-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/vimshottari-dasha'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Vimshottari · 120 year cycle</span>
            <h3>Vimshottari Dasha</h3>
            <p>Birth Moon Nakshatra selects the starting Mahadasha; the remaining Nakshatra fraction determines the birth balance.</p>
          </div>
          <div class="tk-panchang-engine">Lahiri · 365.25 day Dasha year</div>
        </div>
        <div class="tk-birth-controls">
          <label><span>Birth time</span><input id="tkDashaTime" type="time" step="1" value="12:00:00"></label>
          <button id="tkDashaCalculate" type="button">Calculate Dasha</button>
        </div>
        <div id="tkDashaLoading" class="tk-panchang-loading">Calculating Vimshottari periods…</div>
        <div id="tkDashaResult" class="tk-dasha-result"></div>
      <?php elseif (in_array($page['slug'], ['jyotish/mangal-dosha','jyotish/kalasarpa','jyotish/shani-sadesati'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Natal / transit rule engine</span>
            <h3 id="tkDoshaTitle"><?= htmlspecialchars($page['title']) ?></h3>
            <p>Rules are evaluated from the same Lahiri Janma chart used by Tithika Kundali; Sade Sati uses actual Saturn Rashi ingress and re-entry.</p>
          </div>
          <div class="tk-panchang-engine">Lahiri · mean nodes default</div>
        </div>
        <div class="tk-birth-controls">
          <label><span>Birth time</span><input id="tkDoshaTime" type="time" step="1" value="12:00:00"></label>
          <?php if ($page['slug'] === 'jyotish/kalasarpa'): ?>
          <label><span>Rahu / Ketu</span><select id="tkDoshaNode"><option value="mean">Mean nodes</option><option value="true">True nodes</option></select></label>
          <?php endif; ?>
          <button id="tkDoshaCalculate" type="button">Calculate</button>
        </div>
        <div id="tkDoshaLoading" class="tk-panchang-loading">Evaluating chart…</div>
        <div id="tkDoshaResult" class="tk-dosha-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/ashtakavarga'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Classical bindu strength map</span>
            <h3>Ashtakavarga</h3>
            <p>Seven Bhinnashtakavarga tables are built from Sun through Saturn plus Lagna contributor positions, then summed into Sarvashtakavarga.</p>
          </div>
          <div class="tk-panchang-engine">Parashari raw BAV · SAV</div>
        </div>
        <div class="tk-birth-controls">
          <label><span>Birth time</span><input id="tkAshtaTime" type="time" step="1" value="12:00:00"></label>
          <button id="tkAshtaCalculate" type="button">Calculate Ashtakavarga</button>
        </div>
        <div id="tkAshtaLoading" class="tk-panchang-loading">Building Ashtakavarga matrix…</div>
        <div id="tkAshtaResult" class="tk-ashta-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/divisional-charts'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">BPHS Shodashavarga · D1–D60</span>
            <h3>Divisional Charts</h3>
            <p>Sixteen classical Vargas are derived from the same Lahiri Graha longitudes and exact birth Lagna. D2 and D10 use the Parashara construction; high-Varga cusp sensitivity is exposed.</p>
          </div>
          <div class="tk-panchang-engine">D1 · D2 · D3 · D4 · D7 · D9 · D10 · D12 · D16 · D20 · D24 · D27 · D30 · D40 · D45 · D60</div>
        </div>
        <div class="tk-birth-controls">
          <label><span>Birth time</span><input id="tkVargaTime" type="time" step="1" value="12:00:00"></label>
          <label><span>Divisional chart</span><select id="tkVargaSelect">
            <option value="1">D1 · Rashi</option><option value="2">D2 · Hora</option><option value="3">D3 · Drekkana</option><option value="4">D4 · Chaturthamsha</option>
            <option value="7">D7 · Saptamsha</option><option value="9" selected>D9 · Navamsha</option><option value="10">D10 · Dashamsha</option><option value="12">D12 · Dvadashamsha</option>
            <option value="16">D16 · Shodashamsha</option><option value="20">D20 · Vimshamsha</option><option value="24">D24 · Siddhamsha</option><option value="27">D27 · Bhamsha</option>
            <option value="30">D30 · Trimshamsha</option><option value="40">D40 · Khavedamsha</option><option value="45">D45 · Akshavedamsha</option><option value="60">D60 · Shashtyamsha</option>
          </select></label>
          <button id="tkVargaCalculate" type="button">Build chart</button>
        </div>
        <div id="tkVargaLoading" class="tk-panchang-loading">Calculating divisional chart…</div>
        <div id="tkVargaResult" class="tk-varga-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/yogas'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Structural Yoga detector</span>
            <h3>Jyotish Yoga Analysis</h3>
            <p>Detects a curated set of classical D1 combinations from exact Graha geometry, lordship and Graha Drishti, with cancellation or weakening evidence where implemented.</p>
          </div>
          <div class="tk-panchang-engine">Evidence-first · no predictive score</div>
        </div>
        <div class="tk-birth-controls">
          <label><span>Birth time</span><input id="tkYogaTime" type="time" step="1" value="12:00:00"></label>
          <button id="tkYogaCalculate" type="button">Detect Yogas</button>
        </div>
        <div id="tkYogaLoading" class="tk-panchang-loading">Detecting structural Yogas…</div>
        <div id="tkYogaResult" class="tk-yoga-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/shadbala'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Complete six-fold strength profile</span>
            <h3>Shadbala Planetary Strength</h3>
            <p>Sthana, Dig, Kala, Cheshta, Naisargika and Drik Bala are calculated in virupas with every component and method convention exposed.</p>
          </div>
          <div class="tk-panchang-engine">60 virupas = 1 Rupa · Lahiri</div>
        </div>
        <div class="tk-birth-controls">
          <label><span>Birth time</span><input id="tkShadbalaTime" type="time" step="1" value="12:00:00"></label>
          <button id="tkShadbalaCalculate" type="button">Calculate Shadbala</button>
        </div>
        <div id="tkShadbalaLoading" class="tk-panchang-loading">Calculating six-fold planetary strength…</div>
        <div id="tkShadbalaResult" class="tk-shadbala-result"></div>
      <?php elseif (in_array($page['slug'], ['jyotish/rashifal','jyotish/rashifal/daily','jyotish/rashifal/weekly','jyotish/rashifal/monthly','jyotish/rashifal/yearly'], true)): ?>
        <?php
          $rfModes = [
            'jyotish/rashifal' => 'overview',
            'jyotish/rashifal/daily' => 'daily',
            'jyotish/rashifal/weekly' => 'weekly',
            'jyotish/rashifal/monthly' => 'monthly',
            'jyotish/rashifal/yearly' => 'yearly',
          ];
          $rfMode = $rfModes[$page['slug']] ?? 'overview';
        ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Personalized birth-chart Rashifal</span>
            <h3><?= htmlspecialchars($page['title']) ?></h3>
            <p>Uses your Janma chart, functional lordship, Vimshottari activation and horizon-appropriate transits. Scores describe relative emphasis, not guaranteed events.</p>
          </div>
          <div class="tk-panchang-engine">Lahiri · Dasha + transit evidence · auditable scoring</div>
        </div>
        <nav class="tk-rashifal-tabs" aria-label="Rashifal period">
          <a class="<?= $rfMode === 'overview' ? 'active' : '' ?>" href="<?= htmlspecialchars(tithika_pretty_url('jyotish/rashifal')) ?>">Overview</a>
          <a class="<?= $rfMode === 'daily' ? 'active' : '' ?>" href="<?= htmlspecialchars(tithika_pretty_url('jyotish/rashifal/daily')) ?>">Daily</a>
          <a class="<?= $rfMode === 'weekly' ? 'active' : '' ?>" href="<?= htmlspecialchars(tithika_pretty_url('jyotish/rashifal/weekly')) ?>">Weekly</a>
          <a class="<?= $rfMode === 'monthly' ? 'active' : '' ?>" href="<?= htmlspecialchars(tithika_pretty_url('jyotish/rashifal/monthly')) ?>">Monthly</a>
          <a class="<?= $rfMode === 'yearly' ? 'active' : '' ?>" href="<?= htmlspecialchars(tithika_pretty_url('jyotish/rashifal/yearly')) ?>">Yearly</a>
        </nav>
        <div class="tk-birth-controls tk-rashifal-controls">
          <label><span>Birth date</span><input id="tkRashifalBirthDate" type="date"></label>
          <label><span>Birth time</span><input id="tkRashifalBirthTime" type="time" step="1" value="12:00:00"></label>
          <label><span>Forecast date</span><input id="tkRashifalTargetDate" type="date"></label>
          <label><span>Rahu / Ketu</span><select id="tkRashifalNode"><option value="mean">Mean nodes</option><option value="true">True nodes</option></select></label>
          <button id="tkRashifalCalculate" type="button">Build Rashifal</button>
        </div>
        <input id="tkRashifalMode" type="hidden" value="<?= htmlspecialchars($rfMode) ?>">
        <div id="tkRashifalLoading" class="tk-panchang-loading">Building personalized Rashifal…</div>
        <div id="tkRashifalResult" class="tk-rashifal-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/timing-timeline'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Dasha + slow-transit activation timeline</span>
            <h3>Jyotish Timing Timeline</h3>
            <p>Month-by-month emphasis from structural natal evidence, Vimshottari Mahadasha/Antardasha/Pratyantardasha and Jupiter, Saturn, Rahu and Ketu transit houses.</p>
          </div>
          <div class="tk-panchang-engine">Transparent activation index · exact Dasha & ingress markers</div>
        </div>
        <div class="tk-birth-controls tk-timeline-controls">
          <label><span>Birth time</span><input id="tkTimelineBirthTime" type="time" step="1" value="12:00:00"></label>
          <label><span>Start month</span><input id="tkTimelineStart" type="month"></label>
          <label><span>Horizon</span><select id="tkTimelineMonths">
            <option value="6">6 months</option>
            <option value="12" selected>12 months</option>
            <option value="18">18 months</option>
            <option value="24">24 months</option>
            <option value="36">36 months</option>
          </select></label>
          <label><span>Rahu / Ketu</span><select id="tkTimelineNode"><option value="mean">Mean nodes</option><option value="true">True nodes</option></select></label>
          <button id="tkTimelineCalculate" type="button">Build Timeline</button>
        </div>
        <div id="tkTimelineLoading" class="tk-panchang-loading">Building Dasha and transit activation timeline…</div>
        <div id="tkTimelineResult" class="tk-timeline-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/interpretation-report'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Rule-based interpretation layer</span>
            <h3>Jyotish Interpretation Report</h3>
            <p>Explains functional lordship, D1/D9/D10 dignity confirmation, Shadbala capacity, SAV house support and current Dasha/transit activation with evidence attached to every reading.</p>
          </div>
          <div class="tk-panchang-engine">Whole-sign lordship · auditable rules · no deterministic prediction</div>
        </div>
        <div class="tk-birth-controls">
          <label><span>Birth time</span><input id="tkInterpretTime" type="time" step="1" value="12:00:00"></label>
          <label><span>Rahu / Ketu</span><select id="tkInterpretNode"><option value="mean">Mean nodes</option><option value="true">True nodes</option></select></label>
          <button id="tkInterpretCalculate" type="button">Build Interpretation</button>
        </div>
        <div id="tkInterpretLoading" class="tk-panchang-loading">Building evidence-backed interpretation…</div>
        <div id="tkInterpretResult" class="tk-interpret-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/horoscope-analysis'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Unified Jyotish synthesis</span>
            <h3>Unified Horoscope Analysis</h3>
            <p>One evidence-first report combining D1, D9, D10, Shadbala, Sarvashtakavarga, structural Yogas, Vimshottari timing and major transit-house context.</p>
          </div>
          <div class="tk-panchang-engine">Lahiri · auditable evidence · no deterministic claims</div>
        </div>
        <div class="tk-birth-controls">
          <label><span>Birth time</span><input id="tkAnalysisTime" type="time" step="1" value="12:00:00"></label>
          <label><span>Rahu / Ketu</span><select id="tkAnalysisNode"><option value="mean">Mean nodes</option><option value="true">True nodes</option></select></label>
          <button id="tkAnalysisCalculate" type="button">Build Full Analysis</button>
        </div>
        <div id="tkAnalysisLoading" class="tk-panchang-loading">Building unified Jyotish evidence report…</div>
        <div id="tkAnalysisResult" class="tk-analysis-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/janma-kundali'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Janma Kundali · D1 + D9</span>
            <h3>Janma Kundali</h3>
            <p>Whole-sign D1 houses from the birth Lagna, D9 Navamsha, Graha positions, birth Panchang, aspects and Graha Yuddha.</p>
          </div>
          <div class="tk-panchang-engine">Lahiri · Mean / True Rahu-Ketu</div>
        </div>
        <div class="tk-birth-controls">
          <label><span>Birth time</span><input id="tkKundaliTime" type="time" step="1" value="12:00:00"></label>
          <label><span>Rahu / Ketu</span><select id="tkKundaliNode"><option value="mean">Mean nodes</option><option value="true">True nodes</option></select></label>
          <button id="tkKundaliCalculate" type="button">Build Kundali</button>
        </div>
        <div id="tkKundaliLoading" class="tk-panchang-loading">Calculating Janma Kundali…</div>
        <div id="tkKundaliResult" class="tk-kundali-result"></div>
      <?php elseif (in_array($page['slug'], ['planets/positions','planets/transit','planets/combustion','planets/retrograde'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Sidereal planetary engine</span>
            <h3 id="tkPlanetaryTitle"><?= htmlspecialchars($page['title']) ?></h3>
            <p>Apparent geocentric true-ecliptic positions are converted to Lahiri Nirayana longitude with Rashi, Nakshatra, motion and event state.</p>
          </div>
          <div class="tk-panchang-engine">Astronomy Engine · Lahiri · mean nodes</div>
        </div>
        <?php if ($page['slug'] === 'planets/positions'): ?>
        <div class="tk-birth-controls">
          <label><span>Local chart time</span><input id="tkPlanetTime" type="time" step="1" value="12:00:00"></label>
          <label><span>Rahu / Ketu</span><select id="tkNodeModel"><option value="mean">Mean nodes</option><option value="true">True nodes</option></select></label>
          <button id="tkPlanetCalculate" type="button">Update positions</button>
        </div>
        <?php endif; ?>
        <div id="tkPlanetaryLoading" class="tk-panchang-loading">Calculating planetary ephemeris…</div>
        <div id="tkPlanetaryNote" class="tk-lunar-note"></div>
        <div id="tkPlanetaryResult" class="tk-planetary-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/marriage-analysis'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">D1 + D9 + Dasha evidence</span>
            <h3>Deep Marriage Analysis</h3>
            <p>This layer does not add another compatibility score. It compares the seventh house/lord, Navamsha, Venus/Jupiter structure, conservative Mangal cancellation evidence and overlapping Vimshottari periods.</p>
          </div>
          <div class="tk-panchang-engine">Lahiri · whole-sign D1 · D9 Navamsha</div>
        </div>
        <div class="tk-match-profiles">
          <?php foreach (['groom'=>'Vara / Groom','bride'=>'Kanya / Bride'] as $role=>$label): ?>
          <section class="tk-match-person" data-match-role="<?= $role ?>">
            <header><span><?= $role === 'groom' ? '01' : '02' ?></span><div><small>Birth profile</small><h4><?= htmlspecialchars($label) ?></h4></div></header>
            <div class="tk-match-fields">
              <label><span>Name</span><input id="tkMatch<?= ucfirst($role) ?>Name" type="text" placeholder="<?= $role === 'groom' ? 'Groom name' : 'Bride name' ?>"></label>
              <label><span>Birth date</span><input id="tkMatch<?= ucfirst($role) ?>Date" type="date"></label>
              <label><span>Birth time</span><input id="tkMatch<?= ucfirst($role) ?>Time" type="time" step="1" value="12:00:00"></label>
              <label class="wide"><span>Birth city</span><input id="tkMatch<?= ucfirst($role) ?>City" type="search" autocomplete="off" placeholder="Search city"></label>
              <div id="tkMatch<?= ucfirst($role) ?>Results" class="tk-match-search wide"></div>
            </div>
            <button type="button" class="tk-match-use-current" data-match-use-current="<?= $role ?>">Use selected Tithika location</button>
            <small id="tkMatch<?= ucfirst($role) ?>Meta" class="tk-match-meta">Choose the correct birth city for timezone and coordinates.</small>
          </section>
          <?php endforeach; ?>
        </div>
        <div class="tk-birth-controls">
          <label><span>Dasha overlap horizon</span><select id="tkMarriageHorizon"><option value="8">8 years</option><option value="12" selected>12 years</option><option value="18">18 years</option><option value="24">24 years</option></select></label>
        </div>
        <button id="tkMarriageCalculate" class="tk-match-submit" type="button">Build Deep Analysis</button>
        <div id="tkMarriageLoading" class="tk-panchang-loading" hidden>Comparing D1, D9, Mangal and Dasha periods…</div>
        <div id="tkMarriageResult" class="tk-marriage-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/horoscope-match'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Ashtakoota · 36 Guna</span>
            <h3>Horoscope Matching</h3>
            <p>Vara and Kanya use independent birth date, time, place and timezone. The Moon-based 36-point score is kept separate from Mangal, Lagna and Vimshottari context.</p>
          </div>
          <div class="tk-panchang-engine">Lahiri · Ashtakoota + Kundali context</div>
        </div>
        <div class="tk-match-profiles">
          <?php foreach (['groom'=>'Vara / Groom','bride'=>'Kanya / Bride'] as $role=>$label): ?>
          <section class="tk-match-person" data-match-role="<?= $role ?>">
            <header><span><?= $role === 'groom' ? '01' : '02' ?></span><div><small>Birth profile</small><h4><?= htmlspecialchars($label) ?></h4></div></header>
            <div class="tk-match-fields">
              <label><span>Name</span><input id="tkMatch<?= ucfirst($role) ?>Name" type="text" placeholder="<?= $role === 'groom' ? 'Groom name' : 'Bride name' ?>"></label>
              <label><span>Birth date</span><input id="tkMatch<?= ucfirst($role) ?>Date" type="date"></label>
              <label><span>Birth time</span><input id="tkMatch<?= ucfirst($role) ?>Time" type="time" step="1" value="12:00:00"></label>
              <label class="wide"><span>Birth city</span><input id="tkMatch<?= ucfirst($role) ?>City" type="search" autocomplete="off" placeholder="Search city"></label>
              <div id="tkMatch<?= ucfirst($role) ?>Results" class="tk-match-search wide"></div>
            </div>
            <button type="button" class="tk-match-use-current" data-match-use-current="<?= $role ?>">Use selected Tithika location</button>
            <small id="tkMatch<?= ucfirst($role) ?>Meta" class="tk-match-meta">Choose the correct birth city for timezone and coordinates.</small>
          </section>
          <?php endforeach; ?>
        </div>
        <button id="tkMatchCalculate" class="tk-match-submit" type="button">Match Horoscopes</button>
        <div id="tkMatchLoading" class="tk-panchang-loading" hidden>Calculating both birth charts and Ashtakoota…</div>
        <div id="tkMatchResult" class="tk-match-result"></div>
      <?php elseif ($page['slug'] === 'jyotish/nakshatra-compatibility'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Nakshatra + Pada matching</span>
            <h3>Nakshatra Compatibility</h3>
            <p>A lightweight Ashtakoota view for known birth stars. Pada is required because some Nakshatras cross Rashi boundaries.</p>
          </div>
          <div class="tk-panchang-engine">Same 36-point scoring tables</div>
        </div>
        <div class="tk-nak-match-grid">
          <?php foreach (['groom'=>'Vara / Groom','bride'=>'Kanya / Bride'] as $role=>$label): ?>
          <section>
            <small><?= htmlspecialchars($label) ?></small>
            <label><span>Nakshatra</span><select id="tkNak<?= ucfirst($role) ?>"></select></label>
            <label><span>Pada</span><select id="tkNak<?= ucfirst($role) ?>Pada"><option>1</option><option>2</option><option>3</option><option>4</option></select></label>
          </section>
          <?php endforeach; ?>
        </div>
        <button id="tkNakMatchCalculate" class="tk-match-submit" type="button">Check Compatibility</button>
        <div id="tkNakMatchLoading" class="tk-panchang-loading" hidden>Calculating Nakshatra compatibility…</div>
        <div id="tkNakMatchResult" class="tk-match-result"></div>
      <?php elseif (in_array($page['slug'], ['jyotish/birthstar','jyotish/janma-lagna','jyotish/moonsign','jyotish/sunsign'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Birth calculator · Lahiri</span>
            <h3 id="tkJyotishTitle"><?= htmlspecialchars($page['title']) ?></h3>
            <p>Choose the birth date in the toolbar, enter the exact local birth time, and use the selected location for Janma Nakshatra, Rashi or Lagna.</p>
          </div>
          <div class="tk-panchang-engine">Moon + Sun + Ascendant</div>
        </div>
        <div class="tk-birth-controls">
          <label><span>Birth time</span><input id="tkBirthTime" type="time" step="1" value="12:00:00"></label>
          <button id="tkBirthCalculate" type="button">Calculate birth chart</button>
        </div>
        <div id="tkJyotishLoading" class="tk-panchang-loading">Calculating birth factors…</div>
        <div id="tkJyotishResult" class="tk-jyotish-result"></div>
      <?php elseif (in_array($page['slug'], ['festivals/ganesha-chaturthi','festivals/raksha-bandhan','festivals/navratri','festivals/dussehra','festivals/holi','festivals/karwa-chauth','festivals/janmashtami','festivals/rama-navami','festivals/hanuman-jayanti','festivals/akshaya-tritiya','festivals/vat-savitri','festivals/durga-puja','festivals/diwali'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Verified festival rule</span>
            <h3 id="tkFestivalTitle"><?= htmlspecialchars($page['title']) ?></h3>
            <p>Festival date and local timing are selected from exact Tithi windows plus the required Madhyahna, Aparahna, Pradosh, sunrise or moonrise rule.</p>
          </div>
          <div class="tk-panchang-engine">Festival rule engine · Lahiri</div>
        </div>
        <div id="tkFestivalLoading" class="tk-panchang-loading">Calculating festival rule…</div>
        <div id="tkFestivalNote" class="tk-lunar-note"></div>
        <div id="tkFestivalResult" class="tk-festival-result"></div>
      <?php elseif (in_array($page['slug'], ['vrat/pradosham','vrat/sankashti-chaturthi','vrat/masik-shivaratri','festivals/maha-shivaratri'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Location-sensitive Vrat rule</span>
            <h3 id="tkObservanceTitle"><?= htmlspecialchars($page['title']) ?></h3>
            <p>Observance dates are selected from the shared Lahiri Panchang using the local sunset, moonrise or Nishita rule required by this Vrat.</p>
          </div>
          <div class="tk-panchang-engine">Rule engine · Lahiri</div>
        </div>
        <div id="tkObservanceLoading" class="tk-panchang-loading">Calculating yearly observances…</div>
        <div id="tkObservanceNote" class="tk-lunar-note"></div>
        <div id="tkObservanceList" class="tk-observance-list"></div>
      <?php elseif ($page['slug'] === 'vrat/dwadashi'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Dwadashi observance engine</span>
            <h3 id="tkDwadashiTitle">Dwadashi Dates</h3>
            <p>Exact Dwadashi Tithi spans are resolved into local observance dates with month-specific names and next-day Parana windows.</p>
          </div>
          <div class="tk-panchang-engine">Rule engine · Lahiri</div>
        </div>
        <div id="tkDwadashiLoading" class="tk-panchang-loading">Calculating Dwadashi observances…</div>
        <div id="tkDwadashiNote" class="tk-lunar-note"></div>
        <div id="tkDwadashiList" class="tk-dwadashi-list"></div>
      <?php elseif ($page['slug'] === 'vrat/mahadwadashi'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Mahadwadashi rule detector</span>
            <h3 id="tkMahadwadashiTitle">Mahadwadashi</h3>
            <p>Eight Mahadwadashi combinations are detected from Tithi extension, local sunrise/sunset and full-day Nakshatra evidence. Multiple yogas may occur together.</p>
          </div>
          <div class="tk-panchang-engine">Evidence-first classifier</div>
        </div>
        <div id="tkMahadwadashiLoading" class="tk-panchang-loading">Detecting Mahadwadashi yogas…</div>
        <div id="tkMahadwadashiNote" class="tk-lunar-note"></div>
        <div id="tkMahadwadashiList" class="tk-mahadwadashi-list"></div>
      <?php elseif (in_array($page['slug'], ['vrat/ekadashi','vrat/purnima','vrat/amavasya'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Astronomical occurrence engine</span>
            <h3 id="tkLunarTitle"><?= htmlspecialchars($page['title']) ?></h3>
            <p>Exact Tithi windows are calculated first; observance-specific rules are layered separately so the site does not guess a religious date.</p>
          </div>
          <div class="tk-panchang-engine">Moon phase + sunrise state</div>
        </div>
        <div id="tkLunarLoading" class="tk-panchang-loading">Calculating yearly lunar occurrences…</div>
        <div id="tkLunarNote" class="tk-lunar-note"></div>
        <div id="tkLunarList" class="tk-lunar-list"></div>
      <?php elseif (in_array($page['slug'], ['vrat/sankranti','calendars/sankranti','festivals/sankranti','festivals/makar-sankranti'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Nirayana solar ingress</span>
            <h3 id="tkSankrantiTitle">Sankranti <?= date('Y') ?></h3>
            <p>Exact Lahiri sidereal Sun ingress moments for all twelve Rashis. Festival/Punya Kaal rules are kept separate from the astronomical ingress.</p>
          </div>
          <div class="tk-panchang-engine">Astronomy Engine · Lahiri</div>
        </div>
        <div id="tkSankrantiLoading" class="tk-panchang-loading">Calculating yearly Sankranti moments…</div>
        <div id="tkSankrantiNote" class="tk-lunar-note"></div>
        <div id="tkSankrantiList" class="tk-sankranti-list"></div>
      <?php elseif (in_array($page['slug'], ['astronomy/vernal-equinox','astronomy/summer-solstice','astronomy/autumnal-equinox','astronomy/winter-solstice'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Verified astronomy event</span>
            <h3 id="tkSeasonTitle">Calculating seasonal event…</h3>
            <p id="tkSeasonMeta">The astronomical instant is global and displayed in the selected location's local timezone.</p>
          </div>
          <div class="tk-panchang-engine">Astronomy Engine</div>
        </div>
        <div id="tkSeasonLoading" class="tk-panchang-loading">Calculating equinoxes and solstices…</div>
        <div class="tk-single-result">
          <small id="tkSeasonWeekday">Local date & time</small>
          <strong id="tkSeasonResult">—</strong>
        </div>
        <div id="tkSeasonAll" class="tk-season-all"></div>
      <?php elseif (in_array($page['slug'], ['muhurat/lagna','panchang/lagna-kundali'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Live Lagna engine</span>
            <h3 id="tkLagnaTitle">Sidereal Lagna timeline</h3>
            <p>Location-aware Lahiri ascendant periods derived from local apparent sidereal time. Sign lengths are calculated, not assumed.</p>
          </div>
          <div class="tk-panchang-engine">GAST · true obliquity · Lahiri</div>
        </div>
        <div id="tkLagnaLoading" class="tk-panchang-loading">Calculating Lagna periods…</div>
        <div id="tkLagnaList" class="tk-observance-list"></div>
      <?php elseif (in_array($page['slug'], ['panchang/moonrise-moonset','panchang/rahu-kala','muhurat/rahu-kala','muhurat/abhijit'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Live calculation</span>
            <h3 id="tkSinglePrimary">Calculating…</h3>
            <p id="tkSingleMeta">Using the shared Tithika astronomy engine and selected local date.</p>
          </div>
          <div class="tk-panchang-engine" id="tkEngineMeta">Astronomy Engine · Lahiri</div>
        </div>
        <div class="tk-single-result">
          <small>Local timing</small>
          <strong id="tkSingleSecondary">—</strong>
        </div>
      <?php elseif ($page['template'] === 'calendar' || $page['template'] === 'festival'): ?>
        <span class="tk-card-tag">Calendar interface</span>
        <h3>Month-first navigation</h3>
        <p>Compact calendar cells, event badges and drill-down replace long page tables. Location and selected date stay in shared context.</p>
        <div class="tk-calendar-demo">
          <?php for($d=1;$d<=28;$d++): ?>
            <div class="tk-day<?= $d===6?' mark':'' ?><?= in_array($d,[11,19,24],true)?' good':'' ?>"><b><?= $d ?></b><?= $d===6?'Today':'' ?></div>
          <?php endfor; ?>
        </div>
      <?php elseif ($page['template'] === 'calculator'): ?>
        <span class="tk-card-tag">Focused calculator</span>
        <h3>Inputs first. Result second.</h3>
        <p>Birth/location details are separated from the result so mobile users are not forced through a long reference document.</p>
        <div class="tk-form-demo">
          <div class="tk-field">Date / birth date</div>
          <div class="tk-field">Time / birth time</div>
          <div class="tk-field">Location</div>
          <button class="tk-primary" type="button" disabled>Calculation engine adapter pending</button>
        </div>
      <?php elseif ($page['template'] === 'astronomy'): ?>
        <span class="tk-card-tag">Event timeline</span>
        <h3>Chronological astronomical events</h3>
        <p>Event pages use a timeline with exact timestamps, state changes and explanatory metadata instead of dense tables.</p>
        <div class="tk-event-list">
          <?php foreach (['Previous event','Current state','Next event'] as $i=>$label): ?>
            <div class="tk-event"><div class="tk-event-date"><?= $i===1?'NOW':'DATE' ?></div><div><strong><?= htmlspecialchars($label) ?></strong><span>Verified calculation data will populate this row.</span></div><em>Details →</em></div>
          <?php endforeach; ?>
        </div>
      <?php elseif ($page['template'] === 'devotion' || $page['template'] === 'article'): ?>
        <span class="tk-card-tag">Reading mode</span>
        <h3>Distraction-light reference content</h3>
        <div class="tk-reading"><p><span class="tk-drop"><?= htmlspecialchars(mb_substr($page['title'],0,1)) ?></span><?= htmlspecialchars($page['title']) ?> is mapped into Tithika as a focused reading page. The final editorial content can support language switching, larger text, audio, bookmarks and links back to the relevant calendar or Muhurat tool without mixing those controls into the reading surface.</p></div>
      <?php elseif ($page['template'] === 'gallery'): ?>
        <span class="tk-card-tag">Visual collection</span>
        <h3>Fast, lazy-loaded visual browsing</h3>
        <p>Image-heavy pages are separated from calculation pages and designed for responsive lazy loading.</p>
        <div class="tk-gallery-demo"><?php for($i=0;$i<9;$i++): ?><div class="tk-gallery-tile"></div><?php endfor; ?></div>
      <?php else: ?>
        <span class="tk-card-tag"><?= htmlspecialchars(tithika_template_label($page['template'])) ?></span>
        <h3>Task-first results</h3>
        <p>This page uses compact result rows, a sticky date/location context and progressive disclosure. Unsupported values remain intentionally blank until their engine module is validated.</p>
        <div class="tk-placeholder-list">
          <div class="tk-placeholder-row"><i></i><span>Primary timing / result</span></div>
          <div class="tk-placeholder-row"><i></i><span>Secondary timing / context</span></div>
          <div class="tk-placeholder-row"><i></i><span>Related Panchang condition</span></div>
          <div class="tk-placeholder-row"><i></i><span>Notes and calculation method</span></div>
        </div>
      <?php endif; ?>
    </div>

    <aside class="tk-card span-4">
      <div class="tk-card-icon"><?= htmlspecialchars($group['icon']) ?></div>
      <span class="tk-card-tag">Shared context</span>
      <h3>One location and date across Tithika</h3>
      <p>Users should not have to re-select city, timezone and date as they move between Panchang, Muhurat, festival and astronomy tools.</p>
      <a class="tk-link" href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>">Browse all mapped pages →</a>
    </aside>

    <div class="tk-preview span-12" style="grid-column:span 12">
      <small>Performance architecture</small>
      <h3>Shared shell, page-specific data.</h3>
      <p>The route shares one CSS asset, one lightweight JavaScript context layer and a common PHP renderer. Specialized engines can be loaded only on pages that need them.</p>
    </div>
  </div>

  <?php if ($related): ?>
  <section class="tk-related">
    <div class="tk-section-head"><div><span>Keep exploring</span><h2>Related <?= htmlspecialchars($group['title']) ?> tools</h2></div></div>
    <div class="tk-related-grid">
      <?php foreach ($related as $item): ?>
        <a href="<?= htmlspecialchars(tithika_pretty_url($item['slug'])) ?>"><b><?= htmlspecialchars($item['title']) ?></b><span><?= htmlspecialchars(tithika_template_label($item['template'])) ?> →</span></a>
      <?php endforeach; ?>
    </div>
  </section>
  <?php endif; ?>
</section>
<?php tithika_render_footer(); ?>