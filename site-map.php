<?php
declare(strict_types=1);
require __DIR__ . '/includes/site.php';
$routes = tithika_routes();
tithika_render_header('Site Map');
?>
<section class="tk-group-hero">
  <div class="tk-group-icon">⌘</div>
  <h1>Tithika site map</h1>
  <p><?= tithika_page_count() ?> mapped routes across the Tithika product families. <?= tithika_indexable_count() ?> are indexable across verified calculation, calculated aggregation, structured reference and editorial quality tiers.</p>
</section>
<section class="tk-map-wrap">
  <?php foreach ($routes as $key => $group): ?>
    <section class="tk-family">
      <div class="tk-family-head">
        <div class="tk-family-icon"><?= htmlspecialchars($group['icon']) ?></div>
        <div><h2><a href="<?= htmlspecialchars(tithika_pretty_url($key)) ?>"><?= htmlspecialchars($group['title']) ?></a></h2><p><?= htmlspecialchars($group['description']) ?></p></div>
      </div>
      <div class="tk-map-grid">
        <?php foreach ($group['pages'] as $page):
          $full = tithika_find_page($page['slug']);
          $status = ($full && tithika_is_live_page($page['slug'])) ? 'Verified'
            : (($full && tithika_is_aggregate_page($page['slug'])) ? 'Aggregate'
            : (($full && tithika_is_reference_page($page['slug'])) ? 'Reference'
            : (($full && tithika_has_editorial_content($full)) ? 'Editorial' : 'Mapped')));
        ?>
          <a class="tk-map-link" href="<?= htmlspecialchars(tithika_pretty_url($page['slug'])) ?>">
            <b><?= htmlspecialchars($page['title']) ?></b>
            <span><?= htmlspecialchars(tithika_template_label($page['template'])) ?> · <?= htmlspecialchars($status) ?></span>
          </a>
        <?php endforeach; ?>
      </div>
    </section>
  <?php endforeach; ?>
</section>
<?php tithika_render_footer(); ?>
