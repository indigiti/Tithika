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
$isComputed = in_array($page['slug'], ['panchang/daily','panchang/moonrise-moonset','panchang/rahu-kala','muhurat/rahu-kala','muhurat/abhijit'], true);
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
    <span class="tk-engine-state<?= $isComputed ? ' is-live' : '' ?>"><?= $page['slug'] === 'panchang/daily' ? 'Panchang engine live' : ($isComputed ? 'Solar calculation live' : 'Page shell mapped') ?></span>
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
      <?php if ($page['slug'] === 'panchang/daily'): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Verified astronomy</span>
            <h3>Daily Panchang at sunrise</h3>
            <p>Sidereal Sun and Moon positions use Lahiri ayanamsha. Each row shows the state at local sunrise and its next transition.</p>
          </div>
          <div class="tk-panchang-engine" id="tkEngineMeta">Swiss Ephemeris · Lahiri</div>
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
      <?php elseif (in_array($page['slug'], ['panchang/moonrise-moonset','panchang/rahu-kala','muhurat/rahu-kala','muhurat/abhijit'], true)): ?>
        <div class="tk-panchang-live-head">
          <div>
            <span class="tk-card-tag">Live calculation</span>
            <h3 id="tkSinglePrimary">Calculating…</h3>
            <p id="tkSingleMeta">Using the shared Tithika astronomy engine and selected local date.</p>
          </div>
          <div class="tk-panchang-engine" id="tkEngineMeta">Swiss Ephemeris · Lahiri</div>
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
