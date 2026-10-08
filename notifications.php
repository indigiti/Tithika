<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/site.php';
tithika_render_header(tithika_t('notifications.title'));
$categories=['ekadashi','purnima','amavasya','sankashti','pradosh','shivaratri','sankranti','festivals','transit','retrograde','solar'];
?>
<section class="tk-notify-hero" id="tkNotificationCenter">
  <div class="tk-notify-hero-copy">
    <span class="tk-home-kicker"><?= htmlspecialchars(tithika_t('notifications.kicker')) ?></span>
    <h1><?= htmlspecialchars(tithika_t('notifications.hero')) ?></h1>
    <p><?= htmlspecialchars(tithika_t('notifications.intro')) ?></p>
    <div class="tk-notify-hero-actions">
      <a class="primary" href="#tkNotifyAgenda"><?= htmlspecialchars(tithika_t('notifications.upcoming')) ?></a>
      <a href="<?= htmlspecialchars(tithika_url('settings/')) ?>"><?= htmlspecialchars(tithika_t('nav.settings')) ?></a>
    </div>
  </div>
  <aside class="tk-notify-privacy">
    <small><?= htmlspecialchars(tithika_t('notifications.privacy')) ?></small>
    <p><?= htmlspecialchars(tithika_t('notifications.privacy_copy')) ?></p>
  </aside>
</section>

<section class="tk-notify-grid">
  <article class="tk-notify-card span-2">
    <header>
      <div><span><?= htmlspecialchars(tithika_t('notifications.settings')) ?></span><h2><?= htmlspecialchars(tithika_t('notifications.categories')) ?></h2></div>
      <p><?= htmlspecialchars(tithika_t('notifications.categories_copy')) ?></p>
    </header>
    <div class="tk-notify-categories" id="tkNotifyCategories">
      <?php foreach($categories as $category): ?>
        <button type="button" data-notify-category="<?= htmlspecialchars($category) ?>" aria-pressed="false">
          <i aria-hidden="true">✓</i><span><?= htmlspecialchars(tithika_t('notifications.cat.'.$category, ucfirst($category))) ?></span>
        </button>
      <?php endforeach; ?>
    </div>
  </article>

  <article class="tk-notify-card">
    <header><div><span><?= htmlspecialchars(tithika_t('notifications.onsite')) ?></span><h2><?= htmlspecialchars(tithika_t('notifications.onsite')) ?></h2></div></header>
    <p><?= htmlspecialchars(tithika_t('notifications.onsite_copy')) ?></p>
    <button type="button" class="tk-notify-action primary" id="tkNotifyPermission"><?= htmlspecialchars(tithika_t('notifications.enable')) ?></button>
    <small id="tkNotifyPermissionState"></small>
  </article>

  <article class="tk-notify-card">
    <header><div><span>ICS</span><h2><?= htmlspecialchars(tithika_t('notifications.calendar')) ?></h2></div></header>
    <p><?= htmlspecialchars(tithika_t('notifications.calendar_copy')) ?></p>
    <div class="tk-notify-feed-actions">
      <a class="tk-notify-action primary" id="tkNotifyFeed" href="<?= htmlspecialchars(tithika_url('calendar.ics')) ?>" target="_blank" rel="noopener"><?= htmlspecialchars(tithika_t('notifications.open_feed')) ?></a>
      <button type="button" class="tk-notify-action" id="tkNotifyCopyFeed"><?= htmlspecialchars(tithika_t('notifications.copy_feed')) ?></button>
    </div>
    <code id="tkNotifyFeedPreview"><?= htmlspecialchars(tithika_url('calendar.ics')) ?></code>
  </article>
</section>

<section class="tk-home-section tk-notify-agenda" id="tkNotifyAgenda">
  <div class="tk-home-section-head">
    <div><span><?= htmlspecialchars(tithika_t('notifications.horizon')) ?></span><h2><?= htmlspecialchars(tithika_t('notifications.upcoming')) ?></h2></div>
    <p><?= htmlspecialchars(tithika_t('notifications.upcoming_copy')) ?></p>
  </div>
  <div class="tk-notify-agenda-list" id="tkNotifyAgendaList" aria-live="polite">
    <div class="tk-upcoming-empty"><?= htmlspecialchars(tithika_t('notifications.loading')) ?></div>
  </div>
</section>
<?php tithika_render_footer(); ?>
