<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
  <meta name="theme-color" content="#f7f8fc" />
  <title>Tithika — Modern Panchang & Muhurat</title>
  <meta name="description" content="A modern location-aware Panchang experience for Choghadiya, Muhurat, sunrise, sunset, Rahu Kaal, festivals and Vedic calendar utilities." />
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config={theme:{extend:{
      fontFamily:{sans:['Inter','ui-sans-serif','system-ui','sans-serif']},
      boxShadow:{soft:'0 20px 70px rgba(40,55,90,.10)',lift:'0 24px 80px rgba(48,47,91,.16)'}
    }}}
  </script>
  <style>
    :root{--ink:#17213a;--muted:#6e7890;--line:#e8ecf3;--blue:#5faaf6;--violet:#826bef;--pink:#d56eea;--orange:#ffaf68;--green:#68bf79}
    *{box-sizing:border-box}
    html{scroll-behavior:smooth}
    body{background:#eef1f6;color:var(--ink)}
    .shell{background:rgba(255,255,255,.94);box-shadow:0 30px 100px rgba(65,78,105,.15)}
    .glass{background:rgba(255,255,255,.72);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px)}
    .hero-grid{background-image:linear-gradient(rgba(99,112,145,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(99,112,145,.055) 1px,transparent 1px);background-size:70px 70px}
    .soft-border{border:1px solid rgba(225,230,240,.9)}
    .orb{filter:blur(0);box-shadow:inset 0 1px 1px rgba(255,255,255,.85),0 18px 55px rgba(102,104,208,.18)}
    .spectrum{background:linear-gradient(105deg,#79baff 0%,#8da7f5 28%,#aa87ef 50%,#d77be9 72%,#ffac7e 100%)}
    .spectrum-soft{background:linear-gradient(120deg,rgba(116,185,255,.16),rgba(147,137,241,.15),rgba(220,122,235,.13),rgba(255,178,114,.12))}
    .pixel{
      width:68px;height:68px;border-radius:18px;
      background:linear-gradient(145deg,rgba(255,255,255,.92),rgba(255,255,255,.20));
      box-shadow:inset 0 0 18px rgba(255,255,255,.65),0 10px 26px rgba(91,106,160,.08)
    }
    .pixel.blue{background:linear-gradient(145deg,#bfe1ff,#72b3f9)}
    .pixel.violet{background:linear-gradient(145deg,#c8bafa,#9678ef)}
    .pixel.pink{background:linear-gradient(145deg,#efc4f8,#d974e9)}
    .pixel.orange{background:linear-gradient(145deg,#ffd6b3,#ffae73)}
    .tool-card{transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
    .tool-card:hover{transform:translateY(-4px);box-shadow:0 22px 60px rgba(44,61,96,.12);border-color:#dfe4ef}
    .time-seg{position:relative;min-width:112px;flex:1;border-radius:18px;padding:14px 12px;border:1px solid var(--line);background:#fff}
    .time-seg.good{background:#effaf2;border-color:#d9efdf}.time-seg.good .seg-name{color:#257344}
    .time-seg.neutral{background:#f5f7fa}.time-seg.neutral .seg-name{color:#516079}
    .time-seg.avoid{background:#fff3f0;border-color:#f4ddd8}.time-seg.avoid .seg-name{color:#aa4939}
    .time-seg.is-active{box-shadow:0 0 0 3px #fff,0 0 0 5px #7c73ed}
    .seg-name{display:block;font-size:12px;font-weight:900}.seg-time{display:block;margin-top:8px;font-size:10px;font-weight:700;color:#8891a4}
    .chip{border:1px solid #e4e8ef;background:#fff}
    .utility-icon{box-shadow:inset 0 1px 0 rgba(255,255,255,.7),0 10px 24px rgba(52,65,98,.08)}
    .place-result{display:block;width:100%;text-align:left;padding:12px 14px;border-radius:14px;transition:background .15s}
    .place-result:hover{background:#f4f7fb}.place-result strong{display:block;font-size:13px}.place-result span{display:block;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:10px;color:#8b94a6}
    @media (max-width:1023px){#locationPanel{position:fixed!important;left:12px!important;right:12px!important;top:auto!important;bottom:86px!important;width:auto!important}}
    @media (max-width:640px){
      body{background:#fff}.shell{border-radius:0!important;box-shadow:none}.pixel{width:48px;height:48px;border-radius:14px}
      .hero-grid{background-size:44px 44px}
    }
  </style>
</head>
<body class="min-h-screen antialiased selection:bg-violet-200/60">
  <div class="mx-auto min-h-screen max-w-[1540px] p-0 sm:p-4 lg:p-7">
    <div class="shell relative min-h-screen overflow-hidden rounded-none sm:rounded-[2.2rem]">
      <header class="relative z-30 flex items-center justify-between gap-4 px-5 py-5 sm:px-8 lg:px-12">
        <a href="index.php" class="flex items-center gap-3">
          <span class="orb grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-sky-400 via-violet-500 to-pink-400 text-xl font-black text-white">ति</span>
          <div>
            <div class="text-lg font-black tracking-[-.035em]">Tithika</div>
            <div class="-mt-0.5 text-[9px] font-bold uppercase tracking-[.18em] text-slate-400">Vedic time, reimagined</div>
          </div>
        </a>

        <nav class="hidden items-center gap-1 rounded-full border border-slate-200/80 bg-white/75 p-1.5 shadow-sm backdrop-blur lg:flex">
          <a href="#today" class="rounded-full px-4 py-2 text-xs font-bold text-slate-700 hover:bg-slate-100">Today</a>
          <a href="choghadiya.php" class="rounded-full px-4 py-2 text-xs font-bold text-slate-700 hover:bg-slate-100">Choghadiya</a>
          <a href="#utilities" class="rounded-full px-4 py-2 text-xs font-bold text-slate-700 hover:bg-slate-100">Utilities</a>
          <a href="#explore" class="rounded-full px-4 py-2 text-xs font-bold text-slate-700 hover:bg-slate-100">Explore</a>
        </nav>

        <div class="relative">
          <button id="locationBtn" class="flex max-w-[180px] items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2.5 text-xs font-black text-slate-700 shadow-sm sm:max-w-[260px]">
            <span class="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-sky-50 text-sky-600">⌖</span>
            <span id="locationText" class="truncate">Finding location…</span>
          </button>
          <div id="locationPanel" class="absolute right-0 top-14 z-50 hidden w-[min(92vw,380px)] rounded-[1.5rem] border border-slate-200 bg-white p-3 shadow-2xl">
            <div class="flex gap-2">
              <input id="citySearch" autocomplete="off" placeholder="Search city…" class="min-w-0 flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-bold outline-none focus:border-violet-300 focus:ring-4 focus:ring-violet-100" />
              <button id="detectBtn" class="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-[#17213a] text-white">⌖</button>
            </div>
            <div id="searchResults" class="mt-2 hidden max-h-72 overflow-auto"></div>
            <p class="px-2 pb-1 pt-3 text-[10px] font-medium leading-4 text-slate-400">Your location is used only to calculate local solar timings.</p>
          </div>
        </div>
      </header>

      <main>
        <section class="hero-grid relative overflow-hidden px-5 pb-16 pt-8 sm:px-8 lg:px-12 lg:pb-24 lg:pt-14">
          <div class="pointer-events-none absolute -left-20 top-20 h-80 w-80 rounded-full bg-sky-200/35 blur-3xl"></div>
          <div class="pointer-events-none absolute right-0 top-6 h-96 w-96 rounded-full bg-violet-200/30 blur-3xl"></div>

          <div class="relative grid items-center gap-12 lg:grid-cols-[.95fr_1.05fr]">
            <div class="max-w-2xl">
              <div class="mb-6 flex flex-wrap items-center gap-2">
                <span class="chip rounded-full px-3 py-1.5 text-[10px] font-black uppercase tracking-[.14em] text-violet-700">Location aware</span>
                <span class="chip rounded-full px-3 py-1.5 text-[10px] font-black uppercase tracking-[.14em] text-slate-500">Panchang · Muhurat · Festivals</span>
              </div>
              <h1 class="text-[3.25rem] font-black leading-[.92] tracking-[-.065em] text-[#17213a] sm:text-6xl lg:text-[5.6rem]">
                Your day,<br><span class="bg-gradient-to-r from-sky-500 via-violet-500 to-pink-500 bg-clip-text text-transparent">aligned with time.</span>
              </h1>
              <p class="mt-7 max-w-xl text-base font-medium leading-7 text-slate-500 sm:text-lg">A modern daily Panchang that turns traditional Vedic timings into a clear, location-aware experience for today.</p>
              <div class="mt-8 flex flex-wrap gap-3">
                <a href="choghadiya.php" class="rounded-full bg-[#17213a] px-6 py-3.5 text-sm font-black text-white shadow-lg shadow-slate-900/15 hover:-translate-y-0.5">Open Choghadiya →</a>
                <a href="#today" class="rounded-full border border-slate-200 bg-white px-6 py-3.5 text-sm font-black text-slate-700 hover:bg-slate-50">See today’s snapshot</a>
              </div>
              <div class="mt-9 flex flex-wrap gap-x-6 gap-y-2 text-xs font-bold text-slate-400">
                <span>✓ Auto location</span><span>✓ Local sunrise/sunset</span><span>✓ Mobile-first</span>
              </div>
            </div>

            <div class="relative mx-auto w-full max-w-[720px]">
              <div class="absolute -inset-10 rounded-full bg-gradient-to-r from-sky-300/10 via-violet-300/20 to-pink-300/10 blur-3xl"></div>
              <div class="relative rounded-[2rem] border border-white bg-white/70 p-3 shadow-lift backdrop-blur-xl sm:p-5">
                <div class="rounded-[1.65rem] bg-[#111827] p-5 text-white sm:p-7">
                  <div class="flex items-start justify-between gap-4">
                    <div>
                      <div id="currentSide" class="text-[10px] font-black uppercase tracking-[.18em] text-white/40">Current Choghadiya</div>
                      <div class="mt-2 flex items-end gap-3">
                        <div id="currentName" class="text-4xl font-black tracking-[-.05em] sm:text-5xl">Loading…</div>
                        <span id="currentLabel" class="mb-1 rounded-full bg-white/10 px-2.5 py-1 text-[9px] font-black uppercase tracking-[.12em] text-violet-200">Live</span>
                      </div>
                      <div id="currentRange" class="mt-2 text-sm font-semibold text-white/50">Preparing local timings</div>
                    </div>
                    <div class="text-right">
                      <div id="clock" class="text-xl font-black tabular-nums sm:text-2xl">--:--:--</div>
                      <div id="changesIn" class="mt-1 text-[10px] font-bold uppercase tracking-[.12em] text-white/35">—</div>
                    </div>
                  </div>
                  <div class="mt-8 h-1.5 overflow-hidden rounded-full bg-white/10"><div id="heroProgress" class="spectrum h-full w-0 rounded-full transition-[width] duration-500"></div></div>
                  <div class="mt-6 grid grid-cols-3 gap-2.5">
                    <div class="rounded-2xl border border-white/[.06] bg-white/[.045] p-3"><div class="text-[9px] font-bold uppercase tracking-[.12em] text-white/35">Sunrise</div><div id="sunrise" class="mt-1.5 text-sm font-black">--</div></div>
                    <div class="rounded-2xl border border-white/[.06] bg-white/[.045] p-3"><div class="text-[9px] font-bold uppercase tracking-[.12em] text-white/35">Sunset</div><div id="sunset" class="mt-1.5 text-sm font-black">--</div></div>
                    <div class="rounded-2xl border border-white/[.06] bg-white/[.045] p-3"><div class="text-[9px] font-bold uppercase tracking-[.12em] text-white/35">Date</div><div id="heroDate" class="mt-1.5 truncate text-sm font-black">--</div></div>
                  </div>
                </div>

                <div class="mt-3 grid grid-cols-4 gap-2">
                  <div class="pixel blue"></div><div class="pixel blue opacity-80"></div><div class="pixel violet opacity-70"></div><div class="pixel bg-white"></div>
                  <div class="pixel blue opacity-80"></div><div class="pixel violet"></div><div class="pixel pink"></div><div class="pixel orange"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="today" class="px-5 py-10 sm:px-8 lg:px-12 lg:py-14">
          <div class="mb-7 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p class="text-[10px] font-black uppercase tracking-[.2em] text-violet-600">Today at a glance</p>
              <h2 class="mt-2 text-3xl font-black tracking-[-.045em] sm:text-4xl">The essentials, without the clutter.</h2>
              <p id="todayLabel" class="mt-2 text-sm font-semibold text-slate-400">Loading today…</p>
            </div>
            <p id="heroLocation" class="rounded-full bg-slate-50 px-4 py-2 text-xs font-black text-slate-500">Current location</p>
          </div>

          <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <div class="tool-card soft-border rounded-[1.7rem] bg-gradient-to-br from-amber-50 to-white p-5">
              <div class="flex items-center justify-between"><span class="utility-icon grid h-11 w-11 place-items-center rounded-2xl bg-amber-100 text-xl">☀</span><span class="text-[9px] font-black uppercase tracking-[.13em] text-amber-700">Solar</span></div>
              <div class="mt-7 text-xs font-bold text-slate-400">Sunrise</div><div id="sunrise2" class="mt-1 text-2xl font-black">Local</div><p class="mt-2 text-xs font-medium leading-5 text-slate-400">Calculated for your detected location.</p>
            </div>
            <div class="tool-card soft-border rounded-[1.7rem] bg-gradient-to-br from-indigo-50 to-white p-5">
              <div class="flex items-center justify-between"><span class="utility-icon grid h-11 w-11 place-items-center rounded-2xl bg-indigo-100 text-xl">☾</span><span class="text-[9px] font-black uppercase tracking-[.13em] text-indigo-700">Solar</span></div>
              <div class="mt-7 text-xs font-bold text-slate-400">Sunset</div><div id="sunset2" class="mt-1 text-2xl font-black">Local</div><p class="mt-2 text-xs font-medium leading-5 text-slate-400">End of the local daylight period.</p>
            </div>
            <div class="tool-card soft-border rounded-[1.7rem] bg-gradient-to-br from-rose-50 to-white p-5">
              <div class="flex items-center justify-between"><span class="utility-icon grid h-11 w-11 place-items-center rounded-2xl bg-rose-100 text-xl">☊</span><span class="text-[9px] font-black uppercase tracking-[.13em] text-rose-700">Avoid</span></div>
              <div class="mt-7 text-xs font-bold text-slate-400">Rahu Kaal</div><div id="rahu" class="mt-1 text-xl font-black">--</div><p class="mt-2 text-xs font-medium leading-5 text-slate-400">A commonly avoided window for new beginnings.</p>
            </div>
            <div class="tool-card soft-border rounded-[1.7rem] bg-gradient-to-br from-emerald-50 to-white p-5">
              <div class="flex items-center justify-between"><span class="utility-icon grid h-11 w-11 place-items-center rounded-2xl bg-emerald-100 text-xl">✦</span><span class="text-[9px] font-black uppercase tracking-[.13em] text-emerald-700">Next good</span></div>
              <div class="mt-7 text-xs font-bold text-slate-400">Favourable window</div><div id="nextGood" class="mt-1 text-xl font-black">--</div><p id="nextGoodSub" class="mt-2 text-xs font-medium leading-5 text-slate-400">Finding next window…</p>
            </div>
          </div>
        </section>

        <section class="border-y border-slate-100 bg-slate-50/70 px-5 py-10 sm:px-8 lg:px-12 lg:py-14">
          <div class="mb-6 flex items-end justify-between gap-4"><div><p class="text-[10px] font-black uppercase tracking-[.2em] text-sky-600">Day flow</p><h2 class="mt-2 text-2xl font-black tracking-[-.04em] sm:text-3xl">Choghadiya timeline</h2></div><a href="choghadiya.php" class="text-xs font-black text-violet-600 hover:text-violet-800">Full day + night →</a></div>
          <div id="timeline" class="flex gap-2 overflow-x-auto pb-3 pt-1"></div>
        </section>

        <section id="utilities" class="px-5 py-12 sm:px-8 lg:px-12 lg:py-16">
          <div class="mb-8 max-w-2xl"><p class="text-[10px] font-black uppercase tracking-[.2em] text-pink-600">Tithika utilities</p><h2 class="mt-2 text-3xl font-black tracking-[-.045em] sm:text-4xl">A whole Panchang toolkit, organized like an app.</h2><p class="mt-3 text-sm font-medium leading-6 text-slate-500">The dense reference pages become focused tools. Each utility gets a clean page instead of putting everything into one endless dashboard.</p></div>

          <div class="grid gap-4 lg:grid-cols-12">
            <a href="choghadiya.php" class="tool-card relative overflow-hidden rounded-[2rem] border border-slate-200 bg-[#17213a] p-6 text-white lg:col-span-7 lg:min-h-[300px]">
              <div class="absolute right-0 top-0 h-64 w-64 rounded-full bg-violet-500/20 blur-3xl"></div>
              <div class="relative flex h-full flex-col justify-between">
                <div class="flex items-center justify-between"><span class="rounded-full bg-white/10 px-3 py-1.5 text-[9px] font-black uppercase tracking-[.14em] text-violet-200">Live now</span><span class="text-3xl">◐</span></div>
                <div class="mt-14"><h3 class="text-3xl font-black tracking-[-.045em]">Choghadiya</h3><p class="mt-2 max-w-lg text-sm font-medium leading-6 text-white/50">Day and night Muhurat windows, active-period countdown, Rahu Kaal, local sunrise and sunset.</p><div class="mt-5 text-xs font-black text-white">Open utility →</div></div>
              </div>
            </a>

            <div class="tool-card spectrum-soft rounded-[2rem] border border-violet-100 p-6 lg:col-span-5">
              <div class="flex items-center justify-between"><span class="utility-icon grid h-12 w-12 place-items-center rounded-2xl bg-white text-2xl">☸</span><span class="rounded-full bg-white/70 px-3 py-1 text-[9px] font-black uppercase tracking-[.12em] text-violet-600">Next module</span></div>
              <h3 class="mt-10 text-2xl font-black tracking-[-.035em]">Daily Panchang</h3><p class="mt-2 text-sm font-medium leading-6 text-slate-500">Tithi, Nakshatra, Yoga, Karana, Paksha, lunar month, sunrise/moonrise and auspicious timings in one structured view.</p>
            </div>

            <div class="tool-card rounded-[2rem] border border-slate-200 bg-white p-6 lg:col-span-4">
              <span class="utility-icon grid h-12 w-12 place-items-center rounded-2xl bg-amber-100 text-2xl">🪔</span><h3 class="mt-8 text-xl font-black">Muhurat</h3><p class="mt-2 text-sm font-medium leading-6 text-slate-500">Abhijit, Brahma, Godhuli, Vijay and activity-specific auspicious windows.</p>
            </div>
            <div class="tool-card rounded-[2rem] border border-slate-200 bg-white p-6 lg:col-span-4">
              <span class="utility-icon grid h-12 w-12 place-items-center rounded-2xl bg-rose-100 text-2xl">🪷</span><h3 class="mt-8 text-xl font-black">Festivals & Vrat</h3><p class="mt-2 text-sm font-medium leading-6 text-slate-500">Upcoming Ekadashi, Purnima, Sankashti, Pradosh and major Hindu festival calendars.</p>
            </div>
            <div class="tool-card rounded-[2rem] border border-slate-200 bg-white p-6 lg:col-span-4">
              <span class="utility-icon grid h-12 w-12 place-items-center rounded-2xl bg-sky-100 text-2xl">◎</span><h3 class="mt-8 text-xl font-black">Planetary events</h3><p class="mt-2 text-sm font-medium leading-6 text-slate-500">Transits, retrogrades, combustion, zodiac entries and other astronomical markers.</p>
            </div>
          </div>
        </section>

        <section id="explore" class="px-5 pb-14 sm:px-8 lg:px-12 lg:pb-20">
          <div class="overflow-hidden rounded-[2.2rem] bg-[#101c19] text-white">
            <div class="grid lg:grid-cols-[.8fr_1.2fr]">
              <div class="p-7 sm:p-10 lg:p-12">
                <p class="text-[10px] font-black uppercase tracking-[.2em] text-emerald-300">Modern by design</p>
                <h2 class="mt-3 text-4xl font-black tracking-[-.05em] sm:text-5xl">Traditional depth.<br><span class="text-white/35">Modern clarity.</span></h2>
                <p class="mt-5 max-w-md text-sm font-medium leading-7 text-white/50">Tithika is being shaped as a utility platform rather than a replica of legacy Panchang sites: less visual noise, clearer hierarchy and mobile interactions designed for everyday use.</p>
                <div class="mt-8 grid grid-cols-2 gap-3 text-xs font-black">
                  <div class="rounded-2xl border border-white/10 bg-white/[.04] p-4"><div class="text-2xl">⌖</div><div class="mt-4">Location based</div></div>
                  <div class="rounded-2xl border border-white/10 bg-white/[.04] p-4"><div class="text-2xl">◌</div><div class="mt-4">Solar accurate</div></div>
                  <div class="rounded-2xl border border-white/10 bg-white/[.04] p-4"><div class="text-2xl">◫</div><div class="mt-4">Mobile first</div></div>
                  <div class="rounded-2xl border border-white/10 bg-white/[.04] p-4"><div class="text-2xl">✦</div><div class="mt-4">Fast at a glance</div></div>
                </div>
              </div>
              <div class="relative min-h-[420px] overflow-hidden border-t border-white/10 lg:border-l lg:border-t-0">
                <div class="absolute inset-0 bg-[radial-gradient(circle_at_20%_70%,rgba(86,199,161,.35),transparent_26%),radial-gradient(circle_at_70%_30%,rgba(190,218,75,.28),transparent_28%),radial-gradient(circle_at_86%_74%,rgba(56,157,209,.34),transparent_30%)]"></div>
                <div class="absolute left-[8%] top-[18%] h-56 w-72 rotate-[-20deg] rounded-[55%_45%_45%_55%] border border-emerald-200/50 bg-gradient-to-br from-amber-500/80 via-lime-400/60 to-transparent shadow-[0_0_70px_rgba(235,194,75,.22)]"></div>
                <div class="absolute left-[28%] top-[38%] h-64 w-80 rotate-[18deg] rounded-[55%_45%_55%_45%] border border-lime-100/40 bg-gradient-to-br from-lime-400/80 via-emerald-400/55 to-transparent"></div>
                <div class="absolute right-[-8%] top-[18%] h-80 w-80 rotate-[28deg] rounded-[55%_45%_55%_45%] border border-cyan-200/50 bg-gradient-to-br from-emerald-400/75 via-cyan-400/55 to-transparent"></div>
                <div class="absolute inset-x-0 bottom-8 text-center text-[5rem] font-black tracking-[-.07em] text-white/95 sm:text-[7rem]">TITHIKA</div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer class="border-t border-slate-100 px-5 py-8 sm:px-8 lg:px-12">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div><div class="font-black">Tithika</div><div class="mt-1 text-[10px] font-medium text-slate-400">Traditional calendar conventions presented as a modern utility.</div></div>
          <div class="flex gap-5 text-xs font-bold text-slate-400"><a href="choghadiya.php" class="hover:text-slate-700">Choghadiya</a><a href="#utilities" class="hover:text-slate-700">Utilities</a><a href="#today" class="hover:text-slate-700">Today</a></div>
        </div>
      </footer>

      <nav class="glass fixed inset-x-3 bottom-3 z-40 mx-auto flex max-w-md items-center justify-around rounded-[1.4rem] border border-white/90 p-2 shadow-2xl lg:hidden">
        <a href="index.php" class="flex flex-col items-center gap-1 rounded-xl bg-slate-900 px-5 py-2 text-[9px] font-black text-white"><span class="text-base">⌂</span>Home</a>
        <a href="#today" class="flex flex-col items-center gap-1 px-4 py-2 text-[9px] font-black text-slate-500"><span class="text-base">☀</span>Today</a>
        <a href="choghadiya.php" class="flex flex-col items-center gap-1 px-4 py-2 text-[9px] font-black text-slate-500"><span class="text-base">◐</span>Muhurat</a>
        <button id="mobileLocationBtn" class="flex flex-col items-center gap-1 px-4 py-2 text-[9px] font-black text-slate-500"><span class="text-base">⌖</span>Place</button>
      </nav>

      <div id="toast" class="pointer-events-none fixed bottom-24 left-1/2 z-[70] hidden max-w-[calc(100%-2rem)] -translate-x-1/2 rounded-2xl bg-slate-900 px-4 py-3 text-center text-xs font-bold text-white shadow-2xl"></div>
    </div>
  </div>

  <script src="assets/home.js?v=1"></script>
  <script>
    // mirror live solar values into the secondary summary cards
    const mirror=()=>{const a=document.querySelector('#sunrise'),b=document.querySelector('#sunset'),a2=document.querySelector('#sunrise2'),b2=document.querySelector('#sunset2');if(a&&a2)a2.textContent=a.textContent;if(b&&b2)b2.textContent=b.textContent};setInterval(mirror,500);
  </script>
</body>
</html>