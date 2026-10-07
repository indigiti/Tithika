<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/site.php';
tithika_render_header(tithika_t('settings.title'));
?>
<section class="tk-settings-hero">
  <div>
    <span class="tk-home-kicker"><?= htmlspecialchars(tithika_t('settings.kicker')) ?></span>
    <h1><?= htmlspecialchars(tithika_t('settings.hero')) ?></h1>
    <p><?= htmlspecialchars(tithika_t('settings.intro')) ?></p>
  </div>
  <aside>
    <small><?= htmlspecialchars(tithika_t('settings.privacy')) ?></small>
    <strong><?= htmlspecialchars(tithika_t('settings.local')) ?></strong>
    <p><?= htmlspecialchars(tithika_t('settings.privacy_copy')) ?></p>
  </aside>
</section>

<section class="tk-settings-wrap" id="tkSettingsApp">
  <div class="tk-settings-grid">
    <article class="tk-settings-card">
      <header><span><?= htmlspecialchars(tithika_t('settings.appearance')) ?></span><h2><?= htmlspecialchars(tithika_t('settings.theme')) ?></h2></header>
      <div class="tk-settings-options" data-setting="theme">
        <button type="button" data-value="system"><b><?= htmlspecialchars(tithika_t('settings.system')) ?></b><small><?= htmlspecialchars(tithika_t('settings.system_note')) ?></small></button>
        <button type="button" data-value="light"><b><?= htmlspecialchars(tithika_t('settings.light')) ?></b><small><?= htmlspecialchars(tithika_t('settings.light_note')) ?></small></button>
        <button type="button" data-value="dark"><b><?= htmlspecialchars(tithika_t('settings.dark')) ?></b><small><?= htmlspecialchars(tithika_t('settings.dark_note')) ?></small></button>
      </div>
    </article>

    <article class="tk-settings-card">
      <header><span><?= htmlspecialchars(tithika_t('settings.time')) ?></span><h2><?= htmlspecialchars(tithika_t('settings.clock')) ?></h2></header>
      <div class="tk-settings-options" data-setting="clock">
        <button type="button" data-value="12"><b><?= htmlspecialchars(tithika_t('settings.12')) ?></b><small>1:30 PM</small></button>
        <button type="button" data-value="24"><b><?= htmlspecialchars(tithika_t('settings.24')) ?></b><small>13:30</small></button>
      </div>
    </article>

    <article class="tk-settings-card">
      <header><span><?= htmlspecialchars(tithika_t('settings.lunar')) ?></span><h2><?= htmlspecialchars(tithika_t('settings.month')) ?></h2></header>
      <div class="tk-settings-options" data-setting="lunarMonth">
        <button type="button" data-value="amanta"><b><?= htmlspecialchars(tithika_t('settings.amanta')) ?></b><small><?= htmlspecialchars(tithika_t('settings.amanta_note')) ?></small></button>
        <button type="button" data-value="purnimanta"><b><?= htmlspecialchars(tithika_t('settings.purnimanta')) ?></b><small><?= htmlspecialchars(tithika_t('settings.purnimanta_note')) ?></small></button>
      </div>
    </article>

    <article class="tk-settings-card">
      <header><span><?= htmlspecialchars(tithika_t('settings.observance')) ?></span><h2><?= htmlspecialchars(tithika_t('settings.tradition')) ?></h2></header>
      <div class="tk-settings-options" data-setting="tradition">
        <button type="button" data-value="smarta"><b><?= htmlspecialchars(tithika_t('settings.smarta')) ?></b><small><?= htmlspecialchars(tithika_t('settings.smarta_note')) ?></small></button>
        <button type="button" data-value="vaishnava"><b><?= htmlspecialchars(tithika_t('settings.vaishnava')) ?></b><small><?= htmlspecialchars(tithika_t('settings.vaishnava_note')) ?></small></button>
        <button type="button" data-value="iskcon"><b><?= htmlspecialchars(tithika_t('settings.iskcon')) ?></b><small><?= htmlspecialchars(tithika_t('settings.iskcon_note')) ?></small></button>
      </div>
    </article>

    <article class="tk-settings-card span-2">
      <header><span><?= htmlspecialchars(tithika_t('settings.language')) ?></span><h2><?= htmlspecialchars(tithika_t('settings.language_title')) ?></h2></header>
      <div class="tk-settings-options" data-setting="language">
        <button type="button" data-value="en"><b><?= htmlspecialchars(tithika_t('settings.english')) ?></b><small>English interface</small></button>
        <button type="button" data-value="hi"><b><?= htmlspecialchars(tithika_t('settings.hindi')) ?></b><small>हिन्दी इंटरफ़ेस</small></button>
      </div>
      <p class="tk-settings-helper"><?= htmlspecialchars(tithika_t('settings.language_note')) ?></p>
    </article>

    <article class="tk-settings-card">
      <header><span><?= htmlspecialchars(tithika_t('settings.numerals')) ?></span><h2><?= htmlspecialchars(tithika_t('settings.numerals_title')) ?></h2></header>
      <div class="tk-settings-options" data-setting="numerals">
        <button type="button" data-value="latin"><b><?= htmlspecialchars(tithika_t('settings.latin')) ?></b><small><?= htmlspecialchars(tithika_t('settings.latin_note')) ?></small></button>
        <button type="button" data-value="deva"><b><?= htmlspecialchars(tithika_t('settings.devanagari')) ?></b><small><?= htmlspecialchars(tithika_t('settings.devanagari_note')) ?></small></button>
      </div>
    </article>

    <article class="tk-settings-card span-2">
      <header><span><?= htmlspecialchars(tithika_t('settings.context')) ?></span><h2><?= htmlspecialchars(tithika_t('settings.saved_location')) ?></h2></header>
      <div class="tk-settings-location">
        <div><b id="tkSettingsLocationName"><?= htmlspecialchars(tithika_t('settings.no_location')) ?></b><small id="tkSettingsLocationMeta"><?= htmlspecialchars(tithika_t('settings.location_fallback')) ?></small></div>
        <div class="tk-settings-actions">
          <button type="button" class="primary" id="tkSaveCurrentLocation"><?= htmlspecialchars(tithika_t('settings.save_location')) ?></button>
          <button type="button" id="tkClearSavedLocation"><?= htmlspecialchars(tithika_t('settings.clear')) ?></button>
        </div>
      </div>
    </article>
  </div>

  <div class="tk-settings-note">
    <div>◎</div>
    <div><b><?= htmlspecialchars(tithika_t('settings.future')) ?></b><p><?= htmlspecialchars(tithika_t('settings.future_copy')) ?></p></div>
  </div>
</section>
<?php tithika_render_footer(); ?>
