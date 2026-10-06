(()=> {
  const $=s=>document.querySelector(s);
  const base=window.TITHIKA_BASE||'/';
  const pageSlug=window.TITHIKA_PAGE_SLUG||'';
  const panchangPages=['panchang/daily','panchang/moonrise-moonset','panchang/rahu-kala','muhurat/rahu-kala','muhurat/abhijit'];
  const lagnaPages=['muhurat/lagna','panchang/lagna-kundali'];
  const monthPages=['panchang/month'];
  const planetaryModes={
    'planets/positions':'positions',
    'planets/transit':'transit',
    'planets/retrograde':'retrograde',
    'planets/combustion':'combustion'
  };
  const aspectsModes={
    'planets/mutual-aspects':'mutual',
    'planets/lunar-aspects':'lunar',
    'planets/conjunctions':'conjunctions',
    'planets/graha-yuddha':'graha-yuddha'
  };
  const eclipseModes={
    'astronomy/eclipses':'all',
    'astronomy/solar-eclipse':'solar',
    'astronomy/lunar-eclipse':'lunar'
  };
  const kundaliPages=['jyotish/janma-kundali'];
  const analysisPages=['jyotish/horoscope-analysis'];
  const interpretationPages=['jyotish/interpretation-report'];
  const timelinePages=['jyotish/timing-timeline'];
  const rashifalPages=['jyotish/rashifal','jyotish/rashifal/daily','jyotish/rashifal/weekly','jyotish/rashifal/monthly','jyotish/rashifal/yearly'];
  const dashaPages=['jyotish/vimshottari-dasha'];
  const doshaModes={
    'jyotish/mangal-dosha':'mangal',
    'jyotish/kalasarpa':'kalasarpa',
    'jyotish/shani-sadesati':'sade-sati'
  };
  const ashtaPages=['jyotish/ashtakavarga'];
  const shadbalaPages=['jyotish/shadbala'];
  const vargaPages=['jyotish/divisional-charts'];
  const yogaPages=['jyotish/yogas'];
  const matchPages=['jyotish/horoscope-match'];
  const marriagePages=['jyotish/marriage-analysis'];
  const nakMatchPages=['jyotish/nakshatra-compatibility'];
  const NAKSHATRAS=['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishta','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati'];
  const jyotishModes={
    'jyotish/birthstar':'birthstar',
    'jyotish/janma-lagna':'janma-lagna',
    'jyotish/moonsign':'moonsign',
    'jyotish/sunsign':'sunsign'
  };
  const lunarKinds={
    'vrat/ekadashi':'ekadashi',
    'vrat/purnima':'purnima',
    'vrat/amavasya':'amavasya'
  };
  const observanceKinds={
    'vrat/pradosham':'pradosh',
    'vrat/sankashti-chaturthi':'sankashti',
    'vrat/masik-shivaratri':'shivaratri',
    'festivals/maha-shivaratri':'shivaratri'
  };
  const festivalKinds={
    'festivals/ganesha-chaturthi':'ganesh-chaturthi',
    'festivals/raksha-bandhan':'raksha-bandhan',
    'festivals/navratri':'navratri',
    'festivals/dussehra':'dussehra',
    'festivals/holi':'holi',
    'festivals/karwa-chauth':'karwa-chauth',
    'festivals/janmashtami':'janmashtami',
    'festivals/rama-navami':'rama-navami',
    'festivals/hanuman-jayanti':'hanuman-jayanti',
    'festivals/akshaya-tritiya':'akshaya-tritiya',
    'festivals/vat-savitri':'vat-savitri',
    'festivals/durga-puja':'durga-puja',
    'festivals/diwali':'diwali'
  };
  const dwadashiPages=['vrat/dwadashi'];
  const mahadwadashiPages=['vrat/mahadwadashi'];
  const sankrantiPages=['vrat/sankranti','calendars/sankranti','festivals/sankranti','festivals/makar-sankranti'];
  const seasonKinds={
    'astronomy/vernal-equinox':'vernal_equinox',
    'astronomy/summer-solstice':'summer_solstice',
    'astronomy/autumnal-equinox':'autumnal_equinox',
    'astronomy/winter-solstice':'winter_solstice'
  };
  const browserTimezone=Intl.DateTimeFormat().resolvedOptions().timeZone||'Asia/Kolkata';
  const state={
    lat:19.076,lon:72.8777,city:'Mumbai, Maharashtra, India',
    timezone:'Asia/Kolkata',
    data:null,panchang:null,searchTimer:null,dateTouched:false,
    monthData:null,monthKey:'',lunarCache:new Map(),observanceCache:new Map(),festivalCache:new Map(),dwadashiCache:new Map(),mahadwadashiCache:new Map(),sankrantiCache:new Map()
  };
  const matchState={
    groom:{lat:null,lon:null,city:'',timezone:''},
    bride:{lat:null,lon:null,city:'',timezone:''}
  };

  function isoToday(timeZone=state.timezone){
    const parts=new Intl.DateTimeFormat('en-CA',{
      timeZone,year:'numeric',month:'2-digit',day:'2-digit'
    }).formatToParts(new Date());
    const v=Object.fromEntries(parts.map(p=>[p.type,p.value]));
    return `${v.year}-${v.month}-${v.day}`;
  }

  function payload(){
    return {
      lat:state.lat,lon:state.lon,city:state.city,
      date:$('#tkDate')?.value||isoToday(),timezone:state.timezone,hour24:false
    };
  }

  function toast(msg){
    const el=$('#tkToast'); if(!el)return;
    el.textContent=msg;el.hidden=false;
    clearTimeout(el._t);el._t=setTimeout(()=>el.hidden=true,3200);
  }

  function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}

  async function reverse(lat,lon){
    try{
      const r=await fetch(`${base}api.php?action=reverse&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`);
      const j=await r.json();
      if(j.ok&&j.label)state.city=j.label;
    }catch(e){}
  }

  async function resolveTimezone(lat,lon,{fallback=null}={}){
    try{
      const r=await fetch(`${base}api.php?action=timezone&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`);
      const j=await r.json();
      if(!j.ok||!j.timezone)throw new Error(j.error||'Timezone unavailable');
      state.timezone=j.timezone;
      if(!state.dateTouched&&$('#tkDate')) $('#tkDate').value=isoToday(state.timezone);
      return true;
    }catch(e){
      if(fallback){
        state.timezone=fallback;
        if(!state.dateTouched&&$('#tkDate')) $('#tkDate').value=isoToday(state.timezone);
        return true;
      }
      toast('Could not resolve the selected city timezone. Please try again.');
      return false;
    }
  }

  async function calculate(){
    try{
      const r=await fetch(`${base}api.php?action=calculate`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(payload())
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate solar context');
      state.data=j;renderSolar(j);
      if(panchangPages.includes(pageSlug)) await calculatePanchang();
      if(lagnaPages.includes(pageSlug)) await calculateLagna();
      if(monthPages.includes(pageSlug)) await calculateMonth();
      if(planetaryModes[pageSlug]) await calculatePlanetary();
      if(aspectsModes[pageSlug]) await calculateAspects();
      if(eclipseModes[pageSlug]) await calculateEclipses();
      if(kundaliPages.includes(pageSlug)) await calculateKundali();
      if(analysisPages.includes(pageSlug)) await calculateHoroscopeAnalysis();
      if(interpretationPages.includes(pageSlug)) await calculateInterpretation();
      if(timelinePages.includes(pageSlug)) await calculateTimeline();
      if(rashifalPages.includes(pageSlug)) await calculateRashifal();
      if(dashaPages.includes(pageSlug)) await calculateDasha();
      if(doshaModes[pageSlug]) await calculateDosha();
      if(ashtaPages.includes(pageSlug)) await calculateAshtakavarga();
      if(shadbalaPages.includes(pageSlug)) await calculateShadbala();
      if(vargaPages.includes(pageSlug)) await calculateVarga();
      if(yogaPages.includes(pageSlug)) await calculateYogas();
      if(jyotishModes[pageSlug]) await calculateJyotish();
      if(lunarKinds[pageSlug]) await calculateLunarOccurrences();
      if(observanceKinds[pageSlug]) await calculateObservances();
      if(festivalKinds[pageSlug]) await calculateFestival();
      if(dwadashiPages.includes(pageSlug)) await calculateDwadashi();
      if(mahadwadashiPages.includes(pageSlug)) await calculateMahadwadashi();
      if(sankrantiPages.includes(pageSlug)) await calculateSankranti();
      if(seasonKinds[pageSlug]) await calculateSeasons();
    }catch(e){toast(e.message||'Unable to load location context')}
  }

  function renderSolar(d){
    const short=(d.location.city||'Current location').split(',').slice(0,2).join(',');
    const set=(id,val)=>{const el=$(id);if(el)el.textContent=val};
    set('#tkPlaceText',short);
    set('#tkContextLocation',short);
    set('#tkContextDate',`${d.weekday}, ${d.date_label}`);
    set('#tkSunrise',d.sunrise_label);
    set('#tkSunset',d.sunset_label);
    set('#tkRahu',`${d.rahu_kaal.start_label} – ${d.rahu_kaal.end_label}`);
    if(d.active){
      set('#tkCurrent',d.active.name);
      set('#tkCurrentRange',`${d.active.start_label} – ${d.active.end_label}`);
      const now=new Date(),start=new Date(d.active.start),end=new Date(d.active.end);
      const pct=Math.max(0,Math.min(100,((now-start)/(end-start))*100));
      const bar=$('#tkContextProgress');if(bar)bar.style.width=`${pct}%`;
    }else{
      set('#tkCurrent','Solar day');
      set('#tkCurrentRange',`${d.sunrise_label} – ${d.sunset_label}`);
    }
  }

  async function calculatePlanetary(){
    const loading=$('#tkPlanetaryLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating planetary ephemeris…'}
    try{
      const mode=planetaryModes[pageSlug];
      const p=payload();
      if(mode==='positions'){
        const time=$('#tkPlanetTime')?.value||'12:00:00';
        p.datetime=`${p.date}T${time}`;
        p.node_model=$('#tkNodeModel')?.value||'mean';
      }
      const r=await fetch(`${base}api.php?action=planetary&mode=${encodeURIComponent(mode)}`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Planetary engine unavailable');
      if(loading)loading.hidden=true;
      renderPlanetary(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Planetary engine unavailable'}
      toast(e.message||'Planetary engine unavailable');
    }
  }

  function renderPlanetary(d){
    const el=$('#tkPlanetaryResult');if(!el)return;
    const note=$('#tkPlanetaryNote');if(note)note.textContent=d.note||'';
    const title=$('#tkPlanetaryTitle');if(title&&d.year)title.textContent=`${title.textContent.replace(/\s+\d{4}$/,'')} ${d.year}`;
    if(d.mode==='positions'){
      el.innerHTML=`<div class="tk-planet-grid">${(d.planets||[]).map(row=>`<article class="tk-planet-card">
        <div class="tk-planet-name"><strong>${esc(row.name)}</strong><span>${row.retrograde?'↺ Retrograde':'↻ Direct'}${row.combust?' · Asta':''}</span></div>
        <h4>${esc(row.rashi)} ${Number(row.degree_in_rashi).toFixed(2)}°</h4>
        <p>${esc(row.nakshatra)} · Pada ${row.pada}</p>
        <small>${Number(row.longitude).toFixed(2)}° · ${Number(row.speed_deg_day).toFixed(2)}°/day</small>
      </article>`).join('')}</div>`;
      return;
    }
    const rows=d.events||[];
    el.innerHTML=rows.length?rows.map(row=>`<article class="tk-planet-event">
      <div class="tk-planet-event-date"><b>${esc(row.date)}</b><span>${esc(row.planet)}</span></div>
      <div class="tk-planet-event-main">
        <h4>${esc(row.event?row.event.replaceAll('_',' '):row.from_rashi+' → '+row.to_rashi)}</h4>
        <p>${row.from_rashi?esc(row.from_rashi+' → '+row.to_rashi+' · '+row.direction):esc(row.rashi||'')}</p>
        <small>${esc(new Date(row.datetime).toLocaleString('en-IN',{timeZone:state.timezone,dateStyle:'medium',timeStyle:'short'}))}</small>
      </div>
    </article>`).join(''):'<div class="tk-panchang-empty">No events found for this year.</div>';
  }

  async function calculateJyotish(){
    const loading=$('#tkJyotishLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating birth factors…'}
    try{
      const mode=jyotishModes[pageSlug];
      const p=payload();
      p.time=$('#tkBirthTime')?.value||'12:00:00';
      const r=await fetch(`${base}api.php?action=jyotish&mode=${encodeURIComponent(mode)}`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Jyotish calculation unavailable');
      if(loading)loading.hidden=true;
      renderJyotish(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Jyotish calculation unavailable'}
      toast(e.message||'Jyotish calculation unavailable');
    }
  }

  function renderJyotish(d){
    const el=$('#tkJyotishResult');if(!el)return;
    const p=d.primary||{},r=d.result||{};
    el.innerHTML=`<article class="tk-jyotish-primary">
      <small>${esc(p.title||'Result')}</small>
      <h3>${esc(p.value||'—')}</h3>
      <p>${p.pada?'Pada '+p.pada+' · ':''}${esc(p.rashi||'')}${p.degree_in_rashi!==undefined?' · '+Number(p.degree_in_rashi).toFixed(2)+'°':''}</p>
    </article>
    <div class="tk-jyotish-grid">
      <div><small>Moon</small><strong>${esc(r.moon?.rashi||'—')}</strong><span>${esc(r.moon?.nakshatra||'—')} · Pada ${r.moon?.pada||'—'}</span></div>
      <div><small>Sun</small><strong>${esc(r.sun?.rashi||'—')}</strong><span>${esc(r.sun?.nakshatra||'—')} · Pada ${r.sun?.pada||'—'}</span></div>
      <div><small>Lagna</small><strong>${esc(r.lagna?.rashi||'—')}</strong><span>${Number(r.lagna?.degree_in_rashi||0).toFixed(2)}°</span></div>
    </div>`;
  }

  async function calculateAspects(){
    const loading=$('#tkAspectLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating planetary relationships…'}
    try{
      const mode=aspectsModes[pageSlug],p=payload();
      const r=await fetch(`${base}api.php?action=aspects&mode=${encodeURIComponent(mode)}`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Aspect engine unavailable');
      if(loading)loading.hidden=true;
      const note=$('#tkAspectNote');if(note)note.textContent=j.note||'';
      const title=$('#tkAspectTitle');if(title)title.textContent=`${title.textContent.replace(/\s+\d{4}$/,'')} ${j.year}`;
      const el=$('#tkAspectResult');if(!el)return;
      const rows=j.events||[];
      el.innerHTML=rows.length?rows.map(row=>{
        if(mode==='graha-yuddha'){
          return `<article class="tk-planet-event"><div class="tk-planet-event-date"><b>${esc(row.date)}</b><span>${esc(row.rashi)}</span></div><div class="tk-planet-event-main"><h4>${esc(row.planet1)} × ${esc(row.planet2)}</h4><p>Begins ${esc(new Date(row.start).toLocaleString('en-IN',{timeZone:state.timezone,dateStyle:'medium',timeStyle:'short'}))} · Ends ${esc(new Date(row.end).toLocaleString('en-IN',{timeZone:state.timezone,dateStyle:'medium',timeStyle:'short'}))}</p><small>Closest ${Number(row.closest_separation_deg).toFixed(3)}° · Entry winner ${esc(row.entry_winner||'—')} · Exit winner ${esc(row.exit_winner||'—')}</small></div></article>`;
        }
        return `<article class="tk-planet-event"><div class="tk-planet-event-date"><b>${esc(row.date)}</b><span>${esc(row.aspect)}</span></div><div class="tk-planet-event-main"><h4>${esc(row.planet1)} + ${esc(row.planet2)}</h4><p>${Number(row.angle).toFixed(0)}° exact aspect</p><small>${esc(new Date(row.datetime).toLocaleString('en-IN',{timeZone:state.timezone,dateStyle:'medium',timeStyle:'short'}))}</small></div></article>`;
      }).join(''):'<div class="tk-panchang-empty">No matching events found for this year.</div>';
    }catch(e){if(loading)loading.textContent=e.message||'Aspect engine unavailable';toast(e.message||'Aspect engine unavailable')}
  }

  async function calculateEclipses(){
    const loading=$('#tkEclipseLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating eclipse events…'}
    try{
      const mode=eclipseModes[pageSlug],p=payload();
      const r=await fetch(`${base}api.php?action=eclipses&mode=${encodeURIComponent(mode)}`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Eclipse engine unavailable');
      if(loading)loading.hidden=true;
      const note=$('#tkEclipseNote');if(note)note.textContent=j.note||'';
      const title=$('#tkEclipseTitle');if(title)title.textContent=`${title.textContent.replace(/\s+\d{4}$/,'')} ${j.year}`;
      const el=$('#tkEclipseResult');if(!el)return;
      let rows=mode==='solar'?j.solar_global:mode==='lunar'?j.lunar:j.events;
      const localSolar=new Map((j.solar_local||[]).map(x=>[x.peak?.date,x]));
      el.innerHTML=(rows||[]).map(row=>{
        const local=row.type==='solar'?localSolar.get(row.peak?.date):row;
        const visible=local?.locally_visible;
        return `<article class="tk-eclipse-card"><div class="tk-eclipse-kind"><b>${esc(row.kind)}</b><span>${esc(row.type==='solar'?'Solar':'Lunar')}</span></div><div><h4>${esc(row.name)}</h4><p>${esc(row.peak?.label||'—')}</p><small>${visible===true?'Visible from selected location':visible===false?'Not visible from selected location':'Global event'}${row.obscuration!==null&&row.obscuration!==undefined?' · Obscuration '+Math.round(row.obscuration*100)+'%':''}</small></div></article>`;
      }).join('')||'<div class="tk-panchang-empty">No eclipse events found for this year.</div>';
    }catch(e){if(loading)loading.textContent=e.message||'Eclipse engine unavailable';toast(e.message||'Eclipse engine unavailable')}
  }

  function renderKundaliChart(cells,label){
    const order=[11,0,1,2,10,null,null,3,9,null,null,4,8,7,6,5];
    const by=new Map((cells||[]).map(x=>[x.rashi_id,x]));
    return `<section class="tk-kundali-chart-wrap"><h4>${esc(label)}</h4><div class="tk-kundali-chart">${order.map((id,i)=>{
      if(id===null)return `<div class="tk-kundali-center">${i===5?esc(label):''}</div>`;
      const cell=by.get(id)||{};
      return `<div class="tk-kundali-cell"><small>H${cell.house||'—'} · ${esc(cell.rashi||'')}</small><strong>${(cell.planets||[]).map(p=>esc(p.name)+(p.retrograde?' ℞':'')).join(' · ')||'—'}</strong></div>`;
    }).join('')}</div></section>`;
  }

  async function calculateKundali(){
    const loading=$('#tkKundaliLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating Janma Kundali…'}
    try{
      const p=payload();
      p.time=$('#tkKundaliTime')?.value||'12:00:00';
      p.node_model=$('#tkKundaliNode')?.value||'mean';
      const r=await fetch(`${base}api.php?action=kundali`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Kundali engine unavailable');
      if(loading)loading.hidden=true;
      const el=$('#tkKundaliResult');if(!el)return;
      const yuddha=(j.graha_yuddha||[]).map(x=>`${esc(x.planet1)}–${esc(x.planet2)} (${esc(x.winner||'tie')} wins)`).join(' · ');
      el.innerHTML=`<div class="tk-kundali-head"><div><small>Janma Lagna</small><strong>${esc(j.lagna?.rashi||'—')} ${Number(j.lagna?.degree_in_rashi||0).toFixed(2)}°</strong></div><div><small>Birth Nakshatra</small><strong>${esc(j.panchang?.nakshatra||'—')} · Pada ${j.panchang?.nakshatra_pada||'—'}</strong></div><div><small>Node model</small><strong>${esc(j.node_model||'mean')}</strong></div></div>
        <div class="tk-kundali-charts">${renderKundaliChart(j.d1?.cells,'D1 · Rashi')}${renderKundaliChart(j.d9?.cells,'D9 · Navamsha')}</div>
        <div class="tk-kundali-grahas">${(j.d1?.placements||[]).map(p=>`<span><b>${esc(p.name)}</b>${esc(p.rashi)} ${Number(p.degree_in_rashi).toFixed(2)}° · H${p.house}</span>`).join('')}</div>
        <div class="tk-lunar-note">Tithi ${esc(j.panchang?.tithi||'—')} · Yoga ${esc(j.panchang?.yoga||'—')} · Karana ${esc(j.panchang?.karana||'—')}${yuddha?' · Graha Yuddha: '+yuddha:''}</div>`;
    }catch(e){if(loading)loading.textContent=e.message||'Kundali engine unavailable';toast(e.message||'Kundali engine unavailable')}
  }

  async function calculateHoroscopeAnalysis(){
    const loading=$('#tkAnalysisLoading');
    if(loading){loading.hidden=false;loading.textContent='Building unified Jyotish evidence report…'}
    try{
      const p=payload();
      p.time=$('#tkAnalysisTime')?.value||'12:00:00';
      p.node_model=$('#tkAnalysisNode')?.value||'mean';
      const r=await fetch(`${base}api.php?action=horoscope-analysis`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unified analysis engine unavailable');
      if(loading)loading.hidden=true;
      const el=$('#tkAnalysisResult');if(!el)return;
      const bp=j.birth_profile||{}, current=j.dasha?.current||{}, md=current.mahadasha||{}, ad=current.antardasha||{};
      const domains=Object.values(j.domains||{});
      const strength=new Map((j.strengths||[]).map(x=>[x.planet,x]));
      const currentLords=j.timing?.active_dasha_lords||[];
      el.innerHTML=`
        <div class="tk-analysis-hero">
          <div><small>Janma Lagna</small><strong>${esc(bp.lagna?.rashi||'—')} ${Number(bp.lagna?.degree_in_rashi||0).toFixed(2)}°</strong><span>${esc(bp.nakshatra||'—')} · Pada ${bp.nakshatra_pada||'—'}</span></div>
          <div><small>Current Vimshottari</small><strong>${esc(md.lord||'—')} / ${esc(ad.lord||'—')}</strong><span>As of ${esc(new Date(j.as_of).toLocaleDateString('en-IN',{timeZone:state.timezone,dateStyle:'medium'}))}</span></div>
          <div><small>Varga sensitivity</small><strong>${esc(j.sensitivity?.level||'—')}</strong><span>Nearest D9/D10 boundary ${Number(j.sensitivity?.varga_boundary_margin_deg||0).toFixed(3)}°</span></div>
        </div>
        <div class="tk-analysis-domain-grid">${domains.map(d=>`<article><header><small>${esc(d.title)}</small><b>${Number(d.evidence_index||0).toFixed(0)}</b></header><div class="tk-analysis-meter"><i style="width:${Math.max(0,Math.min(100,Number(d.evidence_index||0)))}%"></i></div><p>${esc(d.band)}</p><span>Houses ${(d.houses||[]).join(', ')} · Lords ${(d.house_lords||[]).map(esc).join(', ')}</span><small>${esc(d.description||'')}</small></article>`).join('')}</div>
        <div class="tk-analysis-section"><header><small>Divisional evidence</small><h4>D1 · D9 · D10</h4></header><div class="tk-kundali-charts">${renderKundaliChart(j.charts?.D1?.cells,'D1 · Rashi')}${renderKundaliChart(j.charts?.D9?.cells,'D9 · Navamsha')}${renderKundaliChart(j.charts?.D10?.cells,'D10 · Dashamsha')}</div></div>
        <div class="tk-analysis-section"><header><small>Planetary capacity</small><h4>Shadbala snapshot</h4></header><div class="tk-analysis-strengths">${(j.strengths||[]).map(x=>`<span><b>${esc(x.planet)}</b><strong class="${x.meets_required?'pass':'fail'}">${Number(x.ratio||0).toFixed(2)}×</strong><small>${Number(x.total_rupa||0).toFixed(2)} / ${Number(x.required_rupa||0).toFixed(1)} Rupa</small></span>`).join('')}</div></div>
        <div class="tk-analysis-section"><header><small>Active timing</small><h4>Dasha lords + major transits</h4></header><div class="tk-analysis-timing">${currentLords.map(x=>`<article><b>${esc(x.level)} · ${esc(x.planet)}</b><span>Natal H${x.natal_house||'—'} · ${esc(x.natal_rashi||'—')} · strength ${x.strength_ratio===null||x.strength_ratio===undefined?'—':Number(x.strength_ratio).toFixed(2)+'×'}</span></article>`).join('')}${(j.timing?.major_transits||[]).map(x=>`<article><b>${esc(x.planet)} transit${x.retrograde?' ℞':''}</b><span>${esc(x.rashi)} · H${x.house_from_lagna} from Lagna · H${x.house_from_moon} from Moon</span></article>`).join('')}</div></div>
        <div class="tk-analysis-section"><header><small>Structural combinations</small><h4>${j.yogas?.count||0} detected Yogas</h4></header><div class="tk-yoga-list">${(j.yogas?.items||[]).slice(0,12).map(y=>`<article><div class="tk-yoga-title"><span>${esc(y.category)}</span><h4>${esc(y.name)}</h4></div><p>${esc(y.rule)}</p></article>`).join('')||'<div class="tk-panchang-empty">No Yoga from the current curated rule set was detected.</div>'}</div></div>
        <div class="tk-lunar-note">${esc(j.note||'')} ${esc((j.methodology||[]).join(' · '))}</div>`;
    }catch(e){if(loading)loading.textContent=e.message||'Unified analysis engine unavailable';toast(e.message||'Unified analysis engine unavailable')}
  }

  async function calculateRashifal(){
    const loading=$('#tkRashifalLoading');
    if(loading){loading.hidden=false;loading.textContent='Building personalized Rashifal…'}
    try{
      const mode=$('#tkRashifalMode')?.value||'overview';
      const p=payload();
      p.date=$('#tkRashifalBirthDate')?.value||p.date;
      p.time=$('#tkRashifalBirthTime')?.value||'12:00:00';
      p.target_date=$('#tkRashifalTargetDate')?.value||isoToday(state.timezone);
      p.node_model=$('#tkRashifalNode')?.value||'mean';
      const r=await fetch(`${base}api.php?action=personal-rashifal&mode=${encodeURIComponent(mode)}`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Personalized Rashifal engine unavailable');
      if(loading)loading.hidden=true;
      const el=$('#tkRashifalResult');if(!el)return;
      const bp=j.birth_profile||{},periods=j.periods||{},ctx=j.current_context||{};
      const fmtDate=x=>x?new Date(x).toLocaleDateString('en-IN',{timeZone:state.timezone,dateStyle:'medium'}):'—';
      const modeTitle=x=>({daily:'Daily',weekly:'Weekly',monthly:'Monthly',yearly:'Yearly'}[x]||x);
      const scoreCard=x=>`<article class="tk-rashifal-domain ${esc(x.band||'background')}">
        <header><div><small>${esc(x.quality||'contextual')}</small><h5>${esc(x.title||'')}</h5></div><strong>${Number(x.activation_index||0).toFixed(0)}</strong></header>
        <div class="tk-analysis-meter"><i style="width:${Math.max(0,Math.min(100,Number(x.activation_index||0)))}%"></i></div>
        <p>${esc(x.interpretation||'')}</p>
        <footer><span>Natal ${Number(x.average_base_points??x.base_points??0).toFixed(1)}</span><span>Dasha ${Number(x.average_dasha_points??x.dasha_points??0).toFixed(1)}</span><span>Transit ${Number(x.average_transit_points??x.transit_points??0).toFixed(1)}</span></footer>
      </article>`;
      const renderPeriod=(period,compact=false)=>{
        if(!period)return '';
        const top=period.top_focus||[];
        return `<section class="tk-rashifal-period ${compact?'compact':''}">
          <header><div><small>${esc(modeTitle(period.mode))} forecast</small><h4>${esc(period.label||'')}</h4></div><span>${period.sample_count||0} evidence sample${period.sample_count===1?'':'s'}</span></header>
          <div class="tk-rashifal-focus">${top.map(x=>`<div class="${esc(x.band||'background')}"><small>${esc(x.quality||'contextual')}</small><b>${esc(x.title||'')}</b><strong>${Number(x.activation_index||0).toFixed(0)}</strong></div>`).join('')}</div>
          ${compact?'':`<div class="tk-rashifal-domains">${Object.values(period.domains||{}).map(scoreCard).join('')}</div>
          <div class="tk-rashifal-samples">${(period.samples||[]).map(x=>`<article><header><b>${esc(x.weekday||'')}</b><time>${fmtDate(x.datetime)}</time></header><div>${(x.top_focus||[]).map(y=>`<span class="${esc(y.band||'background')}">${esc(y.title)} <b>${Number(y.activation_index||0).toFixed(0)}</b></span>`).join('')}</div></article>`).join('')}</div>
          <div class="tk-timeline-markers">${(period.markers||[]).map(x=>`<article><time>${fmtDate(x.datetime)}</time><span class="${esc(x.type||'')}">${esc(x.type||'')}</span><b>${esc(x.label||'')}</b></article>`).join('')||'<div class="tk-panchang-empty">No major Dasha or slow-transit boundary in this period.</div>'}</div>`}
        </section>`;
      };
      const currentDasha=(ctx.active_dasha||[]).map(x=>`${esc(x.planet)} ${esc(x.level.replace('dasha',''))}`).join(' · ');
      const slow=(ctx.slow_transits||[]).map(x=>`${esc(x.planet)} H${x.house_from_lagna}${x.retrograde?' ℞':''}`).join(' · ');
      const overview=j.mode==='overview'
        ? `<section class="tk-rashifal-overview"><header><small>Four horizons</small><h4>Personal forecast overview</h4></header><div>${['daily','weekly','monthly','yearly'].map(k=>renderPeriod(periods[k],true)).join('')}</div></section>`
        : renderPeriod(periods[j.mode],false);
      const detail=j.mode==='overview'?'': '';
      el.innerHTML=`
        <div class="tk-rashifal-hero">
          <div><small>Janma Lagna</small><strong>${esc(bp.lagna?.rashi||'—')} ${Number(bp.lagna?.degree_in_rashi||0).toFixed(2)}°</strong><span>${esc(bp.nakshatra||'—')} · Pada ${bp.nakshatra_pada||'—'}</span></div>
          <div><small>Active Vimshottari</small><strong>${currentDasha||'—'}</strong><span>Forecast target ${fmtDate(j.target_date+'T12:00:00')}</span></div>
          <div><small>Slow transit context</small><strong>${slow||'—'}</strong><span>Jupiter · Saturn · Rahu · Ketu from Lagna</span></div>
        </div>
        ${overview}
        ${detail}
        <div class="tk-lunar-note">${esc(j.note||'')} ${esc(j.methodology?.meaning||'')}</div>`;
    }catch(e){if(loading)loading.textContent=e.message||'Personalized Rashifal engine unavailable';toast(e.message||'Personalized Rashifal engine unavailable')}
  }

  async function calculateTimeline(){
    const loading=$('#tkTimelineLoading');
    if(loading){loading.hidden=false;loading.textContent='Building Dasha and transit activation timeline…'}
    try{
      const p=payload();
      p.time=$('#tkTimelineBirthTime')?.value||'12:00:00';
      p.start_month=$('#tkTimelineStart')?.value||isoToday(state.timezone).slice(0,7);
      p.months=Number($('#tkTimelineMonths')?.value||12);
      p.node_model=$('#tkTimelineNode')?.value||'mean';
      const r=await fetch(`${base}api.php?action=jyotish-timeline`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Timing timeline engine unavailable');
      if(loading)loading.hidden=true;
      const el=$('#tkTimelineResult');if(!el)return;
      const months=j.monthly_timeline||[],windows=j.activation_windows||[],years=j.yearly_summary||[],markers=j.markers||[];
      const bp=j.birth_profile||{};
      const fmtMonth=x=>{const [y,m]=String(x||'').split('-').map(Number);return y&&m?new Date(Date.UTC(y,m-1,1)).toLocaleDateString('en-IN',{timeZone:'UTC',year:'numeric',month:'short'}):esc(x||'—')};
      const endLabel=fmtMonth(j.end_month_exclusive);
      el.innerHTML=`
        <div class="tk-timeline-hero">
          <div><small>Forecast span</small><strong>${fmtMonth(j.start_month)} → ${endLabel}</strong><span>${j.months||0} monthly activation samples</span></div>
          <div><small>Janma Lagna</small><strong>${esc(bp.lagna?.rashi||'—')} ${Number(bp.lagna?.degree_in_rashi||0).toFixed(2)}°</strong><span>${esc(bp.nakshatra||'—')} · Pada ${bp.nakshatra_pada||'—'}</span></div>
          <div><small>Exact timing markers</small><strong>${markers.length}</strong><span>Mahadasha / Antardasha changes + slow-planet ingresses</span></div>
        </div>
        <section class="tk-timeline-section"><header><small>Condensed view</small><h4>Activation windows</h4></header>
          <div class="tk-timeline-windows">${windows.map(w=>`<article><span class="${esc(w.band)}">${esc(w.band)}</span><div><small>${fmtMonth(w.start_month)} → ${fmtMonth(w.end_month)} · ${w.months} month${w.months===1?'':'s'}</small><h5>${esc(w.focus_title)}</h5><p>${esc(w.quality)} activation</p></div><strong>${Number(w.average_activation_index||0).toFixed(0)}</strong></article>`).join('')||'<div class="tk-panchang-empty">No activation windows available.</div>'}</div>
        </section>
        <section class="tk-timeline-section"><header><small>Year overview</small><h4>Annual emphasis</h4></header>
          <div class="tk-timeline-years">${years.map(y=>`<article><header><b>${y.year}</b><small>${y.months_covered} months covered</small></header>${(y.top_focus||[]).map(x=>`<div><span>${esc(x.title)}</span><b>${Number(x.average_activation_index||0).toFixed(0)}</b><small>peak ${Number(x.peak_activation_index||0).toFixed(0)} · ${fmtMonth(x.peak_month)}</small></div>`).join('')}</article>`).join('')}</div>
        </section>
        <section class="tk-timeline-section"><header><small>Month-by-month</small><h4>Activation timeline</h4></header>
          <div class="tk-timeline-months">${months.map(m=>{const ds=(m.dasha||[]).map(x=>`${esc(x.planet)} ${esc(x.level.replace('dasha',''))}`).join(' · ');return `<article><header><div><small>${esc(ds||'Dasha context')}</small><h5>${esc(m.label)}</h5></div><span>${(m.transits||[]).map(x=>esc(x.planet)+' H'+x.house_from_lagna).join(' · ')}</span></header><div class="tk-timeline-focus">${(m.top_focus||[]).map(x=>`<div class="${esc(x.band)}"><span>${esc(x.title)}</span><strong>${Number(x.activation_index||0).toFixed(0)}</strong><small>${esc(x.band)} · ${esc(x.quality)}</small></div>`).join('')}</div><p>${esc((m.domains?.[m.top_focus?.[0]?.key]?.interpretation)||'')}</p></article>`}).join('')}</div>
        </section>
        <section class="tk-timeline-section"><header><small>Boundary events</small><h4>Dasha & transit markers</h4></header>
          <div class="tk-timeline-markers">${markers.map(x=>`<article><time>${esc(new Date(x.datetime).toLocaleDateString('en-IN',{timeZone:state.timezone,dateStyle:'medium'}))}</time><span class="${esc(x.type)}">${esc(x.type)}</span><b>${esc(x.label)}</b></article>`).join('')||'<div class="tk-panchang-empty">No major boundary markers in this horizon.</div>'}</div>
        </section>
        <div class="tk-lunar-note">${esc(j.note||'')} ${esc(j.methodology?.meaning||'')}</div>`;
    }catch(e){if(loading)loading.textContent=e.message||'Timing timeline engine unavailable';toast(e.message||'Timing timeline engine unavailable')}
  }

  async function calculateInterpretation(){
    const loading=$('#tkInterpretLoading');
    if(loading){loading.hidden=false;loading.textContent='Building evidence-backed interpretation…'}
    try{
      const p=payload();
      p.time=$('#tkInterpretTime')?.value||'12:00:00';
      p.node_model=$('#tkInterpretNode')?.value||'mean';
      const r=await fetch(`${base}api.php?action=jyotish-interpretation`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Interpretation engine unavailable');
      if(loading)loading.hidden=true;
      const el=$('#tkInterpretResult');if(!el)return;
      const bp=j.birth_profile||{};
      const focus=j.current_focus||[];
      const domains=Object.entries(j.domain_interpretations||{});
      const planets=j.planet_interpretations||[];
      const houses=j.house_interpretations||[];
      const roleClass=x=>({yogakaraka:'good',supportive:'good',mixed:'mixed',challenging:'warning',structural:'neutral'}[x]||'neutral');
      const dignityClass=x=>x==='exalted'||x==='own'?'good':x==='debilitated'?'warning':'neutral';
      el.innerHTML=`
        <div class="tk-interpret-hero">
          <div><small>Janma Lagna</small><strong>${esc(bp.lagna?.rashi||'—')} ${Number(bp.lagna?.degree_in_rashi||0).toFixed(2)}°</strong><span>${esc(bp.nakshatra||'—')} · Pada ${bp.nakshatra_pada||'—'}</span></div>
          <div><small>Interpretation profile</small><strong>Auditable rule-based</strong><span>Whole-sign lordship · D1/D9/D10 · Shadbala · SAV</span></div>
          <div><small>Current focus</small><strong>${focus.length?focus.map(x=>esc(x.title)).join(' · '):'Background cycle'}</strong><span>As-of timing uses Vimshottari + major transit houses</span></div>
        </div>
        <section class="tk-interpret-section"><header><small>Current emphasis</small><h4>Activated domains</h4></header>
          <div class="tk-interpret-focus">${focus.length?focus.map(x=>`<article><span class="${x.activation==='high'?'high':'active'}">${esc(x.activation)}</span><b>${esc(x.title)}</b><strong>${Number(x.evidence_index||0).toFixed(0)}/100</strong></article>`).join(''):'<div class="tk-panchang-empty">No major domain activation is flagged by the current Dasha/transit profile.</div>'}</div>
        </section>
        <section class="tk-interpret-section"><header><small>Domain readings</small><h4>Evidence + timing</h4></header>
          <div class="tk-interpret-domains">${domains.map(([key,d])=>`<article><div class="tk-interpret-domain-head"><div><small>${esc(key)}</small><h5>${esc(d.title)}</h5></div><b>${Number(d.evidence_index||0).toFixed(0)}</b></div><div class="tk-analysis-meter"><i style="width:${Math.max(0,Math.min(100,Number(d.evidence_index||0)))}%"></i></div><p>${esc(d.interpretation||'')}</p><span>Activation: ${esc(d.activation?.activation||'background')}</span>${(d.activation?.reasons||[]).length?`<ul>${d.activation.reasons.slice(0,4).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}</article>`).join('')}</div>
        </section>
        <section class="tk-interpret-section"><header><small>Functional lordship</small><h4>Planet-by-planet interpretation</h4></header>
          <div class="tk-interpret-planets">${planets.map(x=>{const role=x.functional_role||{},conf=x.divisional_confirmation||{},st=x.strength||{};return `<article><header><div><small>${(x.owned_houses||[]).map(h=>'H'+h).join(' · ')}</small><h5>${esc(x.planet)}</h5></div><span class="${roleClass(role.category)}">${esc(role.label||role.category||'')}</span></header><p>${esc(x.interpretation||'')}</p><div class="tk-interpret-facts"><span><small>D1</small><b class="${dignityClass(conf.d1?.dignity)}">${esc(conf.d1?.dignity||'—')}</b><em>H${conf.d1?.house||'—'} · ${esc(conf.d1?.rashi||'—')}</em></span><span><small>D9</small><b class="${dignityClass(conf.d9?.dignity)}">${esc(conf.d9?.dignity||'—')}</b><em>H${conf.d9?.house||'—'} · ${esc(conf.d9?.rashi||'—')}</em></span><span><small>D10</small><b class="${dignityClass(conf.d10?.dignity)}">${esc(conf.d10?.dignity||'—')}</b><em>H${conf.d10?.house||'—'} · ${esc(conf.d10?.rashi||'—')}</em></span><span><small>Shadbala</small><b>${Number(st.ratio||0).toFixed(2)}×</b><em>${x.active_dasha_level?esc(x.active_dasha_level)+' active':'Not current Dasha lord'}</em></span></div></article>`}).join('')}</div>
        </section>
        <section class="tk-interpret-section"><header><small>House synthesis</small><h4>Key houses</h4></header>
          <div class="tk-interpret-houses">${houses.map(x=>`<article><header><span>H${x.house}</span><div><small>${esc(x.theme)}</small><h5>${esc(x.lord)} rules this house</h5></div><b>${x.sav??'—'} SAV</b></header><p>${esc(x.interpretation||'')}</p><small>${(x.evidence||[]).map(esc).join(' · ')}</small></article>`).join('')}</div>
        </section>
        <div class="tk-lunar-note">${esc(j.note||'')} ${esc((j.methodology||[]).join(' · '))}</div>`;
    }catch(e){if(loading)loading.textContent=e.message||'Interpretation engine unavailable';toast(e.message||'Interpretation engine unavailable')}
  }

  async function calculateDasha(){
    const loading=$('#tkDashaLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating Vimshottari periods…'}
    try{
      const p=payload();p.time=$('#tkDashaTime')?.value||'12:00:00';
      const r=await fetch(`${base}api.php?action=vimshottari`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
      const j=await r.json();if(!j.ok)throw new Error(j.error||'Dasha engine unavailable');
      if(loading)loading.hidden=true;
      const el=$('#tkDashaResult');if(!el)return;
      const x=j.result||{};
      const current=x.current;
      el.innerHTML=`<div class="tk-jyotish-primary"><small>Birth balance</small><h3>${esc(x.starting_lord||'—')} Mahadasha</h3><p>${esc(x.nakshatra||'—')} · Pada ${x.nakshatra_pada||'—'} · ${Number(x.birth_balance_years||0).toFixed(2)} years remaining at birth</p></div>
        ${current?`<div class="tk-dasha-current"><span><b>Current Maha</b>${esc(current.mahadasha?.lord||'—')}</span><span><b>Current Antar</b>${esc(current.antardasha?.lord||'—')}</span><span><b>Current Pratyantar</b>${esc(current.antardasha?.current_pratyantardasha?.lord||'—')}</span></div>`:''}
        <div class="tk-dasha-list">${(x.mahadasha||[]).map(m=>`<article><div><b>${esc(m.lord)}</b><small>${esc(new Date(m.start).toLocaleDateString('en-IN',{timeZone:state.timezone,dateStyle:'medium'}))} → ${esc(new Date(m.end).toLocaleDateString('en-IN',{timeZone:state.timezone,dateStyle:'medium'}))}</small></div><div class="tk-dasha-antar">${(m.antardasha||[]).map(a=>`<span><b>${esc(a.lord)}</b>${esc(new Date(a.start).toLocaleDateString('en-IN',{timeZone:state.timezone,year:'numeric',month:'short'}))}</span>`).join('')}</div></article>`).join('')}</div>`;
    }catch(e){if(loading)loading.textContent=e.message||'Dasha engine unavailable';toast(e.message||'Dasha engine unavailable')}
  }

  async function calculateDosha(){
    const loading=$('#tkDoshaLoading');
    if(loading){loading.hidden=false;loading.textContent='Evaluating chart…'}
    try{
      const mode=doshaModes[pageSlug],p=payload();p.time=$('#tkDoshaTime')?.value||'12:00:00';p.node_model=$('#tkDoshaNode')?.value||'mean';
      const r=await fetch(`${base}api.php?action=dosha&mode=${encodeURIComponent(mode)}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
      const j=await r.json();if(!j.ok)throw new Error(j.error||'Dosha engine unavailable');
      if(loading)loading.hidden=true;
      const x=j.result||{},el=$('#tkDoshaResult');if(!el)return;
      if(mode==='mangal'){
        const evidence=x.cancellation_evidence||[];
        el.innerHTML=`<div class="tk-jyotish-primary"><small>Base Mangal Dosha</small><h3>${x.present?(x.effective_present?'Manglik':'Manglik · cancellation evidence'):'Non-Manglik'}</h3><p>Checked from Lagna, Moon and Venus</p></div><div class="tk-jyotish-grid">${(x.checks||[]).map(c=>`<div><small>${esc(c.reference)}</small><strong>House ${c.mars_house}</strong><span>${c.afflicted?'Afflicted':'Clear'}</span></div>`).join('')}</div>${evidence.length?`<div class="tk-rule-flag">${evidence.map(e=>esc(e.description)).join(' · ')}</div>`:''}<div class="tk-lunar-note">${esc(x.note||'')}</div>`;
      }else if(mode==='kalasarpa'){
        el.innerHTML=`<div class="tk-jyotish-primary"><small>Kalasarpa Yoga</small><h3>${x.present?esc(x.type):'Not Present'}</h3><p>${x.present?esc(x.direction||''):'Not all seven classical planets lie in one Rahu–Ketu half'} · ${esc(x.node_model||'mean')} nodes</p></div>`;
      }else{
        el.innerHTML=`<div class="tk-jyotish-primary"><small>Janma Rashi</small><h3>${esc(x.moon_rashi||'—')}</h3><p>${x.current?'Current phase: '+esc(x.current.phase):'No Sade Sati phase at selected present date'}</p></div><div class="tk-dasha-list">${(x.periods||[]).map(s=>`<article><div><b>${esc(s.phase)} · ${esc(s.rashi)}</b><small>${esc(new Date(s.start).toLocaleDateString('en-IN',{timeZone:state.timezone,dateStyle:'medium'}))} → ${esc(new Date(s.end).toLocaleDateString('en-IN',{timeZone:state.timezone,dateStyle:'medium'}))}</small></div></article>`).join('')}</div>`;
      }
    }catch(e){if(loading)loading.textContent=e.message||'Dosha engine unavailable';toast(e.message||'Dosha engine unavailable')}
  }

  async function calculateAshtakavarga(){
    const loading=$('#tkAshtaLoading');
    if(loading){loading.hidden=false;loading.textContent='Building Ashtakavarga matrix…'}
    try{
      const p=payload();p.time=$('#tkAshtaTime')?.value||'12:00:00';
      const r=await fetch(`${base}api.php?action=ashtakavarga`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
      const j=await r.json();if(!j.ok)throw new Error(j.error||'Ashtakavarga engine unavailable');
      if(loading)loading.hidden=true;
      const el=$('#tkAshtaResult');if(!el)return;
      const planets=['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'];
      el.innerHTML=`<div class="tk-ashta-summary"><span><small>SAV Total</small><b>${j.sav?.total||0}</b></span><span><small>Integrity</small><b>${j.integrity?.valid?'337 ✓':'Check failed'}</b></span></div><div class="tk-ashta-table"><div class="head"><b>Rashi</b>${planets.map(p=>`<b>${esc(p.slice(0,3))}</b>`).join('')}<b>SAV</b></div>${(j.rows||[]).map(row=>`<div><strong>H${row.house} · ${esc(row.rashi)}</strong>${planets.map(p=>`<span>${row.bav?.[p]??0}</span>`).join('')}<b>${row.sav}</b></div>`).join('')}</div>`;
    }catch(e){if(loading)loading.textContent=e.message||'Ashtakavarga engine unavailable';toast(e.message||'Ashtakavarga engine unavailable')}
  }

  async function calculateVarga(){
    const loading=$('#tkVargaLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating divisional chart…'}
    try{
      const p=payload();p.time=$('#tkVargaTime')?.value||'12:00:00';p.division=Number($('#tkVargaSelect')?.value||9);
      const r=await fetch(`${base}api.php?action=vargas`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
      const j=await r.json();if(!j.ok)throw new Error(j.error||'Varga engine unavailable');
      if(loading)loading.hidden=true;
      const key='D'+p.division,ch=j.charts?.[key],el=$('#tkVargaResult');if(!el||!ch)return;
      const min=Number(ch.minimum_boundary_margin_deg||0);
      const sensitive=min<0.15;
      el.innerHTML=`<div class="tk-varga-head"><div><small>${esc(ch.key)} · ${esc(ch.name)}</small><h3>${esc(ch.theme)}</h3><p>Lagna ${esc(ch.lagna?.rashi||'—')} ${Number(ch.lagna?.degree_in_rashi||0).toFixed(2)}°</p></div><span class="${sensitive?'warning':'good'}">Nearest division boundary: ${min.toFixed(3)}°</span></div>
        <div class="tk-kundali-charts">${renderKundaliChart(ch.cells,`${ch.key} · ${ch.name}`)}</div>
        <div class="tk-varga-table">${(ch.placements||[]).map(x=>`<span><b>${esc(x.name)}${x.retrograde?' ℞':''}</b>${esc(x.rashi)} ${Number(x.degree_in_rashi).toFixed(2)}° · H${x.house}${x.vargottama?' · Vargottama':''}</span>`).join('')}</div>
        <div class="tk-lunar-note">${esc(j.note||'')}</div>`;
    }catch(e){if(loading)loading.textContent=e.message||'Varga engine unavailable';toast(e.message||'Varga engine unavailable')}
  }

  function yogaEvidence(obj){
    return Object.entries(obj||{}).map(([k,v])=>`${esc(k.replaceAll('_',' '))}: ${esc(Array.isArray(v)?v.map(x=>typeof x==='object'?JSON.stringify(x):x).join(', '):typeof v==='object'?JSON.stringify(v):v)}`).join(' · ');
  }

  async function calculateYogas(){
    const loading=$('#tkYogaLoading');
    if(loading){loading.hidden=false;loading.textContent='Detecting structural Yogas…'}
    try{
      const p=payload();p.time=$('#tkYogaTime')?.value||'12:00:00';
      const r=await fetch(`${base}api.php?action=yogas`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
      const j=await r.json();if(!j.ok)throw new Error(j.error||'Yoga engine unavailable');
      if(loading)loading.hidden=true;
      const el=$('#tkYogaResult');if(!el)return;
      const rows=j.yogas||[];
      el.innerHTML=`<div class="tk-yoga-summary"><span><small>Lagna</small><b>${esc(j.lagna?.rashi||'—')}</b></span><span><small>Detected set</small><b>${j.count||0}</b></span><span><small>Scope</small><b>Structural only</b></span></div>
        <div class="tk-yoga-list">${rows.length?rows.map(y=>`<article><div class="tk-yoga-title"><span>${esc(y.category)}</span><h4>${esc(y.name)}</h4></div><p>${esc(y.rule)}</p><small>${yogaEvidence(y.evidence)}</small>${(y.notes||[]).length?`<em>${esc(y.notes.join(' · '))}</em>`:''}</article>`).join(''):'<div class="tk-panchang-empty">No Yoga from the current curated rule set was detected.</div>'}</div>
        <div class="tk-lunar-note">${esc(j.note||'')}</div>`;
    }catch(e){if(loading)loading.textContent=e.message||'Yoga engine unavailable';toast(e.message||'Yoga engine unavailable')}
  }

  async function calculateShadbala(){
    const loading=$('#tkShadbalaLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating six-fold planetary strength…'}
    try{
      const p=payload();p.time=$('#tkShadbalaTime')?.value||'12:00:00';
      const r=await fetch(`${base}api.php?action=shadbala`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
      const j=await r.json();if(!j.ok)throw new Error(j.error||'Shadbala engine unavailable');
      if(loading)loading.hidden=true;
      const el=$('#tkShadbalaResult');if(!el)return;
      el.innerHTML=`<div class="tk-shadbala-meta"><span><small>Lagna</small><b>${esc(j.lagna?.rashi||'—')}</b></span><span><small>Unit</small><b>60 virupas = 1 Rupa</b></span><span><small>Profile</small><b>Six-fold complete</b></span></div>
        <div class="tk-shadbala-table"><div class="head"><b>Graha</b><b>Sthana</b><b>Dig</b><b>Kala</b><b>Cheshta</b><b>Nais.</b><b>Drik</b><b>Rupa</b><b>Req.</b></div>${(j.planets||[]).map(row=>{const c=row.components_virupa||{};return `<div><strong>${esc(row.planet)}</strong><span>${Number(c.sthana?.subtotal||0).toFixed(1)}</span><span>${Number(c.dig||0).toFixed(1)}</span><span>${Number(c.kala?.subtotal||0).toFixed(1)}</span><span>${Number(c.cheshta||0).toFixed(1)}</span><span>${Number(c.naisargika||0).toFixed(1)}</span><span>${Number(c.drik||0).toFixed(1)}</span><b class="${row.meets_required?'pass':'fail'}">${Number(row.total_rupa||0).toFixed(2)}</b><span>${Number(row.required_rupa||0).toFixed(1)}</span></div>`}).join('')}</div>
        <div class="tk-shadbala-details">${(j.planets||[]).map(row=>{const s=row.components_virupa?.sthana||{},k=row.components_virupa?.kala||{};return `<article><header><b>${esc(row.planet)}</b><span>${Number(row.ratio||0).toFixed(2)}× required</span></header><p>Sthana: Uchcha ${Number(s.uchcha||0).toFixed(1)} · Saptavargaja ${Number(s.saptavargaja||0).toFixed(1)} · Ojayugma ${Number(s.ojayugma||0).toFixed(1)} · Kendradi ${Number(s.kendradi||0).toFixed(1)} · Drekkana ${Number(s.drekkana||0).toFixed(1)}</p><small>Kala: Nathonnatha ${Number(k.nathonnatha||0).toFixed(1)} · Paksha ${Number(k.paksha||0).toFixed(1)} · Tribhaga ${Number(k.tribhaga||0).toFixed(1)} · Abda ${Number(k.abda||0).toFixed(0)} · Masa ${Number(k.masa||0).toFixed(0)} · Vara ${Number(k.vara||0).toFixed(0)} · Hora ${Number(k.hora||0).toFixed(0)} · Ayana ${Number(k.ayana||0).toFixed(1)} · Yuddha ${Number(k.yuddha||0).toFixed(1)}</small></article>`}).join('')}</div>
        <div class="tk-lunar-note">${esc(j.note||'')} ${esc((j.method_notes||[]).join(' · '))}</div>`;
    }catch(e){if(loading)loading.textContent=e.message||'Shadbala engine unavailable';toast(e.message||'Shadbala engine unavailable')}
  }

  function matchProfile(role){
    const cap=role[0].toUpperCase()+role.slice(1);
    const loc=matchState[role];
    const date=$('#tkMatch'+cap+'Date')?.value;
    const time=$('#tkMatch'+cap+'Time')?.value||'12:00:00';
    if(!date)throw new Error((role==='groom'?'Groom':'Bride')+' birth date is required');
    return {
      name:$('#tkMatch'+cap+'Name')?.value||'',
      date,time,
      lat:loc.lat??state.lat,lon:loc.lon??state.lon,
      city:loc.city||$('#tkMatch'+cap+'City')?.value||state.city,
      timezone:loc.timezone||state.timezone
    };
  }

  function syncMatchLocation(role){
    const cap=role[0].toUpperCase()+role.slice(1),loc=matchState[role];
    loc.lat=state.lat;loc.lon=state.lon;loc.city=state.city;loc.timezone=state.timezone;
    const input=$('#tkMatch'+cap+'City');if(input)input.value=state.city;
    const meta=$('#tkMatch'+cap+'Meta');if(meta)meta.textContent=`${state.city} · ${state.timezone}`;
  }

  async function resolveMatchCity(role,row){
    const cap=role[0].toUpperCase()+role.slice(1);
    try{
      const r=await fetch(`${base}api.php?action=timezone&lat=${encodeURIComponent(row.lat)}&lon=${encodeURIComponent(row.lon)}`);
      const j=await r.json();
      if(!j.ok||!j.timezone)throw new Error('Timezone unavailable');
      Object.assign(matchState[role],{lat:row.lat,lon:row.lon,city:row.label,timezone:j.timezone});
      const input=$('#tkMatch'+cap+'City');if(input)input.value=row.label;
      const box=$('#tkMatch'+cap+'Results');if(box)box.innerHTML='';
      const meta=$('#tkMatch'+cap+'Meta');if(meta)meta.textContent=`${row.label} · ${j.timezone}`;
    }catch(e){toast('Could not resolve birth-city timezone')}
  }

  function bindMatchCity(role){
    const cap=role[0].toUpperCase()+role.slice(1),input=$('#tkMatch'+cap+'City'),box=$('#tkMatch'+cap+'Results');
    if(!input||!box)return;
    input.addEventListener('input',()=>{
      clearTimeout(input._timer);const q=input.value.trim();
      if(q.length<2){box.innerHTML='';return}
      input._timer=setTimeout(async()=>{
        try{
          const r=await fetch(`${base}api.php?action=search&q=${encodeURIComponent(q)}`);
          const j=await r.json();
          if(!j.ok||!j.results?.length){box.innerHTML='<span>No places found</span>';return}
          box.innerHTML=j.results.map((x,i)=>`<button type="button" data-i="${i}"><b>${esc(x.label)}</b><small>${esc(x.display_name)}</small></button>`).join('');
          box._rows=j.results;
          box.querySelectorAll('button[data-i]').forEach(btn=>btn.addEventListener('click',()=>resolveMatchCity(role,box._rows[Number(btn.dataset.i)])));
        }catch(e){box.innerHTML='<span>City search unavailable</span>'}
      },260);
    });
  }

  function renderKootaMatch(j,target){
    const el=$(target);if(!el)return;
    const m=j.match||{},rows=m.kootas||[];
    const pct=Math.max(0,Math.min(100,(Number(m.total||0)/36)*100));
    const flag=(name,obj)=>obj?.present?`<span class="tk-match-flag ${obj.cancelled?'cancelled':'warning'}">${name}: ${obj.cancelled?'Dosha cancelled':'Dosha present'}</span>`:`<span class="tk-match-flag good">${name}: clear</span>`;
    const person=(title,p)=>p? `<article class="tk-match-chart"><header><small>${title}</small><strong>${esc(p.moon?.nakshatra||'—')} · ${esc(p.moon?.rashi||'—')}</strong></header>${p.lagna?`<p>Lagna <b>${esc(p.lagna.rashi)}</b> · Mangal <b>${p.mangal?.present?'Manglik':'Non-Manglik'}</b></p><p>Dasha <b>${esc(p.dasha?.mahadasha||'—')} / ${esc(p.dasha?.antardasha||'—')}</b></p>`:''}</article>`:'';
    el.innerHTML=`<section class="tk-match-score"><div class="tk-match-score-ring" style="--score:${pct}%"><strong>${Number(m.total||0).toFixed(1)}</strong><span>/ 36</span></div><div><small>Ashtakoota result</small><h3>${esc(String(m.band||'').replaceAll('-',' '))}</h3><p>${esc(m.band_reason||'')}</p><div class="tk-match-flags">${flag('Bhakoot',m.bhakoot)}${flag('Nadi',m.nadi)}</div></div></section>
      <div class="tk-koota-list">${rows.map(r=>`<article><div><b>${esc(r.name)}</b><small>${esc(r.basis||'')}</small></div><div class="tk-koota-meter"><i style="width:${Math.max(0,Math.min(100,(Number(r.earned||0)/Number(r.maximum||1))*100))}%"></i></div><strong>${Number(r.earned||0).toFixed(1)} / ${Number(r.maximum||0).toFixed(0)}</strong></article>`).join('')}</div>
      ${j.mode==='horoscope'?`<div class="tk-match-charts">${person('Vara / Groom',j.groom)}${person('Kanya / Bride',j.bride)}</div><div class="tk-rule-flag ${j.integration?.mangal_compatible?'':'is-warning'}">Mangal compatibility: ${esc(j.integration?.mangal_note||'—')}</div>`:''}
      ${compactDeepAnalysis(j.integration?.deep_analysis)}
      <div class="tk-lunar-note">${esc(j.note||'')}</div>`;
  }

  function compactDeepAnalysis(deep){
    if(!deep)return '';
    const g=deep.groom||{},b=deep.bride||{},p=deep.pair||{};
    const relation=x=>esc((x||'—').replaceAll('-',' '));
    return `<section class="tk-match-deep-compact">
      <header><small>Beyond 36 Gunas</small><h4>D1 / D9 marriage structure</h4></header>
      <div class="tk-match-deep-grid">
        <div><small>Vara 7th lord</small><b>${esc(g.d1?.seventh_lord||'—')}</b><span>H${g.d1?.seventh_lord_house||'—'} · D9 ${esc(g.d9?.seventh_lord||'—')}</span></div>
        <div><small>Kanya 7th lord</small><b>${esc(b.d1?.seventh_lord||'—')}</b><span>H${b.d1?.seventh_lord_house||'—'} · D9 ${esc(b.d9?.seventh_lord||'—')}</span></div>
        <div><small>D9 Lagna relation</small><b>${relation(p.d9_lagna?.label)}</b><span>${esc(g.d9?.lagna?.rashi||'—')} × ${esc(b.d9?.lagna?.rashi||'—')}</span></div>
        <div><small>Dasha overlaps</small><b>${deep.dasha_overlap?.windows?.length||0}</b><span>Candidate windows in ${deep.dasha_overlap?.horizon_years||12} years</span></div>
      </div>
    </section>`;
  }

  function renderMarriageAnalysis(j,target='#tkMarriageResult'){
    const el=$(target);if(!el)return;
    const g=j.groom||{},b=j.bride||{},pair=j.pair||{},m=j.mangal||{};
    const person=(title,p)=>`<article class="tk-marriage-person">
      <header><small>${title}</small><h4>${esc(p.name||p.location?.city||'Birth chart')}</h4></header>
      <div class="tk-marriage-facts">
        <span><small>D1 Lagna</small><b>${esc(p.lagna?.rashi||'—')}</b></span>
        <span><small>7th house</small><b>${esc(p.d1?.seventh_sign||'—')}</b><em>Lord ${esc(p.d1?.seventh_lord||'—')} · H${p.d1?.seventh_lord_house||'—'}</em></span>
        <span><small>D9 Lagna</small><b>${esc(p.d9?.lagna?.rashi||'—')}</b></span>
        <span><small>D9 7th lord</small><b>${esc(p.d9?.seventh_lord||'—')}</b><em>H${p.d9?.seventh_lord_house||'—'} · ${esc(p.d9?.seventh_lord_rashi||'—')}</em></span>
        <span><small>Venus</small><b>${esc(p.significators?.venus?.rashi||'—')}</b><em>H${p.significators?.venus?.house||'—'} · D9 ${esc(p.significators?.venus_d9?.rashi||'—')}</em></span>
        <span><small>Jupiter</small><b>${esc(p.significators?.jupiter?.rashi||'—')}</b><em>H${p.significators?.jupiter?.house||'—'} · D9 ${esc(p.significators?.jupiter_d9?.rashi||'—')}</em></span>
      </div>
      <div class="tk-marriage-mangal ${p.mangal?.effective_present?'warning':'good'}"><b>Base Mangal: ${p.mangal?.present?'Present':'Clear'}</b><span>After conservative cancellation profile: ${p.mangal?.effective_present?'Still active':'Clear / mitigated'}</span>${(p.mangal?.cancellation_evidence||[]).map(x=>`<small>${esc(x.description)}</small>`).join('')}</div>
    </article>`;

    const windows=(j.dasha_overlap?.windows||[]);
    el.innerHTML=`<div class="tk-marriage-two">${person('Vara / Groom',g)}${person('Kanya / Bride',b)}</div>
      <section class="tk-marriage-pair">
        <header><small>Pair comparison</small><h4>No added score — evidence only</h4></header>
        <div class="tk-match-deep-grid">
          <div><small>D1 7th lords</small><b>${esc(pair.seventh_lords?.groom||'—')} × ${esc(pair.seventh_lords?.bride||'—')}</b><span>${esc(pair.seventh_lords?.groom_to_bride_relation||'—')} / ${esc(pair.seventh_lords?.bride_to_groom_relation||'—')}</span></div>
          <div><small>D9 7th lords</small><b>${esc(pair.d9_seventh_lords?.groom||'—')} × ${esc(pair.d9_seventh_lords?.bride||'—')}</b><span>${esc(pair.d9_seventh_lords?.groom_to_bride_relation||'—')} / ${esc(pair.d9_seventh_lords?.bride_to_groom_relation||'—')}</span></div>
          <div><small>D9 Lagna relation</small><b>${esc(pair.d9_lagna?.label||'—')}</b><span>Whole-sign relationship</span></div>
          <div><small>Venus relation</small><b>${esc(pair.venus?.sign_relation?.label||'—')}</b><span>D9 ${esc(pair.venus?.d9_sign_relation?.label||'—')}</span></div>
          <div><small>Jupiter relation</small><b>${esc(pair.jupiter?.sign_relation?.label||'—')}</b><span>D9 ${esc(pair.jupiter?.d9_sign_relation?.label||'—')}</span></div>
          <div><small>Mangal pair</small><b>${m.mutual_manglik?'Mutual Manglik':m.effective_mismatch?'Mismatch remains':'No effective mismatch'}</b><span>${(m.pair_cancellation_evidence||[]).map(x=>esc(x.rule)).join(' · ')||'Conservative profile'}</span></div>
        </div>
      </section>
      <section class="tk-marriage-dasha"><header><small>Vimshottari overlap</small><h4>Candidate simultaneous periods</h4><p>${esc(j.dasha_overlap?.rule||'')}</p></header>
        <div class="tk-marriage-windows">${windows.length?windows.map(w=>`<article><div><b>${esc(new Date(w.start).toLocaleDateString('en-IN',{dateStyle:'medium'}))} → ${esc(new Date(w.end).toLocaleDateString('en-IN',{dateStyle:'medium'}))}</b><small>${Math.round(w.duration_days)} days · strength ${w.combined_strength}/4</small></div><span>Vara ${esc(w.groom?.mahadasha||'—')}/${esc(w.groom?.antardasha||'—')} · Kanya ${esc(w.bride?.mahadasha||'—')}/${esc(w.bride?.antardasha||'—')}</span></article>`).join(''):'<div class="tk-panchang-empty">No overlap windows under this specific rule profile.</div>'}</div>
      </section>
      <div class="tk-lunar-note">${esc(j.disclaimer||'')}</div>`;
  }

  async function calculateMarriageAnalysis(){
    const loading=$('#tkMarriageLoading');if(loading){loading.hidden=false;loading.textContent='Comparing D1, D9, Mangal and Dasha periods…'}
    try{
      const body={
        groom:matchProfile('groom'),bride:matchProfile('bride'),
        horizon_years:Number($('#tkMarriageHorizon')?.value||12)
      };
      const r=await fetch(`${base}api.php?action=marriage-analysis`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      const j=await r.json();if(!j.ok)throw new Error(j.error||'Marriage analysis unavailable');
      if(loading)loading.hidden=true;renderMarriageAnalysis(j);
    }catch(e){if(loading){loading.hidden=false;loading.textContent=e.message||'Marriage analysis unavailable'};toast(e.message||'Marriage analysis unavailable')}
  }

  async function calculateHoroscopeMatch(){
    const loading=$('#tkMatchLoading');if(loading){loading.hidden=false;loading.textContent='Calculating both birth charts and Ashtakoota…'}
    try{
      const body={mode:'horoscope',groom:matchProfile('groom'),bride:matchProfile('bride')};
      const r=await fetch(`${base}api.php?action=matching&mode=horoscope`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      const j=await r.json();if(!j.ok)throw new Error(j.error||'Matching engine unavailable');
      if(loading)loading.hidden=true;renderKootaMatch(j,'#tkMatchResult');
    }catch(e){if(loading){loading.hidden=false;loading.textContent=e.message||'Matching engine unavailable'};toast(e.message||'Matching engine unavailable')}
  }

  async function calculateNakshatraMatch(){
    const loading=$('#tkNakMatchLoading');if(loading){loading.hidden=false;loading.textContent='Calculating Nakshatra compatibility…'}
    try{
      const body={mode:'nakshatra',groom:{nakshatra:$('#tkNakGroom')?.value,pada:Number($('#tkNakGroomPada')?.value||1)},bride:{nakshatra:$('#tkNakBride')?.value,pada:Number($('#tkNakBridePada')?.value||1)}};
      const r=await fetch(`${base}api.php?action=matching&mode=nakshatra`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      const j=await r.json();if(!j.ok)throw new Error(j.error||'Nakshatra matching unavailable');
      if(loading)loading.hidden=true;renderKootaMatch(j,'#tkNakMatchResult');
    }catch(e){if(loading){loading.hidden=false;loading.textContent=e.message||'Nakshatra matching unavailable'};toast(e.message||'Nakshatra matching unavailable')}
  }

  function initMatching(){
    if(matchPages.includes(pageSlug)||marriagePages.includes(pageSlug)){
      bindMatchCity('groom');bindMatchCity('bride');
      document.querySelectorAll('[data-match-use-current]').forEach(btn=>btn.addEventListener('click',()=>syncMatchLocation(btn.dataset.matchUseCurrent)));
    }
    if(nakMatchPages.includes(pageSlug)){
      ['#tkNakGroom','#tkNakBride'].forEach(sel=>{const el=$(sel);if(el)el.innerHTML=NAKSHATRAS.map(n=>`<option value="${esc(n)}">${esc(n)}</option>`).join('')});
    }
  }

  async function calculateLagna(){
    const loading=$('#tkLagnaLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating Lagna periods…'}
    try{
      const r=await fetch(`${base}api.php?action=lagna`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload())
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate Lagna');
      if(loading)loading.hidden=true;
      const list=$('#tkLagnaList');if(!list)return;
      list.innerHTML=(j.timeline||[]).map(row=>`<article class="tk-observance-event">
        <div class="tk-observance-date"><b>${esc(row.lagna)}</b><span>${Number(row.degree_in_sign||0).toFixed(1)}°</span></div>
        <div class="tk-observance-main"><h4>${esc(row.start_label)} – ${esc(row.end_label)}</h4><p>${Math.round(row.duration_minutes)} minutes</p><small>Sidereal ascendant · Lahiri/Chitrapaksha</small></div>
      </article>`).join('');
    }catch(e){if(loading)loading.textContent=e.message||'Lagna engine unavailable';toast(e.message||'Lagna engine unavailable')}
  }

  async function calculateObservances(){
    const loading=$('#tkObservanceLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating yearly observances…'}
    try{
      const kind=observanceKinds[pageSlug];
      const p=payload();
      const cacheKey=`${kind}|${p.date.slice(0,4)}|${Number(p.lat).toFixed(5)}|${Number(p.lon).toFixed(5)}|${p.timezone}`;
      if(state.observanceCache.has(cacheKey)){
        renderObservances(state.observanceCache.get(cacheKey));
        return;
      }
      const r=await fetch(`${base}api.php?action=observances&kind=${encodeURIComponent(kind)}`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate observances');
      state.observanceCache.set(cacheKey,j);
      renderObservances(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Observance engine unavailable'}
      toast(e.message||'Observance engine unavailable');
    }
  }

  function renderObservances(d){
    const loading=$('#tkObservanceLoading');if(loading)loading.hidden=true;
    const note=$('#tkObservanceNote');if(note)note.textContent=d.note||'';
    const title=$('#tkObservanceTitle');
    if(title)title.textContent=`${title.textContent.replace(/\s+\d{4}$/,'')} ${d.year}`;
    const list=$('#tkObservanceList');if(!list)return;

    let rows=d.events||[];
    if(pageSlug==='festivals/maha-shivaratri'){
      rows=rows.filter(row=>row.maha_shivaratri);
    }
    if(!rows.length){
      list.innerHTML='<div class="tk-panchang-empty">No observances found for this year.</div>';
      return;
    }

    list.innerHTML=rows.map(row=>{
      let timing='';
      let detail='';
      if(d.kind==='pradosh'){
        timing=`${esc(row.puja?.start_label||'—')} – ${esc(row.puja?.end_label||'—')}`;
        detail=`Sunset ${esc(row.sunset_label||'—')} · ${esc(row.paksha||'')}`;
      }else if(d.kind==='sankashti'){
        timing=`Moonrise ${esc(row.moonrise_label||'—')}`;
        detail=`${row.angarki?'Angarki · ':''}${esc(row.paksha||'')} · ${esc(row.amanta_month||'')}`;
      }else{
        timing=`Nishita ${esc(row.nishita?.start_label||'—')} – ${esc(row.nishita?.end_label||'—')}`;
        detail=`${esc(row.amanta_month||'')} · ${esc(row.purnimanta_month||'')}`;
      }

      return `<article class="tk-observance-event${row.maha_shivaratri?' is-major':''}">
        <div class="tk-observance-date"><b>${esc(row.date)}</b><span>${esc(row.weekday||'')}</span></div>
        <div class="tk-observance-main">
          <h4>${esc(row.name||row.observance||'Observance')}</h4>
          <p>${timing}</p>
          <small>${detail}</small>
        </div>
        <a href="${base}panchang/daily/?date=${encodeURIComponent(row.date)}">Panchang →</a>
      </article>`;
    }).join('');
  }

  async function calculateFestival(){
    const loading=$('#tkFestivalLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating festival rule…'}
    try{
      const kind=festivalKinds[pageSlug];
      const p=payload();
      const cacheKey=`${kind}|${p.date.slice(0,4)}|${Number(p.lat).toFixed(5)}|${Number(p.lon).toFixed(5)}|${p.timezone}`;
      if(state.festivalCache.has(cacheKey)){
        renderFestival(state.festivalCache.get(cacheKey));
        return;
      }
      const r=await fetch(`${base}api.php?action=festival&kind=${encodeURIComponent(kind)}`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate festival');
      state.festivalCache.set(cacheKey,j);
      renderFestival(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Festival engine unavailable'}
      toast(e.message||'Festival engine unavailable');
    }
  }

  function renderFestival(d){
    const loading=$('#tkFestivalLoading');if(loading)loading.hidden=true;
    const note=$('#tkFestivalNote');if(note)note.textContent=d.note||'';
    const el=$('#tkFestivalResult');if(!el)return;
    const row=d.event;
    if(!row){
      el.innerHTML='<div class="tk-panchang-empty">No matching festival rule found for this year.</div>';
      return;
    }
    const title=$('#tkFestivalTitle');
    if(title)title.textContent=`${row.title} ${d.year}`;
    const timings=[];
    if(row.puja)timings.push(['Puja',row.puja.start_label+' – '+row.puja.end_label]);
    if(row.thread_ceremony)timings.push(['Thread ceremony',row.thread_ceremony.start_label+' – '+row.thread_ceremony.end_label]);
    if(row.ghatasthapana)timings.push(['Ghatasthapana',row.ghatasthapana.start_label+' – '+row.ghatasthapana.end_label]);
    if(row.vijay_muhurat)timings.push(['Vijay Muhurat',row.vijay_muhurat.start_label+' – '+row.vijay_muhurat.end_label]);
    if(row.aparahna)timings.push(['Aparahna',row.aparahna.start_label+' – '+row.aparahna.end_label]);
    if(row.pradosh)timings.push(['Pradosh',row.pradosh.start_label+' – '+row.pradosh.end_label]);
    if(row.lakshmi_puja)timings.push(['Lakshmi Puja',row.lakshmi_puja.start_label+' – '+row.lakshmi_puja.end_label]);
    if(row.vrishabha_lagna)timings.push(['Vrishabha Lagna',row.vrishabha_lagna.start_label+' – '+row.vrishabha_lagna.end_label]);
    if(row.nishita)timings.push(['Nishita Puja',row.nishita.start_label+' – '+row.nishita.end_label]);
    if(row.sandhi_puja)timings.push(['Sandhi Puja',row.sandhi_puja.start_label+' – '+row.sandhi_puja.end_label]);
    if(row.vaishnava_date&&row.vaishnava_date!==row.date)timings.push(['Vaishnava observance',row.vaishnava_date]);
    if(row.parana?.after_label)timings.push(['Parana','After '+row.parana.after_label]);
    if(row.dahi_handi_date)timings.push(['Dahi Handi',row.dahi_handi_date]);
    if(row.moonrise_label)timings.push(['Moonrise',row.moonrise_label]);
    if(row.upavasa)timings.push(['Upavasa',row.upavasa.start_label+' – '+row.upavasa.end_label]);
    if(row.rangwali_holi_date)timings.push(['Rangwali Holi',row.rangwali_holi_date]);
    const pending=[];
    if(row.vrishabha_lagna_status&&row.vrishabha_lagna_status!=='verified')pending.push('Vrishabha Lagna refinement pending');
    if(row.puja_muhurat_status)pending.push('Evening Puja refinement pending');
    el.innerHTML=`<article class="tk-festival-card">
      <div class="tk-festival-date"><b>${esc(row.date)}</b><span>${esc(row.weekday||'')}</span></div>
      <div class="tk-festival-main">
        <h4>${esc(row.title)}</h4>
        <p>${esc(row.month)} · ${esc(row.paksha)} · ${esc(row.tithi_start_label)} → ${esc(row.tithi_end_label)}</p>
        <div class="tk-festival-times">${timings.map(([k,v])=>`<span><b>${esc(k)}</b>${esc(v)}</span>`).join('')}</div>
        ${pending.length?`<small>${pending.map(esc).join(' · ')}</small>`:''}
      </div>
      <a href="${base}panchang/daily/?date=${encodeURIComponent(row.date)}">Daily Panchang →</a>
    </article>`;
  }

  async function calculateDwadashi(){
    const loading=$('#tkDwadashiLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating Dwadashi observances…'}
    try{
      const p=payload();
      const cacheKey=`${p.date.slice(0,4)}|${Number(p.lat).toFixed(5)}|${Number(p.lon).toFixed(5)}|${p.timezone}`;
      if(state.dwadashiCache.has(cacheKey)){
        renderDwadashi(state.dwadashiCache.get(cacheKey));
        return;
      }
      const r=await fetch(`${base}api.php?action=dwadashi`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate Dwadashi');
      state.dwadashiCache.set(cacheKey,j);
      renderDwadashi(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Dwadashi engine unavailable'}
      toast(e.message||'Dwadashi engine unavailable');
    }
  }

  function renderDwadashi(d){
    const loading=$('#tkDwadashiLoading');if(loading)loading.hidden=true;
    const title=$('#tkDwadashiTitle');if(title)title.textContent=`Dwadashi Dates ${d.year}`;
    const note=$('#tkDwadashiNote');if(note)note.textContent=d.note||'';
    const list=$('#tkDwadashiList');if(!list)return;
    const rows=d.events||[];
    if(!rows.length){
      list.innerHTML='<div class="tk-panchang-empty">No Dwadashi observances found for this year.</div>';
      return;
    }
    list.innerHTML=rows.map(row=>{
      const parana=row.parana;
      const paranaText=parana
        ? `Parana ${esc(parana.start_label||'—')} – ${esc(parana.end_label||'—')}`
        : 'Parana unavailable';
      const special=row.vishnushrinkhala_candidate
        ? '<span class="tk-rule-flag">Special Parana review</span>'
        : '';
      return `<article class="tk-dwadashi-event">
        <div class="tk-dwadashi-date"><b>${esc(row.date)}</b><span>${esc(row.weekday||'')}</span></div>
        <div class="tk-dwadashi-main">
          <div class="tk-dwadashi-title"><h4>${esc(row.name)}</h4>${special}</div>
          <p>${esc(row.paksha||'')} · ${esc(row.purnimanta_month||'')} · ${esc(row.tithi_start_label||'—')} → ${esc(row.tithi_end_label||'—')}</p>
          <small>${paranaText}${row.aliases?.length?' · '+row.aliases.map(esc).join(' · '):''}</small>
        </div>
        <a href="${base}panchang/daily/?date=${encodeURIComponent(row.date)}">Panchang →</a>
      </article>`;
    }).join('');
  }

  async function calculateMahadwadashi(){
    const loading=$('#tkMahadwadashiLoading');
    if(loading){loading.hidden=false;loading.textContent='Detecting Mahadwadashi yogas…'}
    try{
      const p=payload();
      const cacheKey=`${p.date.slice(0,4)}|${Number(p.lat).toFixed(5)}|${Number(p.lon).toFixed(5)}|${p.timezone}`;
      if(state.mahadwadashiCache.has(cacheKey)){
        renderMahadwadashi(state.mahadwadashiCache.get(cacheKey));
        return;
      }
      const r=await fetch(`${base}api.php?action=mahadwadashi`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to classify Mahadwadashi');
      state.mahadwadashiCache.set(cacheKey,j);
      renderMahadwadashi(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Mahadwadashi engine unavailable'}
      toast(e.message||'Mahadwadashi engine unavailable');
    }
  }

  function renderMahadwadashi(d){
    const loading=$('#tkMahadwadashiLoading');if(loading)loading.hidden=true;
    const title=$('#tkMahadwadashiTitle');if(title)title.textContent=`Mahadwadashi ${d.year}`;
    const note=$('#tkMahadwadashiNote');if(note)note.textContent=d.note||'';
    const list=$('#tkMahadwadashiList');if(!list)return;
    const rows=d.events||[];
    if(!rows.length){
      list.innerHTML='<div class="tk-panchang-empty">No Mahadwadashi combinations detected for this year.</div>';
      return;
    }
    list.innerHTML=rows.map(row=>`<article class="tk-mahadwadashi-event">
      <div class="tk-mahadwadashi-date"><b>${esc(row.date)}</b><span>${esc(row.weekday||'')}</span></div>
      <div class="tk-mahadwadashi-main">
        <div class="tk-mahadwadashi-tags">${(row.yogas||[]).map(y=>`<span>${esc(y)}</span>`).join('')}</div>
        <p>${esc(row.paksha||'')} · ${esc(row.amanta_month||'')} · Dwadashi ${esc(row.dwadashi_start_label||'—')} → ${esc(row.dwadashi_end_label||'—')}</p>
        <small>Rule evidence retained: local sunrise/sunset, Tithi spans and Nakshatra state.</small>
      </div>
      <a href="${base}panchang/daily/?date=${encodeURIComponent(row.date)}">Panchang →</a>
    </article>`).join('');
  }

  async function calculateSankranti(){
    const loading=$('#tkSankrantiLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating yearly Sankranti moments…'}
    try{
      const p=payload();
      const cacheKey=`${p.date.slice(0,4)}|${Number(p.lat).toFixed(5)}|${Number(p.lon).toFixed(5)}|${p.timezone}`;
      if(state.sankrantiCache.has(cacheKey)){
        renderSankranti(state.sankrantiCache.get(cacheKey));
        return;
      }
      const r=await fetch(`${base}api.php?action=sankranti`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate Sankranti');
      state.sankrantiCache.set(cacheKey,j);
      renderSankranti(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Sankranti engine unavailable'}
      toast(e.message||'Sankranti engine unavailable');
    }
  }

  function renderSankranti(d){
    const loading=$('#tkSankrantiLoading');if(loading)loading.hidden=true;
    const title=$('#tkSankrantiTitle');
    if(title)title.textContent=`${pageSlug==='festivals/makar-sankranti'?'Makar Sankranti':'Sankranti'} ${d.year}`;
    const note=$('#tkSankrantiNote');if(note)note.textContent=d.note||'';
    const list=$('#tkSankrantiList');if(!list)return;

    let rows=d.events||[];
    if(pageSlug==='festivals/makar-sankranti'){
      const makara=rows.find(row=>row.rashi==='Makara');
      rows=makara?[makara]:[];
    }
    if(!rows.length){
      list.innerHTML='<div class="tk-panchang-empty">No Sankranti events found for this year.</div>';
      return;
    }

    list.innerHTML=rows.map(row=>`<article class="tk-sankranti-event${row.rashi==='Makara'?' is-makara':''}">
      <div class="tk-sankranti-rashi"><small>${esc(row.from_rashi)} →</small><strong>${esc(row.to_rashi)}</strong></div>
      <div class="tk-sankranti-main">
        <h4>${esc(row.name)}</h4>
        <p>${esc(row.weekday)} · ${esc(row.date_label)} · ${esc(row.time_label||'—')}</p>
        <small>${row.daylight_ingress?'Ingress during local daylight':'Ingress outside local daylight'} · Sunrise ${esc(row.sunrise_label||'—')} · Sunset ${esc(row.sunset_label||'—')}</small>
      </div>
      <a href="${base}panchang/daily/?date=${encodeURIComponent(row.date)}">Panchang →</a>
    </article>`).join('');
  }

  async function calculateSeasons(){
    const loading=$('#tkSeasonLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating equinoxes and solstices…'}
    try{
      const r=await fetch(`${base}api.php?action=seasons`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(payload())
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate seasonal events');
      renderSeasons(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Season engine unavailable'}
      toast(e.message||'Season engine unavailable');
    }
  }

  function renderSeasons(d){
    const loading=$('#tkSeasonLoading');if(loading)loading.hidden=true;
    const key=seasonKinds[pageSlug];
    const event=d.events?.[key];
    const set=(id,val)=>{const el=$(id);if(el)el.textContent=val};
    if(event){
      set('#tkSeasonTitle',event.name);
      set('#tkSeasonWeekday',event.weekday);
      set('#tkSeasonResult',`${event.date_label} · ${event.time_label}`);
      set('#tkSeasonMeta',`Displayed in ${d.timezone} for the selected location.`);
    }
    const all=$('#tkSeasonAll');if(!all)return;
    all.innerHTML=Object.entries(d.events||{}).map(([k,row])=>`
      <div class="tk-season-row${k===key?' is-current':''}">
        <div><small>${esc(row.weekday)}</small><strong>${esc(row.name)}</strong></div>
        <span>${esc(row.date_label)} · ${esc(row.time_label)}</span>
      </div>`).join('');
  }

  async function calculateLunarOccurrences(){
    const loading=$('#tkLunarLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating yearly lunar occurrences…'}
    try{
      const kind=lunarKinds[pageSlug];
      const p=payload();
      const cacheKey=`${kind}|${p.date.slice(0,4)}|${Number(p.lat).toFixed(5)}|${Number(p.lon).toFixed(5)}|${p.timezone}`;
      if(state.lunarCache.has(cacheKey)){
        renderLunarOccurrences(state.lunarCache.get(cacheKey));
        return;
      }
      const r=await fetch(`${base}api.php?action=lunar-occurrences&kind=${encodeURIComponent(kind)}`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate lunar occurrences');
      state.lunarCache.set(cacheKey,j);
      renderLunarOccurrences(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Lunar occurrence engine unavailable'}
      toast(e.message||'Lunar occurrence engine unavailable');
    }
  }

  function renderLunarOccurrences(d){
    const loading=$('#tkLunarLoading');if(loading)loading.hidden=true;
    const note=$('#tkLunarNote');if(note)note.textContent=d.note||'';
    const title=$('#tkLunarTitle');if(title)title.textContent=`${title.textContent.replace(/\s+\d{4}$/,'')} ${d.year}`;
    const list=$('#tkLunarList');if(!list)return;
    if(!d.events?.length){
      list.innerHTML='<div class="tk-panchang-empty">No occurrences found for this year.</div>';
      return;
    }
    const fmtDate=iso=>new Intl.DateTimeFormat('en-US',{
      timeZone:state.timezone,month:'short',day:'numeric',weekday:'short'
    }).format(new Date(iso));
    list.innerHTML=d.events.map(row=>{
      const candidateRows=(row.sunrise_candidates||[]).map(x=>{
        const parana=x.parana;
        const paranaText=parana
          ? `Parana: after ${esc(parana.earliest_label||parana.next_sunrise_label||'sunrise')}${parana.deadline_label ? ` · before ${esc(parana.deadline_label)}` : ' · Dwadashi ended before sunrise'}`
          : '';
        return `<div class="tk-lunar-candidate">
          <div><b>${esc(x.weekday.slice(0,3))} ${esc(x.date)}</b><span>Sunrise ${esc(x.sunrise_label||'—')}</span></div>
          ${paranaText ? `<small>${paranaText}</small>` : ''}
        </div>`;
      }).join('');
      const obs=row.observance;
      const selection=obs ? `<div class="tk-ekadashi-selection">
        <span><b>Smarta</b>${esc(obs.smarta?.date||'—')}</span>
        <span><b>Vaishnava</b>${esc(obs.vaishnava?.date||'—')}</span>
      </div>` : '';
      return `<article class="tk-lunar-event">
        <div class="tk-lunar-event-date"><b>${esc(fmtDate(row.start))}</b><span>${esc(row.paksha||'')}</span></div>
        <div class="tk-lunar-event-main">
          <h4>${esc(row.name)}</h4>
          <p>${esc(row.amanta_month||'')} · ${esc(row.start_label)} → ${esc(row.end_label)}</p>
          ${selection}
          ${candidateRows ? `<div class="tk-lunar-candidates">${candidateRows}</div>` : '<small>No sunrise falls inside this Tithi window</small>'}
        </div>
      </article>`;
    }).join('');
  }

  async function calculateMonth(){
    const loading=$('#tkMonthLoading');
    if(loading){loading.hidden=false;loading.textContent='Building month Panchang…'}
    try{
      const p=payload();
      const cacheKey=`${p.date.slice(0,7)}|${Number(p.lat).toFixed(5)}|${Number(p.lon).toFixed(5)}|${p.timezone}`;
      if(state.monthData&&state.monthKey===cacheKey){
        renderMonth(state.monthData);
        return;
      }
      const r=await fetch(`${base}api.php?action=panchang-month`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(p)
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate Month Panchang');
      state.monthData=j;
      state.monthKey=cacheKey;
      renderMonth(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Month Panchang unavailable'}
      toast(e.message||'Month Panchang unavailable');
    }
  }

  function renderMonth(d){
    const loading=$('#tkMonthLoading');if(loading)loading.hidden=true;
    const title=$('#tkMonthTitle');if(title)title.textContent=`${d.month_name} ${d.year}`;
    const engine=$('#tkMonthEngine');if(engine)engine.textContent=`${d.engine?.ayanamsha||'Lahiri'} · Month engine`;
    const grid=$('#tkMonthGrid');if(!grid)return;
    const selectedDate=payload().date;
    const selectedRow=(d.days||[]).find(row=>row.date===selectedDate);
    const selection=$('#tkMonthSelection');
    if(selection)selection.textContent=selectedRow?.available
      ? `${selectedRow.weekday}, ${selectedRow.date} · ${selectedRow.tithi} · ${selectedRow.nakshatra}`
      : `Selected date: ${selectedDate}`;
    const dailyLink=$('#tkMonthDailyLink');
    if(dailyLink)dailyLink.href=`${base}panchang/daily/?date=${encodeURIComponent(selectedDate)}`;
    const blanks=Math.max(0,Number(d.first_weekday||0));
    let html=Array.from({length:blanks},()=>'<div class="tk-month-day is-empty"></div>').join('');
    html+=(d.days||[]).map(row=>{
      if(!row.available)return `<div class="tk-month-day is-unavailable"><b>${row.day}</b><small>Unavailable</small></div>`;
      const special=row.tithi==='Ekadashi'?' ekadashi':row.tithi==='Purnima'?' purnima':row.tithi==='Amavasya'?' amavasya':'';
      const selected=selectedDate===row.date?' is-selected':'';
      return `<button type="button" class="tk-month-day${special}${selected}" data-month-date="${esc(row.date)}">
        <span class="tk-month-day-top"><b>${row.day}</b><em>${esc(row.weekday_short||'')}</em></span>
        <strong>${esc(row.tithi||'—')}</strong>
        <small>${esc(row.paksha||'')}</small>
        <span class="tk-month-nak">${esc(row.nakshatra||'—')}</span>
      </button>`;
    }).join('');
    grid.innerHTML=html;
    grid.querySelectorAll('[data-month-date]').forEach(btn=>btn.addEventListener('click',()=>{
      const input=$('#tkDate');if(!input)return;
      input.value=btn.dataset.monthDate;
      state.dateTouched=true;
      calculate();
    }));
  }

  async function calculatePanchang(){
    const loading=$('#tkPanchangLoading');
    if(loading){loading.hidden=false;loading.textContent='Calculating sidereal Panchang…'}
    try{
      const r=await fetch(`${base}api.php?action=panchang`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(payload())
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate Panchang');
      state.panchang=j;renderPanchang(j);
    }catch(e){
      if(loading){loading.hidden=false;loading.textContent=e.message||'Panchang engine unavailable'}
      toast(e.message||'Panchang engine unavailable');
    }
  }

  function renderPanchang(d){
    const set=(id,val)=>{const el=$(id);if(el)el.textContent=val};
    const loading=$('#tkPanchangLoading');if(loading)loading.hidden=true;
    const s=d.sunrise_state||{};
    set('#tkTithiName',s.tithi||'—');
    set('#tkTithiMeta',`${s.paksha||''} · Tithi ${s.tithi_number||''}`);
    set('#tkNakshatraName',s.nakshatra||'—');
    set('#tkYogaName',s.yoga||'—');
    set('#tkKaranaName',s.karana||'—');
    set('#tkPakshaName',d.paksha||'—');
    set('#tkMoonRashi',d.moon_rashi||'—');
    set('#tkSunRashi',d.sun_rashi||'—');
    set('#tkAmantaMonth',d.lunar_month?.amanta||'—');
    set('#tkPurnimantaMonth',d.lunar_month?.purnimanta||'—');
    set('#tkMoonrise',d.moonrise_label||'—');
    set('#tkMoonset',d.moonset_label||'—');
    set('#tkEngineMeta',`${d.engine?.ayanamsha||'Lahiri'} · ${d.engine?.astronomy||d.engine?.ephemeris||'Astronomy Engine'}`);
    const range=v=>v ? `${v.start_label} – ${v.end_label}` : '—';
    set('#tkMuhuratAbhijit',range(d.muhurtas?.abhijit));
    set('#tkMuhuratVijaya',range(d.muhurtas?.vijaya));
    set('#tkMuhuratBrahma',range(d.muhurtas?.brahma));
    set('#tkMuhuratGodhuli',range(d.muhurtas?.godhuli));
    set('#tkMuhuratPratah',range(d.muhurtas?.pratah_sandhya));
    set('#tkMuhuratSayahna',range(d.muhurtas?.sayahna_sandhya));
    set('#tkMuhuratNishita',range(d.muhurtas?.nishita));
    set('#tkMuhuratYamaganda',range(d.muhurtas?.yamaganda));
    set('#tkMuhuratGulika',range(d.muhurtas?.gulika));

    renderSinglePage(d);
    renderTransitions('#tkTithiTransitions',d.tithi,'Tithi');
    renderTransitions('#tkNakshatraTransitions',d.nakshatra,'Nakshatra');
    renderTransitions('#tkYogaTransitions',d.yoga,'Yoga');
    renderTransitions('#tkKaranaTransitions',d.karana,'Karana');
  }

  function renderSinglePage(d){
    const set=(id,val)=>{const el=$(id);if(el)el.textContent=val};
    const range=v=>v ? `${v.start_label} – ${v.end_label}` : '—';
    if(pageSlug==='panchang/moonrise-moonset'){
      set('#tkSinglePrimary','Moonrise & Moonset');
      set('#tkSingleSecondary',`Moonrise ${d.moonrise_label||'—'} · Moonset ${d.moonset_label||'—'}`);
      set('#tkSingleMeta',`${d.date_label} · ${d.location?.city||'Selected location'}`);
    }
    if(pageSlug==='panchang/rahu-kala'||pageSlug==='muhurat/rahu-kala'){
      set('#tkSinglePrimary','Rahu Kala');
      set('#tkSingleSecondary',range(d.muhurtas?.rahu_kaal));
      set('#tkSingleMeta','Sunrise-to-sunset period divided into eight weekday-specific segments.');
    }
    if(pageSlug==='muhurat/abhijit'){
      set('#tkSinglePrimary','Abhijit Muhurat');
      set('#tkSingleSecondary',range(d.muhurtas?.abhijit));
      set('#tkSingleMeta','The central daytime Muhurta, calculated from the local sunrise-to-sunset span.');
    }
  }

  function renderTransitions(selector,rows,label){
    const el=$(selector);if(!el)return;
    if(!rows?.length){el.innerHTML='<div class="tk-panchang-empty">No transition data</div>';return}
    el.innerHTML=rows.map((row,i)=>`
      <div class="tk-panchang-transition">
        <div><small>${i===0?'At sunrise':label}</small><strong>${esc(row.name)}</strong></div>
        <span>${esc(row.end_label||'continues')}</span>
      </div>`).join('');
  }

  async function locate(silent=false){
    if(!navigator.geolocation){calculate();return}
    navigator.geolocation.getCurrentPosition(async p=>{
      state.lat=p.coords.latitude;state.lon=p.coords.longitude;state.city='Current location';
      await Promise.all([
        reverse(state.lat,state.lon),
        resolveTimezone(state.lat,state.lon,{fallback:browserTimezone})
      ]);
      calculate();
    },()=>{
      if(!silent)toast('Location permission unavailable. Using Mumbai as fallback.');
      calculate();
    },{enableHighAccuracy:false,timeout:7000,maximumAge:600000});
  }

  const panel=$('#tkPlacePanel');
  $('#tkPlaceButton')?.addEventListener('click',e=>{e.stopPropagation();panel.hidden=!panel.hidden});
  $('#tkDetectLocation')?.addEventListener('click',()=>locate(false));
  document.addEventListener('click',e=>{
    if(panel&&!panel.hidden&&!e.target.closest('#tkPlacePanel')&&!e.target.closest('#tkPlaceButton'))panel.hidden=true;
  });

  $('#tkCitySearch')?.addEventListener('input',e=>{
    clearTimeout(state.searchTimer);const q=e.target.value.trim();
    if(q.length<2){$('#tkSearchResults').innerHTML='';return}
    state.searchTimer=setTimeout(()=>searchCity(q),260);
  });

  async function searchCity(q){
    const box=$('#tkSearchResults');if(!box)return;
    try{
      const r=await fetch(`${base}api.php?action=search&q=${encodeURIComponent(q)}`);
      const j=await r.json();
      if(!j.ok||!j.results?.length){box.innerHTML='<div class="tk-search-item"><span>No places found</span></div>';return}
      box.innerHTML=j.results.map((x,i)=>`<button class="tk-search-item" data-i="${i}"><strong>${esc(x.label)}</strong><span>${esc(x.display_name)}</span></button>`).join('');
      box._rows=j.results;
      box.querySelectorAll('.tk-search-item[data-i]').forEach(btn=>btn.addEventListener('click',async()=>{
        const x=box._rows[Number(btn.dataset.i)];
        const old={lat:state.lat,lon:state.lon,city:state.city,timezone:state.timezone};
        state.lat=x.lat;state.lon=x.lon;state.city=x.label;
        const resolved=await resolveTimezone(state.lat,state.lon);
        if(!resolved){
          Object.assign(state,old);
          return;
        }
        panel.hidden=true;
        calculate();
      }));
    }catch(e){toast('City search is temporarily unavailable')}
  }

  $('#tkDate')?.addEventListener('change',()=>{state.dateTouched=true;calculate()});
  document.querySelectorAll('[data-shift-date]').forEach(btn=>btn.addEventListener('click',()=>{
    const input=$('#tkDate');if(!input)return;
    const d=new Date((input.value||isoToday())+'T12:00:00');
    const shift=Number(btn.dataset.shiftDate||0);
    if(pageSlug==='panchang/month'){
      d.setDate(1);
      d.setMonth(d.getMonth()+shift);
    }else if(lunarKinds[pageSlug]||observanceKinds[pageSlug]||festivalKinds[pageSlug]||(planetaryModes[pageSlug]&&planetaryModes[pageSlug]!=='positions')||aspectsModes[pageSlug]||eclipseModes[pageSlug]||dwadashiPages.includes(pageSlug)||mahadwadashiPages.includes(pageSlug)||seasonKinds[pageSlug]||sankrantiPages.includes(pageSlug)){
      d.setFullYear(d.getFullYear()+shift);
    }else{
      d.setDate(d.getDate()+shift);
    }
    input.value=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    state.dateTouched=true;
    calculate();
  }));
  $('#tkToday')?.addEventListener('click',()=>{const input=$('#tkDate');state.dateTouched=false;if(input)input.value=isoToday(state.timezone);calculate()});
  $('#tkMatchCalculate')?.addEventListener('click',()=>calculateHoroscopeMatch());
  $('#tkMarriageCalculate')?.addEventListener('click',()=>calculateMarriageAnalysis());
  $('#tkNakMatchCalculate')?.addEventListener('click',()=>calculateNakshatraMatch());
  $('#tkPlanetCalculate')?.addEventListener('click',()=>calculatePlanetary());
  $('#tkPlanetTime')?.addEventListener('change',()=>{if(pageSlug==='planets/positions')calculatePlanetary()});
  $('#tkNodeModel')?.addEventListener('change',()=>{if(pageSlug==='planets/positions')calculatePlanetary()});
  $('#tkDashaCalculate')?.addEventListener('click',()=>calculateDasha());
  $('#tkDashaTime')?.addEventListener('change',()=>{if(dashaPages.includes(pageSlug))calculateDasha()});
  $('#tkDoshaCalculate')?.addEventListener('click',()=>calculateDosha());
  $('#tkDoshaTime')?.addEventListener('change',()=>{if(doshaModes[pageSlug])calculateDosha()});
  $('#tkDoshaNode')?.addEventListener('change',()=>{if(doshaModes[pageSlug])calculateDosha()});
  $('#tkAshtaCalculate')?.addEventListener('click',()=>calculateAshtakavarga());
  $('#tkAshtaTime')?.addEventListener('change',()=>{if(ashtaPages.includes(pageSlug))calculateAshtakavarga()});
  $('#tkVargaCalculate')?.addEventListener('click',()=>calculateVarga());
  $('#tkVargaSelect')?.addEventListener('change',()=>{if(vargaPages.includes(pageSlug))calculateVarga()});
  $('#tkVargaTime')?.addEventListener('change',()=>{if(vargaPages.includes(pageSlug))calculateVarga()});
  $('#tkYogaCalculate')?.addEventListener('click',()=>calculateYogas());
  $('#tkYogaTime')?.addEventListener('change',()=>{if(yogaPages.includes(pageSlug))calculateYogas()});
  $('#tkShadbalaCalculate')?.addEventListener('click',()=>calculateShadbala());
  $('#tkShadbalaTime')?.addEventListener('change',()=>{if(shadbalaPages.includes(pageSlug))calculateShadbala()});
  $('#tkRashifalCalculate')?.addEventListener('click',()=>calculateRashifal());
  $('#tkRashifalBirthDate')?.addEventListener('change',()=>{if(rashifalPages.includes(pageSlug))calculateRashifal()});
  $('#tkRashifalBirthTime')?.addEventListener('change',()=>{if(rashifalPages.includes(pageSlug))calculateRashifal()});
  $('#tkRashifalTargetDate')?.addEventListener('change',()=>{if(rashifalPages.includes(pageSlug))calculateRashifal()});
  $('#tkRashifalNode')?.addEventListener('change',()=>{if(rashifalPages.includes(pageSlug))calculateRashifal()});
  $('#tkTimelineCalculate')?.addEventListener('click',()=>calculateTimeline());
  $('#tkTimelineBirthTime')?.addEventListener('change',()=>{if(timelinePages.includes(pageSlug))calculateTimeline()});
  $('#tkTimelineStart')?.addEventListener('change',()=>{if(timelinePages.includes(pageSlug))calculateTimeline()});
  $('#tkTimelineMonths')?.addEventListener('change',()=>{if(timelinePages.includes(pageSlug))calculateTimeline()});
  $('#tkTimelineNode')?.addEventListener('change',()=>{if(timelinePages.includes(pageSlug))calculateTimeline()});
  $('#tkInterpretCalculate')?.addEventListener('click',()=>calculateInterpretation());
  $('#tkInterpretTime')?.addEventListener('change',()=>{if(interpretationPages.includes(pageSlug))calculateInterpretation()});
  $('#tkInterpretNode')?.addEventListener('change',()=>{if(interpretationPages.includes(pageSlug))calculateInterpretation()});
  $('#tkAnalysisCalculate')?.addEventListener('click',()=>calculateHoroscopeAnalysis());
  $('#tkAnalysisTime')?.addEventListener('change',()=>{if(analysisPages.includes(pageSlug))calculateHoroscopeAnalysis()});
  $('#tkAnalysisNode')?.addEventListener('change',()=>{if(analysisPages.includes(pageSlug))calculateHoroscopeAnalysis()});
  $('#tkKundaliCalculate')?.addEventListener('click',()=>calculateKundali());
  $('#tkKundaliTime')?.addEventListener('change',()=>{if(kundaliPages.includes(pageSlug))calculateKundali()});
  $('#tkKundaliNode')?.addEventListener('change',()=>{if(kundaliPages.includes(pageSlug))calculateKundali()});
  $('#tkBirthCalculate')?.addEventListener('click',()=>calculateJyotish());
  $('#tkBirthTime')?.addEventListener('change',()=>{if(jyotishModes[pageSlug])calculateJyotish()});

  const input=$('#tkDate');
  const queryDate=new URLSearchParams(window.location.search).get('date');
  if(input&&queryDate&&/^\d{4}-\d{2}-\d{2}$/.test(queryDate)&&!Number.isNaN(Date.parse(queryDate+'T12:00:00Z'))){
    input.value=queryDate;
    state.dateTouched=true;
  }else if(input&&!input.value){
    input.value=isoToday(state.timezone);
  }
  const rashBirth=$('#tkRashifalBirthDate');if(rashBirth&&!rashBirth.value)rashBirth.value=input?.value||isoToday(state.timezone);
  const rashTarget=$('#tkRashifalTargetDate');if(rashTarget&&!rashTarget.value)rashTarget.value=isoToday(state.timezone);
  const timelineStart=$('#tkTimelineStart');if(timelineStart&&!timelineStart.value)timelineStart.value=isoToday(state.timezone).slice(0,7);
  initMatching();
  locate(true);
})();