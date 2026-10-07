(() => {
  'use strict';
  const root=document.getElementById('tkDailyDashboard');
  if(!root)return;
  const base=window.TITHIKA_BASE||'/';
  const $=s=>document.querySelector(s);
  const settings=()=>window.TithikaSettings?.get?.()||{clock:'12',lunarMonth:'amanta',tradition:'smarta'};
  let controller=null,lastKey='';

  const esc=(v='')=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const set=(id,value)=>{const el=$(id);if(el)el.textContent=value??'—'};
  function timeRange(row){
    if(!row)return '—';
    return [row.start_label,row.end_label].filter(Boolean).join(' – ')||'—';
  }
  function formatDay(value,tz){
    if(!value)return '';
    try{
      return new Intl.DateTimeFormat('en-IN',{timeZone:tz||'Asia/Kolkata',weekday:'short',day:'numeric',month:'short'}).format(new Date(value+'T12:00:00'));
    }catch(e){return value}
  }
  function routeUrl(route){return base+String(route||'').replace(/^\/+|\/+$/g,'')+'/';}

  function render(data){
    const pref=settings(),today=data.today||{},loc=data.location||{},chog=data.choghadiya||{};
    const month=pref.lunarMonth==='purnimanta'?today.purnimanta_month:today.amanta_month;
    set('#tkDailyDate',(today.weekday?today.weekday+' · ':'')+(today.date_label||data.date||''));
    set('#tkDailyLocation',String(loc.city||'Selected location').split(',').slice(0,2).join(', '));
    set('#tkDailyTithi',today.tithi||'—');
    set('#tkDailyPaksha',today.paksha||'—');
    set('#tkDailyNakshatra',today.nakshatra||'—');
    set('#tkDailyMoon','Moon '+(today.moon_rashi||'—'));
    set('#tkDailyYoga',today.yoga||'—');
    set('#tkDailyKarana','Karana '+(today.karana||'—'));
    set('#tkDailyMonth',month||'—');
    set('#tkDailyMonthMode',(pref.lunarMonth==='purnimanta'?'Purnimanta':'Amanta')+' preference');
    set('#tkDailySunrise',today.sunrise||'—');
    set('#tkDailySunset',today.sunset||'—');
    set('#tkDailyMoonrise',today.moonrise||'—');
    set('#tkDailyAbhijit',timeRange(today.abhijit));
    set('#tkDailyRahu',timeRange(today.rahu_kaal));

    const active=chog.active||chog.next_auspicious;
    set('#tkDailyChogName',active?.name||(chog.next_auspicious?'Next '+chog.next_auspicious.name:'No active period'));
    set('#tkDailyChogTime',active?((active.label?active.label+' · ':'')+timeRange(active)):'Open the full timeline for all periods');
    set('#tkDailyLead',
      'For '+String(loc.city||'your selected location').split(',').slice(0,2).join(', ')+
      ', '+(today.tithi||'the current Tithi')+' aligns with '+(today.nakshatra||'the current Nakshatra')+
      '. The dashboard keeps timing, observances and planet events in one local context.'
    );

    const box=$('#tkUpcomingEvents'),rows=data.upcoming||[];
    if(box){
      box.innerHTML=rows.length?rows.slice(0,8).map(row=>`
        <a class="tk-upcoming-card type-${esc(row.type||'event')}" href="${esc(routeUrl(row.route))}">
          <time>${esc(formatDay(row.date,loc.timezone))}</time>
          <span>${esc(row.type||'event')}</span>
          <h3>${esc(row.title||'Upcoming event')}</h3>
          <p>${esc(row.subtitle||'Verified Tithika event')}</p>
          <b>View details →</b>
        </a>`).join(''):'<div class="tk-upcoming-empty">No major tracked events fall inside this dashboard horizon. Open the full calendars for the complete year.</div>';
    }
    root.setAttribute('aria-busy','false');
  }

  async function load(context){
    const pref=settings();
    const payload={
      lat:Number(context.lat),lon:Number(context.lon),city:context.city,timezone:context.timezone,
      date:context.date,hour24:pref.clock==='24',tradition:pref.tradition,horizon_days:21
    };
    const key=JSON.stringify(payload);
    if(key===lastKey)return;
    lastKey=key;
    controller?.abort();controller=new AbortController();
    root.setAttribute('aria-busy','true');
    try{
      const response=await fetch(base+'api.php?action=home-dashboard',{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal
      });
      const data=await response.json();
      if(!response.ok||!data.ok)throw new Error(data.error||'Dashboard unavailable');
      render(data);
    }catch(error){
      if(error.name==='AbortError')return;
      root.setAttribute('aria-busy','false');
      set('#tkDailyLead','Daily dashboard could not refresh. The individual Panchang and Muhurat tools remain available.');
      const box=$('#tkUpcomingEvents');
      if(box)box.innerHTML='<div class="tk-upcoming-empty">Unable to load the aggregated event feed right now.</div>';
    }
  }

  window.addEventListener('tithika:context',e=>load(e.detail||{}));
  window.addEventListener('tithika:settings',()=>{
    lastKey='';
    const ctx=window.TithikaContext?.get?.();
    if(ctx)load(ctx);
  });
  const initial=window.TithikaContext?.get?.();
  if(initial)setTimeout(()=>load(initial),0);
})();