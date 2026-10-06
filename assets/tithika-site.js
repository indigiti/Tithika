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
  $('#tkPlanetCalculate')?.addEventListener('click',()=>calculatePlanetary());
  $('#tkPlanetTime')?.addEventListener('change',()=>{if(pageSlug==='planets/positions')calculatePlanetary()});
  $('#tkNodeModel')?.addEventListener('change',()=>{if(pageSlug==='planets/positions')calculatePlanetary()});
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
  locate(true);
})();