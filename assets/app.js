const $ = s => document.querySelector(s);
const state = {
  lat: 19.0760,
  lon: 72.8777,
  city: 'Mumbai, Maharashtra, India',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata',
  hour24: false,
  data: null,
  searchTimer: null,
  mobileTab: 'day'
};

const todayISO = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
};
$('#dateInput').value = todayISO();

function toast(msg){
  const t=$('#toast'); t.textContent=msg; t.classList.remove('hidden');
  clearTimeout(t._x); t._x=setTimeout(()=>t.classList.add('hidden'),3200);
}
function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function qualityClass(q){return ['best','good','gain'].includes(q)?`quality-${q}`:q==='neutral'?'quality-neutral':'quality-avoid'}
function rowHTML(r, active){
  return `<div class="period-row ${qualityClass(r.quality)} ${active?'active-ring':''} grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 rounded-[1.15rem] border bg-white/90 p-3 sm:p-3.5">
    <span class="period-dot grid h-10 w-10 shrink-0 place-items-center rounded-2xl text-sm font-black">${esc(r.emoji)}</span>
    <div class="min-w-0">
      <div class="flex flex-wrap items-center gap-1.5">
        <strong class="text-sm font-black sm:text-[15px]">${esc(r.name)}</strong>
        <span class="period-pill rounded-full px-2 py-0.5 text-[9px] font-black uppercase tracking-[.08em]">${esc(r.label)}</span>
        ${active?'<span class="rounded-full bg-orange-100 px-2 py-0.5 text-[9px] font-black uppercase tracking-[.08em] text-orange-700">Now</span>':''}
      </div>
      <div class="mt-1 text-[10px] font-semibold uppercase tracking-[.08em] text-stone-400">Period ${r.index} of 8</div>
    </div>
    <div class="text-right text-[11px] font-black leading-5 tabular-nums text-stone-600 sm:text-xs"><span class="block sm:inline">${esc(r.start_label)}</span><span class="mx-1 hidden text-stone-300 sm:inline">→</span><span class="block text-stone-400 sm:inline sm:text-stone-600">${esc(r.end_label)}</span></div>
  </div>`;
}
function durationText(start,end){
  const ms=Math.max(0,new Date(end)-new Date(start));
  const mins=Math.round(ms/60000), h=Math.floor(mins/60), m=mins%60;
  return `${h}h ${String(m).padStart(2,'0')}m`;
}
function setMobileTab(tab){
  state.mobileTab=tab;
  const isDay=tab==='day';
  $('#dayTab').setAttribute('aria-selected',String(isDay));
  $('#nightTab').setAttribute('aria-selected',String(!isDay));
  $('#dayPanel').dataset.mobileHidden=String(!isDay);
  $('#nightPanel').dataset.mobileHidden=String(isDay);
}
$('#dayTab').addEventListener('click',()=>setMobileTab('day'));
$('#nightTab').addEventListener('click',()=>setMobileTab('night'));

async function calculate(){
  document.documentElement.classList.add('is-loading');
  try{
    const res=await fetch('api.php?action=calculate',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({lat:state.lat,lon:state.lon,city:state.city,date:$('#dateInput').value,timezone:state.timezone,hour24:state.hour24})
    });
    const data=await res.json();
    if(!data.ok) throw new Error(data.error||'Calculation failed');
    state.data=data; render(data);
  }catch(e){toast(e.message||'Unable to calculate timings')}
  finally{document.documentElement.classList.remove('is-loading')}
}

function render(d){
  const city=d.location.city;
  $('#locationMini').textContent=`⌖ ${city}`;
  $('#headerLocation').textContent=city;
  $('#citySearch').value=city;
  $('#coords').textContent=`${d.location.lat.toFixed(4)}, ${d.location.lon.toFixed(4)} · ${d.location.timezone}`;
  $('#locationStatus').textContent='● Location applied';

  $('#sunrise').textContent=d.sunrise_label;
  $('#sunset').textContent=d.sunset_label;
  $('#sunriseHero').textContent=d.sunrise_label;
  $('#sunsetHero').textContent=d.sunset_label;
  $('#dayLength').textContent=`Daylight ${durationText(d.sunrise,d.sunset)}`;
  $('#nightLength').textContent=`Night ${durationText(d.sunset,d.next_sunrise)}`;
  $('#selectedDateTitle').textContent=`${d.weekday}, ${d.date_label}`;
  $('#dayHeading').textContent=`${d.sunrise_label} → ${d.sunset_label}`;
  $('#nightHeading').textContent=`${d.sunset_label} → ${new Intl.DateTimeFormat([], {hour:'numeric',minute:'2-digit',hour12:!state.hour24,timeZone:d.location.timezone}).format(new Date(d.next_sunrise))}`;

  $('#dayList').innerHTML=d.day.map(r=>rowHTML(r,d.active?.side==='day'&&d.active.index===r.index&&!d.active?.carry_from_previous_date)).join('');
  $('#nightList').innerHTML=d.night.map(r=>rowHTML(r,d.active?.side==='night'&&d.active.index===r.index&&!d.active?.carry_from_previous_date)).join('');
  $('#rahu').textContent=`${d.rahu_kaal.start_label} – ${d.rahu_kaal.end_label}`;

  if(d.active){
    $('#currentName').textContent=d.active.name;
    $('#currentRange').textContent=`${d.active.start_label} – ${d.active.end_label}`;
    $('#currentQuality').textContent=d.active.label;
    $('#activeSide').textContent=d.active.side==='day'?'☀ Day period':'☾ Night period';
    $('#currentEyebrow').textContent=d.active.carry_from_previous_date?'Current Choghadiya · previous night':'Current Choghadiya';
    if(window.innerWidth<768) setMobileTab(d.active.side==='night'?'night':'day');
  } else {
    const isToday=$('#dateInput').value===todayISO();
    $('#currentName').textContent=isToday?'Solar schedule':'Selected day';
    $('#currentRange').textContent=`${d.weekday}, ${d.date_label}`;
    $('#currentQuality').textContent='Schedule';
    $('#activeSide').textContent=isToday?'Today':'Reference date';
    $('#currentEyebrow').textContent=isToday?'Today’s Choghadiya':'Viewing Choghadiya';
    $('#currentProgress').style.setProperty('--progress','0%');
    $('#progressText').textContent='—';
  }

  if(d.next_auspicious){
    const n=d.next_auspicious;
    $('#nextGood').textContent=`${n.name} · ${n.start_label} – ${n.end_label}`;
    $('#nextGoodSub').textContent=`${n.side==='day'?'Day':'Night'} Choghadiya · ${n.label}`;
  } else {
    $('#nextGood').textContent='No later favourable window';
    $('#nextGoodSub').textContent='Choose the next date to view upcoming periods.';
  }
  updateClock();
}

