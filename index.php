<?php
declare(strict_types=1);
require __DIR__ . '/includes/site.php';

$routes = tithika_routes();
tithika_render_header(tithika_t('home.page_title'));
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
      <article><small><?= htmlspecialchars(tithika_t('home.nakshatra')) ?></small><b id="tkDailyNakshatra">—</b><span id="tkDailyMoon"><?= htmlspecialchars(tithika_t('dynamic.moon')) ?> —</span></article>
      <article><small><?= htmlspecialchars(tithika_t('home.yoga')) ?></small><b id="tkDailyYoga">—</b><span id="tkDailyKarana"><?= htmlspecialchars(tithika_t('dynamic.karana')) ?> —</span></article>
      <article><small><?= htmlspecialchars(tithika_t('home.lunar_month')) ?></small><b id="tkDailyMonth">—</b><span id="tkDailyMonthMode"><?= htmlspecialchars(tithika_t('dynamic.amanta').' '.tithika_t('dynamic.preference')) ?></span></article>
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
    <div><small><?= htmlspecialchars(tithika_t('home.choghadiya')) ?></small><h2 id="tkDailyChogName"><?= htmlspecialchars(tithika_t('home.calculating')) ?></h2><p id="tkDailyChogTime"><?= htmlspecialchars(tithika_t('home.local_sequence')) ?></p></div>
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
    <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/rahu-kala')) ?>"><?= htmlspecialchars(tithika_t('home.details')) ?></a>
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
    <div><span><?= htmlspecialchars(tithika_t('home.explore_kicker')) ?></span><h2><?= htmlspecialchars(tithika_t('home.explore_title')) ?></h2></div>
    <p><?= htmlspecialchars(tithika_t('home.explore_copy')) ?></p>
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
        <h3><?= htmlspecialchars(tithika_t('nav.' . $key, $group['title'])) ?></h3>
        <p><?= htmlspecialchars(tithika_t('groupdesc.' . $key, $group['description'])) ?></p>
        <small><?= htmlspecialchars(tithika_t('home.production_routes', null, ['count'=>$live])) ?></small>
      </a>
    <?php endforeach; ?>
  </div>
</section>

<section class="tk-home-section alt">
  <div class="tk-home-section-head">
    <div><span><?= htmlspecialchars(tithika_t('home.stack_kicker')) ?></span><h2><?= htmlspecialchars(tithika_t('home.stack_title')) ?></h2></div>
    <p><?= htmlspecialchars(tithika_t('home.stack_copy')) ?></p>
  </div>
  <div class="tk-home-feature-grid">
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_url('intelligence/')) ?>">
      <b><?= htmlspecialchars(tithika_t('home.feature_intelligence_title')) ?></b><p><?= htmlspecialchars(tithika_t('home.feature_intelligence_copy')) ?></p><span><?= htmlspecialchars(tithika_t('home.feature_intelligence_action')) ?></span>
    </a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('panchang/daily')) ?>">
      <b><?= htmlspecialchars(tithika_t('home.feature_panchang_title')) ?></b><p><?= htmlspecialchars(tithika_t('home.feature_panchang_copy')) ?></p><span><?= htmlspecialchars(tithika_t('home.feature_panchang_action')) ?></span>
    </a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('muhurat/vivah')) ?>">
      <b><?= htmlspecialchars(tithika_t('home.feature_muhurat_title')) ?></b><p><?= htmlspecialchars(tithika_t('home.feature_muhurat_copy')) ?></p><span><?= htmlspecialchars(tithika_t('home.feature_muhurat_action')) ?></span>
    </a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('jyotish/horoscope-analysis')) ?>">
      <b><?= htmlspecialchars(tithika_t('home.feature_jyotish_title')) ?></b><p><?= htmlspecialchars(tithika_t('home.feature_jyotish_copy')) ?></p><span><?= htmlspecialchars(tithika_t('home.feature_jyotish_action')) ?></span>
    </a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('festivals/diwali')) ?>">
      <b><?= htmlspecialchars(tithika_t('home.feature_festival_title')) ?></b><p><?= htmlspecialchars(tithika_t('home.feature_festival_copy')) ?></p><span><?= htmlspecialchars(tithika_t('home.feature_festival_action')) ?></span>
    </a>
  </div>
</section>

<section class="tk-home-section">
  <div class="tk-home-section-head">
    <div><span><?= htmlspecialchars(tithika_t('home.reference_kicker')) ?></span><h2><?= htmlspecialchars(tithika_t('home.reference_title')) ?></h2></div>
    <p><?= htmlspecialchars(tithika_t('home.reference_copy')) ?></p>
  </div>
  <div class="tk-home-feature-grid">
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('learn/panchang')) ?>"><b><?= htmlspecialchars(tithika_t('home.feature_learn_title')) ?></b><p><?= htmlspecialchars(tithika_t('home.feature_learn_copy')) ?></p><span><?= htmlspecialchars(tithika_t('home.feature_learn_action')) ?></span></a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('devotion/aarti')) ?>"><b><?= htmlspecialchars(tithika_t('home.feature_devotion_title')) ?></b><p><?= htmlspecialchars(tithika_t('home.feature_devotion_copy')) ?></p><span><?= htmlspecialchars(tithika_t('home.feature_devotion_action')) ?></span></a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_pretty_url('gallery/hindu-symbols')) ?>"><b><?= htmlspecialchars(tithika_t('home.feature_gallery_title')) ?></b><p><?= htmlspecialchars(tithika_t('home.feature_gallery_copy')) ?></p><span><?= htmlspecialchars(tithika_t('home.feature_gallery_action')) ?></span></a>
    <a class="tk-home-feature" href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>"><b><?= htmlspecialchars(tithika_t('home.feature_map_title')) ?></b><p><?= htmlspecialchars(tithika_t('home.feature_map_copy', null, ['count'=>tithika_page_count()])) ?></p><span><?= htmlspecialchars(tithika_t('home.feature_map_action')) ?></span></a>
  </div>
</section>
<?php tithika_render_footer(); ?>
