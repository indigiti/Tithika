<!doctype html>
<html lang="en" class="h-full">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
  <meta name="theme-color" content="#1f1638" />
  <title>Choghadiya — Tithika</title>
  <meta name="description" content="Location-aware Choghadiya with local sunrise, sunset, Rahu Kaal and live Muhurat timings." />
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config={theme:{extend:{fontFamily:{sans:['Inter','ui-sans-serif','system-ui','sans-serif']},boxShadow:{card:'0 18px 55px rgba(45,32,20,.08)',float:'0 22px 70px rgba(38,24,63,.18)'}}}}
  </script>
  <style>
    :root{color-scheme:light;--ink:#20182f;--paper:#f7f3ec;--saffron:#f08a24;--violet:#211836}
    *{box-sizing:border-box}
    html{background:var(--paper)}
    body{background:
      radial-gradient(circle at 8% -5%,rgba(244,183,91,.28),transparent 27rem),
      radial-gradient(circle at 100% 0%,rgba(149,126,197,.16),transparent 30rem),
      var(--paper)}
    .surface{background:rgba(255,255,255,.82);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)}
    .hero-grid{background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:28px 28px}
    .quality-best,.quality-good,.quality-gain{--q:#16724b;--qt:#0f6240;--qb:#eaf7ef;--qd:#bfe9cf}
    .quality-neutral{--q:#526174;--qt:#445063;--qb:#eef2f5;--qd:#d8e0e6}
    .quality-avoid{--q:#b44635;--qt:#983828;--qb:#fff0ec;--qd:#f4c9bf}
    .period-row{border-color:#ece7df;transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease,background .18s ease}
    .period-row:hover{transform:translateY(-1px);box-shadow:0 12px 28px rgba(45,32,20,.07);border-color:var(--qd)}
    .period-dot{background:var(--qb);color:var(--q);border:1px solid var(--qd)}
    .period-pill{background:var(--qb);color:var(--qt)}
    .active-ring{border-color:#f5a14d!important;background:linear-gradient(90deg,#fff9f1,#fff)!important;box-shadow:0 14px 34px rgba(240,138,36,.13)}
    .active-ring .period-dot{box-shadow:0 0 0 4px rgba(240,138,36,.10)}
    .hide-scroll::-webkit-scrollbar{display:none}.hide-scroll{scrollbar-width:none}
    .progress-track{background:rgba(255,255,255,.12)}
    .progress-fill{width:var(--progress,0%);transition:width .5s linear}
    .shine:before{content:"";position:absolute;inset:-1px;border-radius:inherit;padding:1px;background:linear-gradient(135deg,rgba(255,255,255,.75),rgba(255,255,255,.08),rgba(255,255,255,.35));-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;pointer-events:none}
    .segmented button[aria-selected="true"]{background:#211836;color:#fff;box-shadow:0 8px 24px rgba(33,24,54,.18)}
    @media (max-width: 767px){.schedule-panel[data-mobile-hidden="true"]{display:none}}
  </style>
</head>
<body class="min-h-full text-[#20182f] antialiased selection:bg-orange-200/70">
  <a href="index.php" class="fixed left-4 top-4 z-[60] rounded-full border border-white/70 bg-white/90 px-3 py-2 text-xs font-black text-[#211836] shadow-lg backdrop-blur hover:bg-white">← Tithika Home</a>
  <main class="mx-auto max-w-[1440px] px-3 pb-10 pt-3 sm:px-5 sm:pt-5 lg:px-8 lg:pt-7">

    <header class="mb-4 flex items-center justify-between gap-3 px-1 sm:mb-5">
      <div class="flex min-w-0 items-center gap-3">
        <div class="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-[#211836] text-xl text-white shadow-lg shadow-violet-950/10">☀</div>
        <div class="min-w-0">
          <div class="flex items-center gap-2"><h1 class="truncate text-lg font-black tracking-[-.03em] sm:text-xl">Choghadiya</h1><span class="hidden rounded-full bg-orange-100 px-2 py-1 text-[10px] font-black uppercase tracking-[.12em] text-orange-700 sm:inline">Live</span></div>
          <p class="truncate text-xs font-medium text-stone-500">Location-aware Muhurat timings</p>
        </div>
      </div>
      <button id="headerLocateBtn" class="group flex max-w-[52%] items-center gap-2 rounded-full border border-white/80 bg-white/70 px-3 py-2 shadow-sm backdrop-blur hover:bg-white sm:max-w-none">
        <span class="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-orange-100 text-orange-700">⌖</span>
        <span id="headerLocation" class="truncate text-left text-xs font-bold text-stone-700 sm:max-w-[260px]">Finding your location…</span>
      </button>
    </header>

    <section class="grid gap-4 xl:grid-cols-[1.42fr_.88fr]">
      <article class="hero-grid shine relative overflow-hidden rounded-[2rem] bg-[#211836] p-5 text-white shadow-float sm:p-7 lg:min-h-[360px] lg:p-8">
        <div class="absolute -right-16 -top-20 h-64 w-64 rounded-full bg-orange-400/20 blur-3xl"></div>
        <div class="absolute -bottom-24 left-1/3 h-64 w-64 rounded-full bg-fuchsia-500/10 blur-3xl"></div>
        <div class="relative flex h-full flex-col justify-between gap-8">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span id="currentQuality" class="rounded-full bg-white/10 px-3 py-1.5 text-[11px] font-black uppercase tracking-[.12em] text-orange-200">Live schedule</span>
                <span id="activeSide" class="rounded-full border border-white/10 px-3 py-1.5 text-[11px] font-bold text-white/65">Today</span>
              </div>
              <p id="currentEyebrow" class="mt-5 text-xs font-bold uppercase tracking-[.22em] text-white/45">Current Choghadiya</p>
              <div id="currentName" class="mt-1 text-[2.75rem] font-black leading-none tracking-[-.055em] sm:text-6xl">Locating…</div>
              <p id="currentRange" class="mt-3 text-sm font-semibold text-white/65 sm:text-base">Preparing your local timings</p>
            </div>
            <div class="hidden h-16 w-16 shrink-0 place-items-center rounded-full border border-white/10 bg-white/[.05] text-3xl sm:grid">ॐ</div>
          </div>

          <div>
            <div class="mb-2 flex items-center justify-between gap-3 text-[11px] font-bold uppercase tracking-[.12em] text-white/45">
              <span>Period progress</span><span id="progressText">—</span>
            </div>
            <div class="progress-track h-2 overflow-hidden rounded-full"><div id="currentProgress" class="progress-fill h-full rounded-full bg-gradient-to-r from-orange-400 to-amber-200" style="--progress:0%"></div></div>
            <div class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div class="rounded-2xl border border-white/[.07] bg-white/[.055] p-3.5"><div class="text-[10px] font-bold uppercase tracking-[.14em] text-white/40">Local time</div><div id="liveClock" class="mt-1.5 text-lg font-black tabular-nums">--:--:--</div></div>
              <div class="rounded-2xl border border-white/[.07] bg-white/[.055] p-3.5"><div class="text-[10px] font-bold uppercase tracking-[.14em] text-white/40">Changes in</div><div id="countdown" class="mt-1.5 text-lg font-black tabular-nums text-orange-200">--:--:--</div></div>
              <div class="rounded-2xl border border-white/[.07] bg-white/[.055] p-3.5"><div class="text-[10px] font-bold uppercase tracking-[.14em] text-white/40">Sunrise</div><div id="sunriseHero" class="mt-1.5 text-lg font-black">--</div></div>
              <div class="rounded-2xl border border-white/[.07] bg-white/[.055] p-3.5"><div class="text-[10px] font-bold uppercase tracking-[.14em] text-white/40">Sunset</div><div id="sunsetHero" class="mt-1.5 text-lg font-black">--</div></div>
            </div>
          </div>
        </div>
      </article>

      <aside class="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
        <div class="surface rounded-[2rem] border border-white/90 p-5 shadow-card sm:p-6">
          <div class="flex items-start justify-between gap-3">
            <div><p class="text-[10px] font-black uppercase tracking-[.18em] text-orange-600">Selected day</p><h2 id="selectedDateTitle" class="mt-1 text-2xl font-black tracking-[-.035em]">Today</h2><p id="locationMini" class="mt-1.5 max-w-sm truncate text-xs font-medium text-stone-500">Detecting location…</p></div>
            <button id="calendarTodayBtn" class="rounded-2xl bg-[#f3ede5] px-3 py-2 text-xs font-black text-stone-700 hover:bg-orange-100">Today</button>
          </div>
          <div class="mt-5 grid grid-cols-2 gap-2.5">
            <div class="rounded-2xl bg-amber-50 p-4"><div class="flex items-center justify-between"><span class="text-lg">☀️</span><span class="text-[10px] font-black uppercase tracking-[.12em] text-amber-700">Sunrise</span></div><div id="sunrise" class="mt-3 text-xl font-black">--</div><div id="dayLength" class="mt-1 text-[11px] font-semibold text-amber-700/70">Daylight —</div></div>
            <div class="rounded-2xl bg-indigo-50 p-4"><div class="flex items-center justify-between"><span class="text-lg">🌙</span><span class="text-[10px] font-black uppercase tracking-[.12em] text-indigo-700">Sunset</span></div><div id="sunset" class="mt-3 text-xl font-black">--</div><div id="nightLength" class="mt-1 text-[11px] font-semibold text-indigo-700/70">Night —</div></div>
          </div>
        </div>

        <div class="surface rounded-[2rem] border border-white/90 p-5 shadow-card sm:p-6">
          <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
            <div class="rounded-2xl border border-rose-100 bg-rose-50/70 p-4">
              <div class="flex items-center gap-2 text-[10px] font-black uppercase tracking-[.15em] text-rose-600"><span>☊</span> Rahu Kaal</div>
              <div id="rahu" class="mt-2 text-sm font-black text-rose-950">--</div>
              <p class="mt-1 text-[11px] font-medium leading-4 text-rose-700/60">Traditionally avoided for new beginnings.</p>
            </div>
            <div class="rounded-2xl border border-emerald-100 bg-emerald-50/70 p-4">
              <div class="flex items-center gap-2 text-[10px] font-black uppercase tracking-[.15em] text-emerald-700"><span>✦</span> Next auspicious</div>
              <div id="nextGood" class="mt-2 text-sm font-black text-emerald-950">--</div>
              <p id="nextGoodSub" class="mt-1 text-[11px] font-medium leading-4 text-emerald-700/60">Finding your next favourable window.</p>
            </div>
          </div>
        </div>
      </aside>
    </section>

    <section class="surface sticky top-2 z-20 mt-4 rounded-[1.65rem] border border-white/90 p-3 shadow-card sm:p-4">
      <div class="grid gap-3 lg:grid-cols-[1.35fr_.68fr_auto_auto] lg:items-end">
        <div class="relative">
          <label class="mb-1.5 block px-1 text-[10px] font-black uppercase tracking-[.14em] text-stone-400">Location</label>
          <div class="flex gap-2">
            <div class="relative min-w-0 flex-1">
              <div class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400">⌕</div>
              <input id="citySearch" autocomplete="off" class="w-full rounded-2xl border border-stone-200 bg-white py-3 pl-10 pr-4 text-sm font-bold text-stone-800 outline-none ring-orange-100 transition placeholder:font-medium placeholder:text-stone-400 focus:border-orange-300 focus:ring-4" placeholder="Search city or place…" />
              <div id="searchResults" class="absolute z-40 mt-2 hidden max-h-80 w-full overflow-auto rounded-2xl border border-stone-200 bg-white p-1.5 shadow-2xl"></div>
            </div>
            <button id="locateBtn" title="Use my current location" class="grid h-[46px] w-[46px] shrink-0 place-items-center rounded-2xl bg-[#211836] text-lg text-white shadow-lg shadow-violet-950/10 hover:-translate-y-px">⌖</button>
          </div>
        </div>
        <div>
          <label class="mb-1.5 block px-1 text-[10px] font-black uppercase tracking-[.14em] text-stone-400">Date</label>
          <input id="dateInput" type="date" class="w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm font-bold text-stone-800 outline-none ring-orange-100 transition focus:border-orange-300 focus:ring-4" />
        </div>
        <div class="flex gap-2 lg:pb-0">
          <button data-shift="-1" class="navBtn grid h-[46px] w-[46px] place-items-center rounded-2xl border border-stone-200 bg-white text-lg font-black text-stone-600 hover:bg-stone-50" aria-label="Previous day">‹</button>
          <button data-shift="1" class="navBtn grid h-[46px] w-[46px] place-items-center rounded-2xl border border-stone-200 bg-white text-lg font-black text-stone-600 hover:bg-stone-50" aria-label="Next day">›</button>
        </div>
        <button id="formatBtn" class="h-[46px] rounded-2xl bg-[#f3ede5] px-4 text-xs font-black text-stone-700 hover:bg-stone-200">12 hour</button>
      </div>
      <div class="mt-2 flex items-center justify-between gap-3 px-1"><span id="coords" class="truncate text-[10px] font-medium text-stone-400"></span><span id="locationStatus" class="shrink-0 text-[10px] font-bold text-emerald-700">● Auto location ready</span></div>
    </section>

    <section class="mt-5">
      <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div><p class="text-[10px] font-black uppercase tracking-[.18em] text-orange-600">Daily timeline</p><h2 class="mt-1 text-2xl font-black tracking-[-.035em] sm:text-3xl">Choghadiya periods</h2><p class="mt-1 text-sm font-medium text-stone-500">Eight solar periods for the day and eight for the night.</p></div>
        <div class="segmented flex rounded-2xl bg-white/75 p-1 shadow-sm md:hidden">
          <button id="dayTab" aria-selected="true" class="flex-1 rounded-xl px-5 py-2.5 text-xs font-black text-stone-500">☀ Day</button>
          <button id="nightTab" aria-selected="false" class="flex-1 rounded-xl px-5 py-2.5 text-xs font-black text-stone-500">☾ Night</button>
        </div>
      </div>

      <div class="grid gap-4 md:grid-cols-2">
        <article id="dayPanel" class="schedule-panel surface rounded-[2rem] border border-white/90 p-3 shadow-card sm:p-4">
          <div class="flex items-center justify-between gap-3 px-2 pb-3 pt-1">
            <div class="flex items-center gap-3"><span class="grid h-10 w-10 place-items-center rounded-2xl bg-amber-100 text-lg">☀</span><div><p class="text-[10px] font-black uppercase tracking-[.15em] text-amber-700">Day Choghadiya</p><h3 id="dayHeading" class="mt-0.5 text-base font-black">Sunrise → Sunset</h3></div></div>
            <span id="dayPeriodMeta" class="rounded-full bg-amber-50 px-3 py-1.5 text-[10px] font-black text-amber-700">8 periods</span>
          </div>
          <div id="dayList" class="space-y-2"></div>
        </article>

        <article id="nightPanel" data-mobile-hidden="true" class="schedule-panel surface rounded-[2rem] border border-white/90 p-3 shadow-card sm:p-4">
          <div class="flex items-center justify-between gap-3 px-2 pb-3 pt-1">
            <div class="flex items-center gap-3"><span class="grid h-10 w-10 place-items-center rounded-2xl bg-indigo-100 text-lg">☾</span><div><p class="text-[10px] font-black uppercase tracking-[.15em] text-indigo-700">Night Choghadiya</p><h3 id="nightHeading" class="mt-0.5 text-base font-black">Sunset → Next sunrise</h3></div></div>
            <span id="nightPeriodMeta" class="rounded-full bg-indigo-50 px-3 py-1.5 text-[10px] font-black text-indigo-700">8 periods</span>
          </div>
          <div id="nightList" class="space-y-2"></div>
        </article>
      </div>
    </section>

    <section class="mt-5 grid gap-4 lg:grid-cols-[1.3fr_.7fr]">
      <div class="rounded-[2rem] bg-gradient-to-br from-orange-100 via-amber-50 to-white p-5 shadow-card sm:p-6">
        <div class="flex items-start justify-between gap-4"><div><p class="text-[10px] font-black uppercase tracking-[.18em] text-orange-700">Reading the colours</p><h3 class="mt-1.5 text-lg font-black">Faster at-a-glance decisions</h3><p class="mt-2 max-w-2xl text-sm font-medium leading-6 text-stone-600">Amrit, Shubh and Labh are shown in green; Chara is neutral; Rog, Kaal and Udveg are highlighted as avoid periods. The active period gets a saffron outline.</p></div><span class="hidden text-3xl sm:block">✦</span></div>
      </div>
      <div class="surface rounded-[2rem] border border-white/90 p-5 shadow-card sm:p-6"><p class="text-[10px] font-black uppercase tracking-[.18em] text-stone-400">Legend</p><div class="mt-4 flex flex-wrap gap-2 text-xs font-black"><span class="rounded-full bg-emerald-100 px-3 py-2 text-emerald-800">● Auspicious</span><span class="rounded-full bg-slate-100 px-3 py-2 text-slate-700">● Neutral</span><span class="rounded-full bg-rose-100 px-3 py-2 text-rose-800">● Avoid</span></div></div>
    </section>

    <footer class="px-3 py-8 text-center text-[11px] font-medium leading-5 text-stone-400">Traditional Panchang timing utility. Choghadiya and Rahu Kaal are cultural/astrological conventions, not scientific predictions. Location permission is used only to calculate local solar timings.</footer>
  </main>

  <div id="toast" class="pointer-events-none fixed bottom-[max(1rem,env(safe-area-inset-bottom))] left-1/2 z-50 hidden max-w-[calc(100%-2rem)] -translate-x-1/2 rounded-2xl bg-[#211836] px-4 py-3 text-center text-sm font-bold text-white shadow-2xl"></div>
  <script src="assets/app.js?v=2"></script>
</body>
</html>
