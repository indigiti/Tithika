<?php
declare(strict_types=1);
require __DIR__ . '/includes/site.php';

$routes = tithika_routes();
tithika_render_header('Modern Panchang, Muhurat & Jyotish');
?>
<section class="tk-home-dashboard" id="tkHomeDashboard" aria-live="polite">
  <div class="tk-home-dashboard-hero">
    <div class="tk-home-dashboard-copy">
      <span class="tk-home-kicker">Daily intelligence · location aware · evidence first</span>
      <h1>Your day in <em>Vedic time.</em></h1>
      <p>One live dashboard for today’s Panchang, current Choghadiya, the next favorable windows, upcoming observances and planetary movement—calculated for your selected location.</p>
      <div class="tk-home-actions">
        <a class="primary" href="<?= htmlspecialchars(tithika_url('intelligence/')) ?>">Ask Tithika Intelligence →</a>
        <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/daily')) ?>">Full Panchang</a>
        <a href="<?= htmlspecialchars(tithika_pretty_url('muhurat/choghadiya')) ?>">Choghadiya</a>
        <a href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>">All tools</a>
      </div>
      <div class="tk-home-live-meta">
        <span><i></i><b id="tkHomePlace">Resolving location…</b></span>
        <span id="tkHomeDate">Loading today…</span>
        <span id="tkHomeCache">Live engines</span>
      </div>
    </div>

    <aside class="tk-home-now-card" id="tkHomeNow">
      <div class="tk-home-now-head"><span>Current Choghadiya</span><b id="tkHomeNowBadge">LIVE</b></div>
      <strong id="tkHomeCurrentName">—</strong>
      <p id="tkHomeCurrentLabel">Calculating the current traditional timing period…</p>
      <div class="tk-home-now-time"><span id="tkHomeCurrentRange">—</span><span id="tkHomeCurrentSide">—</span></div>
      <div class="tk-home-now-bar"><i id="tkHomeCurrentProgress"></i></div>
      <a href="<?= htmlspecialchars(tithika_pretty_url('muhurat/choghadiya')) ?>">Open complete Choghadiya →</a>
    </aside>
  </div>

  <div class="tk-home-today-grid">
    <article><small>Tithi</small><strong id="tkHomeTithi">—</strong><span id="tkHomePaksha">—</span></article>
    <article><small>Nakshatra</small><strong id="tkHomeNakshatra">—</strong><span>At local sunrise</span></article>
    <article><small>Yoga</small><strong id="tkHomeYoga">—</strong><span id="tkHomeKarana">Karana —</span></article>
    <article><small>Moon</small><strong id="tkHomeMoon">—</strong><span id="tkHomeMonth">Lunar month —</span></article>
    <article><small>Sunrise</small><strong id="tkHomeSunrise">—</strong><span id="tkHomeSunset">Sunset —</span></article>
    <article class="is-caution"><small>Rahu Kaal</small><strong id="tkHomeRahu">—</strong><span>Traditional avoid window</span></article>
  </div>

  <div class="tk-home-dashboard-grid">
    <section class="tk-home-dash-card tk-home-advisor-card">
      <header><div><span>Intelligence advisor</span><h2>Best windows ahead.</h2></div><a href="<?= htmlspecialchars(tithika_url('intelligence/')) ?>">Ask why →</a></header>
      <p id="tkHomeAdvisorSummary">Ranking verified Panchang and Muhurat windows for the next seven days…</p>
      <div class="tk-home-recommendations" id="tkHomeRecommendations"><div class="tk-home-skeleton"></div><div class="tk-home-skeleton"></div></div>
    </section>

    <section class="tk-home-dash-card">
      <header><div><span>Upcoming calendar</span><h2>What’s next.</h2></div><a href="<?= htmlspecialchars(tithika_pretty_url('festivals/hindu')) ?>">Calendar →</a></header>
      <div class="tk-home-event-list" id="tkHomeCalendar"><div class="tk-home-skeleton"></div><div class="tk-home-skeleton"></div><div class="tk-home-skeleton"></div></div>
    </section>

    <section class="tk-home-dash-card">
      <header><div><span>Planetary movement</span><h2>Next transits.</h2></div><a href="<?= htmlspecialchars(tithika_pretty_url('planets/transit')) ?>">All transits →</a></header>
      <div class="tk-home-event-list" id="tkHomePlanets"><div class="tk-home-skeleton"></div><div class="tk-home-skeleton"></div></div>
    </section>

    <section class="tk-home-dash-card tk-home-proof-card">
      <header><div><span>Evidence contract</span><h2>Why you can inspect it.</h2></div></header>
      <div class="tk-home-proof-grid">
        <div><b>292</b><span>certified routes</span></div>
        <div><b>6</b><span>intelligence layers</span></div>
        <div><b>0</b><span>runtime CSS frameworks</span></div>
      </div>
      <div id="tkHomeProvenance" class="tk-home-provenance"><span>Loading engine provenance…</span></div>
    </section>
  </div>

  <div class="tk-home-error" id="tkHomeError" hidden>
    <strong>Daily dashboard is temporarily unavailable.</strong>
    <span>Core Tithika tools remain available; try refreshing or open the Daily Panchang directly.</span>
  </div>
