<?php
declare(strict_types=1);
require __DIR__ . '/includes/site.php';

$routes = tithika_routes();
tithika_render_header('Modern Panchang, Muhurat & Jyotish');
?>
<section class="tk-daily-hero" id="tkDailyDashboard" aria-busy="true">
  <div class="tk-daily-backdrop" aria-hidden="true"></div>
  <div class="tk-daily-copy">
    <span class="tk-home-kicker"><?= htmlspecialchars(tithika_t('home.kicker')) ?></span>
    <h1><?= htmlspecialchars(tithika_t('home.title')) ?></h1>
    <p id="tkDailyLead"><?= htmlspecialchars(tithika_t('home.loading')) ?></p>
    <div class="tk-daily-actions">
      <a class="primary" href="<?= htmlspecialchars(tithika_url('intelligence/')) ?>"><?= htmlspecialchars(tithika_t('home.ask')) ?></a>
      <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/daily')) ?>"><?= htmlspecialchars(tithika_t('home.full_panchang')) ?></a>
      <a href="<?= htmlspecialchars(tithika_url('settings/')) ?>"><?= htmlspecialchars(tithika_t('home.personalize')) ?></a>
    </div>
  </div>

  <div class="tk-daily-summary">
    <header>
      <div><small id="tkDailyDate"><?= htmlspecialchars(tithika_t('home.selected_date')) ?></small><strong id="tkDailyLocation"><?= htmlspecialchars(tithika_t('home.resolving')) ?></strong></div>
      <span class="tk-daily-live"><i></i> <?= htmlspecialchars(tithika_t('home.verified')) ?></span>
    </header>
    <div class="tk-daily-primary-grid">
      <article><small><?= htmlspecialchars(tithika_t('home.tithi')) ?></small><b id="tkDailyTithi">—</b><span id="tkDailyPaksha">—</span></article>
      <article><small><?= htmlspecialchars(tithika_t('home.nakshatra')) ?></small><b id="tkDailyNakshatra">—</b><span id="tkDailyMoon">Moon —</span></article>
      <article><small><?= htmlspecialchars(tithika_t('home.yoga')) ?></small><b id="tkDailyYoga">—</b><span id="tkDailyKarana">Karana —</span></article>
      <article><small><?= htmlspecialchars(tithika_t('home.lunar_month')) ?></small><b id="tkDailyMonth">—</b><span id="tkDailyMonthMode">Amanta preference</span></article>
    </div>
    <div class="tk-daily-solar">
      <span><small><?= htmlspecialchars(tithika_t('home.sunrise')) ?></small><b id="tkDailySunrise">—</b></span>
      <span><small><?= htmlspecialchars(tithika_t('home.sunset')) ?></small><b id="tkDailySunset">—</b></span>
      <span><small><?= htmlspecialchars(tithika_t('home.moonrise')) ?></small><b id="tkDailyMoonrise">—</b></span>
    </div>
  </div>
</section>

<section class="tk-daily-strip">
  <article class="tk-now-card">
    <div class="tk-now-icon">✦</div>
    <div><small><?= htmlspecialchars(tithika_t('home.choghadiya')) ?></small><h2 id="tkDailyChogName">Calculating…</h2><p id="tkDailyChogTime">Local day/night sequence</p></div>
    <a href="<?= htmlspecialchars(tithika_pretty_url('muhurat/choghadiya')) ?>"><?= htmlspecialchars(tithika_t('home.open_timeline')) ?></a>
  </article>
  <article class="tk-now-card">
    <div class="tk-now-icon">☀</div>
    <div><small><?= htmlspecialchars(tithika_t('home.abhijit')) ?></small><h2 id="tkDailyAbhijit">—</h2><p><?= htmlspecialchars(tithika_t('home.abhijit_note')) ?></p></div>
    <a href="<?= htmlspecialchars(tithika_pretty_url('muhurat/abhijit')) ?>"><?= htmlspecialchars(tithika_t('home.details')) ?></a>
  </article>
  <article class="tk-now-card">
    <div class="tk-now-icon">◐</div>
    <div><small><?= htmlspecialchars(tithika_t('home.rahu')) ?></small><h2 id="tkDailyRahu">—</h2><p><?= htmlspecialchars(tithika_t('home.rahu_note')) ?></p></div>
    <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/rahu-kala')) ?>">Details →</a>
  </article>
</section>

<section class="tk-home-section tk-upcoming-section">
  <div class="tk-home-section-head">
    <div><span><?= htmlspecialchars(tithika_t('home.upcoming')) ?></span><h2><?= htmlspecialchars(tithika_t('home.next_days')) ?></h2></div>
    <p><?= htmlspecialchars(tithika_t('home.upcoming_copy')) ?></p>
  </div>
  <div class="tk-upcoming-grid" id="tkUpcomingEvents" aria-live="polite">
    <div class="tk-upcoming-skeleton"></div><div class="tk-upcoming-skeleton"></div><div class="tk-upcoming-skeleton"></div>
  </div>
</section>

<section class="tk-home-ai">
  <div><span><?= htmlspecialchars(tithika_t('home.ai_kicker')) ?></span><h2><?= htmlspecialchars(tithika_t('home.ai_title')) ?></h2><p><?= htmlspecialchars(tithika_t('home.ai_copy')) ?></p></div>
  <a href="<?= htmlspecialchars(tithika_url('intelligence/')) ?>"><?= htmlspecialchars(tithika_t('home.open_ai')) ?> <b>↗</b></a>
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
<?php tithika_render_footer(); ?>
