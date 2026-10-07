<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/site.php';
$base = tithika_base_path();
$canonical = tithika_absolute_url(tithika_url('intelligence/'));
?>
<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="theme-color" content="#0b0b10">
  <title>Tithika Intelligence — Multi-engine Panchang, Muhurat & Jyotish</title>
  <meta name="description" content="Explainable multi-engine intelligence for Panchang, Muhurat and Jyotish, built on Tithika's verified deterministic calculation stack.">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="<?= htmlspecialchars($canonical) ?>">
  <link rel="stylesheet" href="<?= htmlspecialchars(tithika_asset_url('assets/intelligence.css')) ?>">
</head>
<body>
<a class="ti-skip" href="#workspace">Skip to Intelligence workspace</a>

<header class="ti-nav">
  <a class="ti-brand" href="<?= htmlspecialchars(tithika_url()) ?>" aria-label="Tithika home">
    <span class="ti-brand-mark">ति</span>
    <span><b>Tithika</b><small>Intelligence</small></span>
  </a>
  <nav aria-label="Intelligence sections">
    <button class="ti-nav-link is-active" data-view="ask">Ask</button>
    <button class="ti-nav-link" data-view="advisor">Advisor</button>
    <button class="ti-nav-link" data-view="jyotish">Jyotish</button>
    <button class="ti-nav-link" data-view="quality">Quality</button>
  </nav>
  <div class="ti-nav-actions">
    <span class="ti-status" id="tiSystemStatus"><i></i>Connecting</span>
    <button class="ti-icon-btn" id="tiTheme" type="button" aria-label="Toggle theme">◐</button>
  </div>
</header>

