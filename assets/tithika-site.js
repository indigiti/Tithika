(()=> {
  const $=s=>document.querySelector(s);
  const base=window.TITHIKA_BASE||'/';
  const pageSlug=window.TITHIKA_PAGE_SLUG||'';
  const panchangPages=['panchang/daily','panchang/moonrise-moonset','panchang/rahu-kala','muhurat/rahu-kala','muhurat/abhijit'];
  const monthPages=['panchang/month'];
  const browserTimezone=Intl.DateTimeFormat().resolvedOptions().timeZone||'Asia/Kolkata';
  const state={
    lat:19.076,lon:72.8777,city:'Mumbai, Maharashtra, India',
    timezone:'Asia/Kolkata',
    data:null,panchang:null,searchTimer:null,dateTouched:false
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
      if(monthPages.includes(pageSlug)) await calculateMonth();
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

  async function calculateMonth(){
    const loading=$('#tkMonthLoading');
    if(loading){loading.hidden=false;loading.textContent='Building month Panchang…'}
    try{
      const r=await fetch(`${base}api.php?action=panchang-month`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(payload())
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate Month Panchang');
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
    const blanks=Math.max(0,Number(d.first_weekday||0));
    let html=Array.from({length:blanks},()=>'<div class="tk-month-day is-empty"></div>').join('');
    html+=(d.days||[]).map(row=>{
      if(!row.available)return `<div class="tk-month-day is-unavailable"><b>${row.day}</b><small>Unavailable</small></div>`;
      const special=row.tithi==='Ekadashi'?' ekadashi':row.tithi==='Purnima'?' purnima':row.tithi==='Amavasya'?' amavasya':'';
      const selected=payload().date===row.date?' is-selected':'';
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
    }else{
      d.setDate(d.getDate()+shift);
    }
    input.value=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    state.dateTouched=true;
    calculate();
  }));
  $('#tkToday')?.addEventListener('click',()=>{const input=$('#tkDate');state.dateTouched=false;if(input)input.value=isoToday(state.timezone);calculate()});

  const input=$('#tkDate');if(input&&!input.value)input.value=isoToday(state.timezone);
  locate(true);
})();