</section>

<section class="tk-home-section">
  <div class="tk-home-section-head">
    <div><span>Explore Tithika</span><h2>One platform, clear product families.</h2></div>
    <p>Each family shares the same local context and calculation contracts, while specialized engines load only where they are needed.</p>
  </div>
  <div class="tk-home-family-grid">
    <?php foreach ($routes as $key=>$group):
      $live = 0;
      foreach ($group['pages'] as $item) {
          $full = tithika_find_page($item['slug']);
          if ($full && tithika_is_indexable_page($full)) $live++;
      }
    ?>
      <a class="tk-home-family" href="<?= htmlspecialchars(tithika_pretty_url($key)) ?>">
        <i aria-hidden="true"><?= htmlspecialchars($group['icon']) ?></i>
        <h3><?= htmlspecialchars($group['title']) ?></h3>
        <p><?= htmlspecialchars($group['description']) ?></p>
        <small><?= $live ?> production-quality routes →</small>
      </a>
    <?php endforeach; ?>
  </div>
</section>

<section class="tk-home-section alt">
  <div class="tk-home-section-head">
    <div><span>Calculation stack</span><h2>Built around evidence, not black boxes.</h2></div>
    <p>Calculation pages keep astronomical state, observance rules, interpretation and timing layers inspectable.</p>
  </div>
  <div class="tk-home-feature-grid">
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_url('intelligence/')) ?>">
      <b>Tithika Intelligence</b><p>Six explainable layers orchestrate Panchang, Muhurat and Jyotish engines with confidence, provenance, privacy-aware caching and cross-engine quality checks.</p><span>Open Intelligence →</span>
    </a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('panchang/daily')) ?>">
      <b>Daily Panchang</b><p>Tithi, Nakshatra, Yoga, Karana, lunar month and local solar context from the verified Lahiri Panchang engine.</p><span>Open Panchang →</span>
    </a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('muhurat/vivah')) ?>">
      <b>Specialized Muhurat</b><p>Activity-specific windows with Panchang evidence, common blocked-period subtraction and versioned profiles.</p><span>Find Muhurat →</span>
    </a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('jyotish/horoscope-analysis')) ?>">
      <b>Unified Jyotish</b><p>Kundali, Vargas, Shadbala, Ashtakavarga, Yogas, Dasha, interpretation and timing in one connected stack.</p><span>Open analysis →</span>
    </a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('festivals/diwali')) ?>">
      <b>Festival rules</b><p>Major observances resolve exact Tithi windows through reusable sunrise, Madhyahna, Pradosh and Nishita selectors.</p><span>Browse festivals →</span>
    </a>
  </div>
</section>

<section class="tk-home-section">
  <div class="tk-home-section-head">
    <div><span>Reference & devotion</span><h2>Content stays separate from calculation logic.</h2></div>
    <p>Learn, Devotion and Gallery routes now use a structured editorial layer, making them useful without embedding third-party text or media into the core engine.</p>
  </div>
  <div class="tk-home-feature-grid">
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('learn/panchang')) ?>"><b>Learn Panchang</b><p>Understand the five limbs, sunrise-state conventions and how Tithika separates astronomy from observance rules.</p><span>Read guide →</span></a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('devotion/aarti')) ?>"><b>Devotion library</b><p>Structured devotional taxonomy with practice context and links back to relevant festival and timing tools.</p><span>Open library →</span></a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('gallery/hindu-symbols')) ?>"><b>Visual index</b><p>Lightweight original gallery surfaces that do not slow calculation-heavy pages or depend on external artwork.</p><span>Open gallery →</span></a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>"><b>Complete product map</b><p>Browse all <?= tithika_page_count() ?> mapped routes and see which parts of the platform are calculation, content, calendar or reference surfaces.</p><span>Open site map →</span></a>
  </div>
</section>
<script src="<?= htmlspecialchars(tithika_asset_url('assets/home.js')) ?>" defer></script>
<?php tithika_render_footer(); ?>
