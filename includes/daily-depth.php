<?php
/**
 * Calculated daily Panchang overview. Values are populated exclusively from
 * existing Tithika APIs; these are not DrikPanchang screenshots or sample dates.
 */
declare(strict_types=1);
?>
<section class="tk-daily-depth" id="tkDailyDepth" aria-labelledby="tkDepthTitle">
  <div class="tk-depth-heading">
    <div>
      <span class="tk-depth-eyebrow">Detailed daily Panchang · Lahiri</span>
      <h2 id="tkDepthTitle">Your complete local Hindu day</h2>
      <p id="tkDepthContext" aria-live="polite">Calculating the selected sunrise-to-sunrise day…</p>
    </div>
    <span class="tk-depth-source">Calculated, not example data</span>
  </div>

  <section class="tk-depth-panel" aria-labelledby="tkDepthTimelineHeading">
    <div class="tk-depth-panel-head">
      <div><span class="tk-depth-eyebrow">Astronomical transitions</span><h3 id="tkDepthTimelineHeading">Panchang timeline</h3></div>
      <span id="tkDepthDaySpan" class="tk-depth-subtle">Local sunrise → next sunrise</span>
    </div>
    <div class="tk-depth-ruler" id="tkDepthRuler" aria-label="Sunrise, sunset and next sunrise times"></div>
    <div class="tk-depth-tracks" id="tkDepthTracks" aria-live="polite">
      <p class="tk-depth-muted">Waiting for Tithi, Nakshatra, Yoga and Karana transitions…</p>
    </div>
    <p class="tk-depth-explain">Lengths are proportional to actual elapsed time. Hover or focus on a segment to inspect its local start and end; dates cross midnight where applicable.</p>
  </section>

  <div class="tk-depth-cards">
    <section class="tk-depth-card" aria-labelledby="tkDepthAtGlanceTitle">
      <div class="tk-depth-card-head"><span aria-hidden="true">☼</span><h3 id="tkDepthAtGlanceTitle">Panchang at sunrise</h3></div>
      <dl id="tkDepthSummary" class="tk-depth-definition"><div><dt>Selected day</dt><dd>Calculating…</dd></div></dl>
      <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/sankalpa')) ?>">Sankalpa, seasons &amp; Samvat →</a>
    </section>
    <section class="tk-depth-card" aria-labelledby="tkDepthFestivalsTitle">
      <div class="tk-depth-card-head"><span aria-hidden="true">✿</span><h3 id="tkDepthFestivalsTitle">Upcoming observances</h3></div>
      <div id="tkDepthObservances" class="tk-depth-feed" aria-live="polite">Loading verified upcoming observances…</div>
      <a href="<?= htmlspecialchars(tithika_pretty_url('festivals/hindu')) ?>">Explore festival calendars →</a>
    </section>
    <section class="tk-depth-card" aria-labelledby="tkDepthPlanetsTitle">
      <div class="tk-depth-card-head"><span aria-hidden="true">☿</span><h3 id="tkDepthPlanetsTitle">Planetary events</h3></div>
      <div id="tkDepthPlanets" class="tk-depth-feed" aria-live="polite">Loading recorded planetary ingress and station events…</div>
      <a href="<?= htmlspecialchars(tithika_pretty_url('planets/transit')) ?>">All planetary transits →</a>
    </section>
    <section class="tk-depth-card" aria-labelledby="tkDepthRashifalTitle">
      <div class="tk-depth-card-head"><span aria-hidden="true">✧</span><h3 id="tkDepthRashifalTitle">Rashifal &amp; Moon sign</h3></div>
      <p>Moon Rashi at sunrise: <strong id="tkDepthMoonSign">—</strong></p>
      <p class="tk-depth-muted">Personalized interpretation needs birth date, exact time and place. Tithika does not invent twelve generic predictions as astronomical facts.</p>
      <a href="<?= htmlspecialchars(tithika_pretty_url('jyotish/rashifal/daily')) ?>">Open personalized daily Rashifal →</a>
    </section>
    <section class="tk-depth-card" aria-labelledby="tkDepthVedicTitle">
      <div class="tk-depth-card-head"><span aria-hidden="true">⌛</span><h3 id="tkDepthVedicTitle">Vedic time</h3></div>
      <div class="tk-depth-switch" role="group" aria-label="Vedic time scale">
        <button type="button" data-depth-clock="60" aria-pressed="true">60 Ghati</button>
        <button type="button" data-depth-clock="30" aria-pressed="false">30 + 30 Ghati</button>
      </div>
      <div class="tk-depth-clock" id="tkDepthClock" aria-live="off">—:—:—</div>
      <p id="tkDepthClockLabel" class="tk-depth-muted">Ghati : Pal : Vipal · local Hindu day</p>
      <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/vedic-clock')) ?>">Full Vedic clock &amp; method →</a>
    </section>
    <section class="tk-depth-card" aria-labelledby="tkDepthLagnaTitle">
      <div class="tk-depth-card-head"><span aria-hidden="true">◇</span><h3 id="tkDepthLagnaTitle">Lagna &amp; Graha positions</h3></div>
      <p class="tk-depth-muted">Sidereal chart for a selected local time (not a birth chart).</p>
      <label class="tk-depth-time-label" for="tkDepthChartTime">Chart time <input type="time" id="tkDepthChartTime" value="12:00"></label>
      <button type="button" class="tk-depth-action" id="tkDepthLoadChart">Calculate chart</button>
      <div id="tkDepthChart" class="tk-depth-chart" aria-live="polite"></div>
      <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/lagna-kundali')) ?>">Detailed Lagna chart →</a>
    </section>
  </div>

  <section class="tk-depth-panel" aria-labelledby="tkDepthTimingTitle">
    <div class="tk-depth-panel-head">
      <div><span class="tk-depth-eyebrow">Calculation-backed intervals</span><h3 id="tkDepthTimingTitle">Auspicious and caution timings</h3></div>
      <a href="<?= htmlspecialchars(tithika_pretty_url('muhurat/choghadiya')) ?>">Full Choghadiya →</a>
    </div>
    <div class="tk-depth-timing-grid" id="tkDepthTiming">
      <p class="tk-depth-muted">Waiting for local sunrise-derived Muhurat intervals…</p>
    </div>
    <p class="tk-depth-explain">Conventions differ between schools and regions. A calculated Muhurat interval is not a personalized recommendation.</p>
  </section>

  <section class="tk-depth-panel" aria-labelledby="tkDepthAdvancedTitle">
    <div class="tk-depth-panel-head">
      <div><span class="tk-depth-eyebrow">More verified tools</span><h3 id="tkDepthAdvancedTitle">Traditional calendar details</h3></div>
      <span class="tk-depth-subtle">Calculation and tradition profiles kept separate</span>
    </div>
    <div class="tk-depth-tools">
      <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/sankalpa')) ?>"><strong>Samvat, Ritu &amp; Ayana</strong><span>Vikram, Shaka, seasonal and lunar contexts</span></a>
      <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/chandrabalam')) ?>"><strong>Chandrabalam</strong><span>Evaluate using Janma Rashi</span></a>
      <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/tarabalam')) ?>"><strong>Tarabalam</strong><span>Evaluate using Janma Nakshatra</span></a>
      <a href="<?= htmlspecialchars(tithika_pretty_url('muhurat/panchaka-rahita')) ?>"><strong>Panchaka Rahita</strong><span>Rule-based Lagna and timing boundaries</span></a>
      <a href="<?= htmlspecialchars(tithika_pretty_url('muhurat/lagna')) ?>"><strong>Udaya Lagna</strong><span>Local sign-rise transitions</span></a>
      <a href="<?= htmlspecialchars(tithika_pretty_url('panchang/panchak')) ?>"><strong>Panchak and Bhadra</strong><span>Evidence-backed caution intervals</span></a>
    </div>
  </section>
</section>
<script src="<?= htmlspecialchars(tithika_asset_url('assets/daily-depth.js')) ?>" defer></script>