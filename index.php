<?php
declare(strict_types=1);
require __DIR__ . '/includes/site.php';

$routes = tithika_routes();
tithika_render_header('Modern Panchang, Muhurat & Jyotish');
?>
<section class="tk-home-hero">
  <div class="tk-home-hero-inner">
    <div>
      <span class="tk-home-kicker">Location-aware · evidence-first</span>
      <h1>Vedic time, without the clutter.</h1>
      <p>Tithika combines daily Panchang, Choghadiya, Muhurat, festivals, regional calendars and Jyotish in one responsive system. Exact astronomy and rule-based observances remain separate so every result can show where it came from.</p>
      <div class="tk-home-actions">
        <a class="primary" href="<?= htmlspecialchars(tithika_url('intelligence/')) ?>">Open Tithika Intelligence →</a>
        <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/daily')) ?>">Daily Panchang</a>
        <a href="<?= htmlspecialchars(tithika_pretty_url('muhurat/choghadiya')) ?>">Choghadiya</a>
        <a href="<?= htmlspecialchars(tithika_pretty_url('jyotish/janma-kundali')) ?>">Janma Kundali</a>
        <a href="<?= htmlspecialchars(tithika_url('site-map.php')) ?>">All tools</a>
      </div>
    </div>
    <aside class="tk-home-panel">
      <small>Production map</small>
      <h2><?= tithika_page_count() ?> logical routes</h2>
      <p>Only verified calculation routes and structured editorial pages are exposed as indexable SEO surfaces. Remaining mapped shells stay available for product development without becoming thin search pages.</p>
      <div class="tk-home-stats">
        <div><b><?= tithika_indexable_count() ?></b><span>indexable/live pages</span></div>
        <div><b><?= count($routes) ?></b><span>product families</span></div>
        <div><b>1</b><span>shared location/date context</span></div>
        <div><b>0</b><span>runtime CSS frameworks</span></div>
      </div>
    </aside>
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
<?php tithika_render_footer(); ?>