<main>
  <section class="ti-hero">
    <div class="ti-aurora ti-aurora-one"></div>
    <div class="ti-aurora ti-aurora-two"></div>
    <div class="ti-hero-grid"></div>
    <div class="ti-hero-copy">
      <span class="ti-eyebrow">Verified engines · explainable synthesis · private by default</span>
      <h1>Intelligence,<br><em>with provenance.</em></h1>
      <p>Ask Tithika to combine Panchang, Muhurat and Jyotish layers without turning deterministic calculations into a black box.</p>
      <div class="ti-command">
        <div class="ti-command-icon">✦</div>
        <textarea id="tiQuestion" rows="1" placeholder="Ask: What are the best traditional timing windows today?"></textarea>
        <button id="tiAsk" type="button"><span>Ask Tithika</span><b>↗</b></button>
      </div>
      <div class="ti-prompts" aria-label="Suggested questions">
        <button data-prompt="What are the best traditional timing windows today?">Best time today</button>
        <button data-prompt="Find a good vehicle purchase Muhurat this week.">Vehicle Muhurat</button>
        <button data-prompt="Explain my Kundali using Shadbala, D9, Yogas and Dasha.">Explain my chart</button>
        <button data-prompt="Check today's Panchang and Choghadiya for inconsistencies.">Audit today</button>
      </div>
    </div>
    <aside class="ti-hero-card">
      <div class="ti-orbit">
        <div class="ti-orbit-core"><span>6</span><small>layers</small></div>
        <i class="o1">P</i><i class="o2">M</i><i class="o3">J</i><i class="o4">Q</i>
      </div>
      <div class="ti-hero-card-copy">
        <small>Multi-engine architecture</small>
        <strong>Facts first.<br>Interpretation second.</strong>
        <p>Every answer carries confidence, engine versions and source category.</p>
      </div>
    </aside>
  </section>

  <section class="ti-context-shell" aria-label="Calculation context">
    <div class="ti-context">
      <label><span>Location</span><input id="tiCity" type="search" autocomplete="off" value="Pune, Maharashtra, India"><div id="tiPlaces" class="ti-places" hidden></div></label>
      <button class="ti-locate" id="tiLocate" type="button" aria-label="Use current location">⌖</button>
      <label><span>Date</span><input id="tiDate" type="date"></label>
      <label><span>Birth time</span><input id="tiTime" type="time" value="12:00"></label>
      <label><span>Purpose</span>
        <select id="tiPurpose">
          <option value="general">General timing</option>
          <option value="vehicle">Vehicle purchase</option>
          <option value="property">Property purchase</option>
          <option value="griha-pravesh">Griha Pravesh</option>
          <option value="vivah">Vivah</option>
          <option value="namakarana">Namakarana</option>
        </select>
      </label>
      <label><span>Range</span><select id="tiRange"><option value="today">Today</option><option value="week">7 days</option></select></label>
    </div>
  </section>

  <section class="ti-workspace" id="workspace">
    <aside class="ti-sidebar">
      <div class="ti-side-head"><small>Intelligence stack</small><span id="tiEngineCount">— engines</span></div>
      <button class="ti-layer is-active" data-view="ask"><i>01</i><span><b>Conversation</b><small>Natural-language routing</small></span><em>↗</em></button>
      <button class="ti-layer" data-view="advisor"><i>02</i><span><b>Timing Advisor</b><small>Panchang + Muhurat</small></span><em>↗</em></button>
      <button class="ti-layer" data-view="jyotish"><i>03</i><span><b>Jyotish Fusion</b><small>Six calculation systems</small></span><em>↗</em></button>
      <button class="ti-layer" data-view="profile"><i>04</i><span><b>Profile Engine</b><small>Preference-aware ranking</small></span><em>↗</em></button>
      <button class="ti-layer" data-view="quality"><i>05</i><span><b>Quality AI</b><small>Cross-engine checks</small></span><em>↗</em></button>
      <div class="ti-privacy">
        <div>◈</div><span><b>Private by default</b><small>Personal birth/profile requests are not persistently cached.</small></span>
      </div>
    </aside>

    <div class="ti-stage">
      <div class="ti-stage-head">
        <div><span id="tiStageKicker">Conversational Tithika</span><h2 id="tiStageTitle">Ask across the whole stack.</h2></div>
        <div class="ti-stage-actions">
          <button id="tiRunCurrent" type="button">Run intelligence <span>→</span></button>
        </div>
      </div>

      <div class="ti-empty" id="tiEmpty">
        <div class="ti-empty-glyph">✦</div>
        <h3>One question. Multiple verified engines.</h3>
        <p>Tithika will route your request, expose the calculation sources and separate calculated facts from traditional interpretation.</p>
        <div class="ti-capabilities">
          <span>Panchang</span><span>Choghadiya</span><span>Muhurat</span><span>Kundali</span><span>Shadbala</span><span>Vargas</span><span>Yogas</span><span>Dasha</span><span>Transits</span>
        </div>
      </div>

      <div class="ti-loading" id="tiLoading" hidden>
        <div class="ti-loader"><i></i><i></i><i></i></div>
        <div><b>Orchestrating verified engines</b><span id="tiLoadingText">Building an explainable answer…</span></div>
      </div>

      <div class="ti-result" id="tiResult" hidden></div>
    </div>

    <aside class="ti-inspector">
      <div class="ti-inspector-head"><span>Evidence</span><b id="tiConfidence">—</b></div>
      <div class="ti-meter"><i id="tiConfidenceBar"></i></div>
      <div id="tiProvenance" class="ti-provenance">
        <p>Run an intelligence request to see engine-level provenance and confidence here.</p>
      </div>
      <div class="ti-boundary">
        <small>System boundary</small>
        <p>AI may explain and rank verified results. It does not invent astronomical positions or sacred-calendar timestamps.</p>
      </div>
    </aside>
  </section>

  <section class="ti-editorial">
    <div><span>Architecture</span><h2>Six layers.<br>One evidence contract.</h2></div>
    <div class="ti-editorial-grid">
      <article><small>01</small><h3>Intelligence Core</h3><p>Engine registry, confidence, provenance, cache policy and synthesis-provider routing.</p></article>
      <article><small>02</small><h3>Timing Advisor</h3><p>Ranks Choghadiya, Panchang Muhurtas and purpose-specific rule profiles.</p></article>
      <article><small>03</small><h3>Jyotish Fusion</h3><p>Kundali, Shadbala, D9, Yogas, Vimshottari and current planetary state.</p></article>
      <article><small>04</small><h3>Conversation</h3><p>Intent routing across the stack with structured answers and required-input awareness.</p></article>
      <article><small>05</small><h3>Profile Engine</h3><p>Personal preference ranking after calculation, never before it.</p></article>
      <article><small>06</small><h3>Quality AI</h3><p>Cross-engine invariants, drift detection and fail-closed structural checks.</p></article>
    </div>
  </section>
</main>

<footer class="ti-footer"><span>Tithika Intelligence</span><p>Traditional Panchang and Jyotish interpretations are cultural/astrological systems, not scientific predictions or professional advice.</p><a href="<?= htmlspecialchars(tithika_url()) ?>">Return to Tithika →</a></footer>

<script>window.TITHIKA_BASE = <?= json_encode($base, JSON_UNESCAPED_SLASHES) ?>;</script>
<script src="<?= htmlspecialchars(tithika_asset_url('assets/intelligence.js')) ?>" defer></script>
</body>
</html>
