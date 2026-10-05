<?php
declare(strict_types=1);
require __DIR__ . '/includes/site.php';
$routes = tithika_routes();
tithika_render_header('Site Map');
?>
<section class="tk-group-hero">
  <div class="tk-group-icon">⌘</div>
  <h1>Tithika site map</h1>
  <p><?= tithika_page_count() ?> mapped utility and content pages, organized into shared product families. This map is the implementation contract for the upgraded Tithika experience.</p>
</section>
<section class="tk-map-wrap">
  <?php foreach ($routes as $key => $group): ?>
    <section class="tk-family">
      <div class="tk-family-head">
        <div class="tk-family-icon"><?= htmlspecialchars($group['icon']) ?></div>
        <div><h2><a href="<?= htmlspecialchars(tithika_pretty_url($key)) ?>"><?= htmlspecialchars($group['title']) ?></a></h2><p><?= htmlspecialchars($group['description']) ?></p></div>
      </div>
      <div class="tk-map-grid">
        <?php foreach ($group['pages'] as $page): ?>
          <a class="tk-map-link" href="<?= htmlspecialchars(tithika_pretty_url($page['slug'])) ?>">
            <b><?= htmlspecialchars($page['title']) ?></b>
            <span><?= htmlspecialchars(tithika_template_label($page['template'])) ?></span>
          </a>
        <?php endforeach; ?>
      </div>
    </section>
  <?php endforeach; ?>
</section>
<?php tithika_render_footer(); ?>
