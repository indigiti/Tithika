<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/site.php';
tithika_render_header('Settings & Profile');
?>
<section class="tk-settings-hero">
  <div>
    <span class="tk-home-kicker">Local-first preferences</span>
    <h1>Make Tithika yours.</h1>
    <p>Choose your visual theme, time format, lunar-month convention, preferred tradition and default location. Settings stay in this browser; no account or database is required.</p>
  </div>
  <aside>
    <small>Privacy model</small>
    <strong>Stored locally.</strong>
    <p>Birth data is not stored here. Only explicit product preferences and an optional saved location are retained in browser storage.</p>
  </aside>
</section>

<section class="tk-settings-wrap" id="tkSettingsApp">
  <div class="tk-settings-grid">
    <article class="tk-settings-card">
      <header><span>Appearance</span><h2>Theme</h2></header>
      <div class="tk-settings-options" data-setting="theme">
        <button type="button" data-value="system"><b>System</b><small>Follow device appearance</small></button>
        <button type="button" data-value="light"><b>Light</b><small>Bright editorial interface</small></button>
        <button type="button" data-value="dark"><b>Dark</b><small>Low-light premium interface</small></button>
      </div>
    </article>
    <article class="tk-settings-card">
      <header><span>Time display</span><h2>Clock</h2></header>
      <div class="tk-settings-options" data-setting="clock">
        <button type="button" data-value="12"><b>12-hour</b><small>1:30 PM</small></button>
        <button type="button" data-value="24"><b>24-hour</b><small>13:30</small></button>
      </div>
    </article>
    <article class="tk-settings-card">
      <header><span>Lunar calendar</span><h2>Month convention</h2></header>
      <div class="tk-settings-options" data-setting="lunarMonth">
        <button type="button" data-value="amanta"><b>Amanta</b><small>Month ends at Amavasya</small></button>
        <button type="button" data-value="purnimanta"><b>Purnimanta</b><small>Month ends at Purnima</small></button>
      </div>
    </article>
    <article class="tk-settings-card">
      <header><span>Observance preference</span><h2>Tradition</h2></header>
      <div class="tk-settings-options" data-setting="tradition">
        <button type="button" data-value="smarta"><b>Smarta</b><small>General household convention</small></button>
        <button type="button" data-value="vaishnava"><b>Vaishnava</b><small>Vaishnava observance profile</small></button>
        <button type="button" data-value="iskcon"><b>ISKCON</b><small>ISKCON-compatible Ekadashi profile</small></button>
      </div>
    </article>
    <article class="tk-settings-card span-2">
      <header><span>Default context</span><h2>Saved location</h2></header>
      <div class="tk-settings-location">
        <div><b id="tkSettingsLocationName">No saved location</b><small id="tkSettingsLocationMeta">Tithika will continue using geolocation or the standard fallback.</small></div>
        <div class="tk-settings-actions">
          <button type="button" class="primary" id="tkSaveCurrentLocation">Save current selected location</button>
          <button type="button" id="tkClearSavedLocation">Clear</button>
        </div>
      </div>
    </article>
  </div>
  <div class="tk-settings-note">
    <div>◎</div>
    <div><b>Designed for future localization.</b><p>The settings schema reserves language/profile compatibility; full Hindi and regional UI localization will be a translation layer rather than duplicated pages.</p></div>
  </div>
</section>
<?php tithika_render_footer(); ?>