function updateClock(){
  const d=state.data; if(!d)return;
  const now=new Date();
  $('#liveClock').textContent=new Intl.DateTimeFormat([], {hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:!state.hour24,timeZone:d.location.timezone}).format(now);
  if(d.active){
    const start=new Date(d.active.start), end=new Date(d.active.end);
    const total=Math.max(1,end-start), elapsed=Math.min(total,Math.max(0,now-start));
    const pct=Math.max(0,Math.min(100,(elapsed/total)*100));
    $('#currentProgress').style.setProperty('--progress',`${pct.toFixed(1)}%`);
    $('#progressText').textContent=`${Math.round(pct)}% elapsed`;
    let sec=Math.max(0,Math.floor((end-now)/1000));
    const h=String(Math.floor(sec/3600)).padStart(2,'0'),m=String(Math.floor(sec%3600/60)).padStart(2,'0'),s=String(sec%60).padStart(2,'0');
    $('#countdown').textContent=`${h}:${m}:${s}`;
  }else{
    $('#countdown').textContent='--:--:--';
  }
}
setInterval(updateClock,1000);

async function reverseLocation(lat,lon){
  try{
    const r=await fetch(`api.php?action=reverse&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`);
    const j=await r.json(); if(j.ok&&j.label)state.city=j.label;
  }catch(e){}
}

async function useMyLocation(silent=false){
  if(!navigator.geolocation){
    $('#locationStatus').textContent='● City search available';
    if(!silent)toast('Geolocation is not supported by this browser');
    return calculate();
  }
  $('#headerLocation').textContent='Finding your location…';
  $('#locationMini').textContent='⌖ Detecting location…';
  $('#locationStatus').textContent='● Requesting location…';
  navigator.geolocation.getCurrentPosition(async p=>{
    state.lat=p.coords.latitude; state.lon=p.coords.longitude; state.city='Current location';
    await reverseLocation(state.lat,state.lon);
    $('#locationStatus').textContent='● Auto location active';
    calculate();
  },()=>{
    $('#locationStatus').textContent='● Using default city';
    if(!silent)toast('Location permission unavailable — search for your city instead.');
    calculate();
  },{enableHighAccuracy:false,timeout:7000,maximumAge:600000});
}

$('#locateBtn').addEventListener('click',()=>useMyLocation(false));
$('#headerLocateBtn').addEventListener('click',()=>useMyLocation(false));
$('#formatBtn').addEventListener('click',()=>{
  state.hour24=!state.hour24;
  $('#formatBtn').textContent=state.hour24?'24 hour':'12 hour';
  calculate();
});
$('#dateInput').addEventListener('change',calculate);
$('#calendarTodayBtn').addEventListener('click',()=>{$('#dateInput').value=todayISO();calculate()});
document.querySelectorAll('.navBtn').forEach(b=>b.addEventListener('click',()=>{
  const d=new Date($('#dateInput').value+'T12:00:00');
  d.setDate(d.getDate()+Number(b.dataset.shift));
  $('#dateInput').value=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  calculate();
}));

$('#citySearch').addEventListener('input',e=>{
  clearTimeout(state.searchTimer); const q=e.target.value.trim();
  if(q.length<2){$('#searchResults').classList.add('hidden');return;}
  state.searchTimer=setTimeout(()=>searchCity(q),280);
});
async function searchCity(q){
  const box=$('#searchResults');
  try{
    const r=await fetch(`api.php?action=search&q=${encodeURIComponent(q)}`),j=await r.json();
    if(!j.ok||!j.results?.length){box.innerHTML='<div class="p-3 text-xs font-semibold text-stone-400">No matching place</div>';box.classList.remove('hidden');return;}
    box.innerHTML=j.results.map((x,i)=>`<button data-i="${i}" class="placeResult block w-full rounded-xl px-3 py-3 text-left transition hover:bg-orange-50"><div class="text-sm font-black text-stone-800">${esc(x.label)}</div><div class="mt-0.5 truncate text-[11px] font-medium text-stone-400">${esc(x.display_name)}</div></button>`).join('');
    box._rows=j.results; box.classList.remove('hidden');
    box.querySelectorAll('.placeResult').forEach(btn=>btn.onclick=()=>{
      const x=box._rows[Number(btn.dataset.i)];
      state.lat=x.lat; state.lon=x.lon; state.city=x.label;
      $('#citySearch').value=x.label; box.classList.add('hidden');
      $('#locationStatus').textContent='● Searched location active';
      calculate();
    });
  }catch(e){toast('City lookup is temporarily unavailable')}
}
document.addEventListener('click',e=>{if(!e.target.closest('#citySearch')&&!e.target.closest('#searchResults'))$('#searchResults').classList.add('hidden')});

useMyLocation(true);
