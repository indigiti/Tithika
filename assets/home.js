const $ = s => document.querySelector(s);

const state = {
  lat: 19.076,
  lon: 72.8777,
  city: 'Mumbai, Maharashtra, India',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata',
  data: null,
  searchTimer: null
};

function localDateISO(){
  const parts = new Intl.DateTimeFormat('en-CA',{year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
  const v = Object.fromEntries(parts.map(p=>[p.type,p.value]));
  return `${v.year}-${v.month}-${v.day}`;
}

function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function toast(message){
  const el=$('#toast'); if(!el)return;
  el.textContent=message; el.classList.remove('hidden');
  clearTimeout(el._t); el._t=setTimeout(()=>el.classList.add('hidden'),3200);
}

async function reverseLocation(lat,lon){
  try{
    const r=await fetch(`api.php?action=reverse&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`);
    const j=await r.json();
    if(j.ok&&j.label) state.city=j.label;
  }catch(e){}
}

async function calculate(){
  try{
    const r=await fetch('api.php?action=calculate',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        lat:state.lat,lon:state.lon,city:state.city,
        date:localDateISO(),timezone:state.timezone,hour24:false
      })
    });
    const j=await r.json();
    if(!j.ok) throw new Error(j.error||'Unable to load today’s timings');
    state.data=j; render(j);
  }catch(e){toast(e.message||'Unable to load timings')}
}

function render(d){
  const shortCity=(d.location.city||'Current location').split(',').slice(0,2).join(',');
  $('#locationText').textContent=shortCity;
  $('#heroLocation').textContent=shortCity;
  $('#todayLabel').textContent=`${d.weekday}, ${d.date_label}`;
  $('#heroDate').textContent=d.date_label;
  $('#sunrise').textContent=d.sunrise_label;
  $('#sunset').textContent=d.sunset_label;
  if($('#sunrise2')) $('#sunrise2').textContent=d.sunrise_label;
  if($('#sunset2')) $('#sunset2').textContent=d.sunset_label;
  $('#rahu').textContent=`${d.rahu_kaal.start_label} – ${d.rahu_kaal.end_label}`;
  $('#nextGood').textContent=d.next_auspicious ? `${d.next_auspicious.name} · ${d.next_auspicious.start_label}` : 'View tomorrow';
  $('#nextGoodSub').textContent=d.next_auspicious ? `${d.next_auspicious.start_label} – ${d.next_auspicious.end_label}` : 'No later favourable window';

  if(d.active){
    $('#currentName').textContent=d.active.name;
    $('#currentLabel').textContent=d.active.label;
    $('#currentRange').textContent=`${d.active.start_label} – ${d.active.end_label}`;
    $('#currentSide').textContent=d.active.side==='day'?'Day Choghadiya':'Night Choghadiya';
  }else{
    $('#currentName').textContent='Today’s schedule';
    $('#currentLabel').textContent='Ready';
    $('#currentRange').textContent=`${d.sunrise_label} – ${d.sunset_label}`;
    $('#currentSide').textContent='Solar day';
  }

  const rows=d.day||[];
  $('#timeline').innerHTML=rows.map((r,i)=>{
    const active=d.active && !d.active.carry_from_previous_date && d.active.side==='day' && d.active.index===r.index;
    const tone=['best','good','gain'].includes(r.quality)?'good':r.quality==='neutral'?'neutral':'avoid';
    return `<div class="time-seg ${tone} ${active?'is-active':''}" style="--i:${i}">
      <span class="seg-name">${esc(r.name)}</span>
      <span class="seg-time">${esc(r.start_label)}</span>
    </div>`;
  }).join('');

  updateClock();
}

function updateClock(){
  if(!state.data)return;
  const d=state.data, now=new Date();
  $('#clock').textContent=new Intl.DateTimeFormat([],{
    hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true,timeZone:d.location.timezone
  }).format(now);
  if(d.active){
    const start=new Date(d.active.start),end=new Date(d.active.end);
    const pct=Math.max(0,Math.min(100,((now-start)/(end-start))*100));
    $('#heroProgress').style.width=`${pct}%`;
    let sec=Math.max(0,Math.floor((end-now)/1000));
    const h=String(Math.floor(sec/3600)).padStart(2,'0');
    const m=String(Math.floor(sec%3600/60)).padStart(2,'0');
    $('#changesIn').textContent=`${h}h ${m}m`;
  }
}
setInterval(updateClock,1000);

async function useLocation(silent=false){
  if(!navigator.geolocation){calculate();return}
  $('#locationText').textContent='Locating…';
  navigator.geolocation.getCurrentPosition(async p=>{
    state.lat=p.coords.latitude;state.lon=p.coords.longitude;state.city='Current location';
    await reverseLocation(state.lat,state.lon);
    calculate();
  },()=>{
    if(!silent)toast('Location unavailable. Using Mumbai; you can search another city.');
    calculate();
  },{enableHighAccuracy:false,timeout:7000,maximumAge:600000});
}

$('#locationBtn')?.addEventListener('click',()=>$('#locationPanel').classList.toggle('hidden'));
$('#mobileLocationBtn')?.addEventListener('click',()=>$('#locationPanel').classList.toggle('hidden'));
$('#detectBtn')?.addEventListener('click',()=>useLocation(false));

$('#citySearch')?.addEventListener('input',e=>{
  clearTimeout(state.searchTimer);
  const q=e.target.value.trim();
  if(q.length<2){$('#searchResults').classList.add('hidden');return}
  state.searchTimer=setTimeout(()=>searchCity(q),250);
});

async function searchCity(q){
  try{
    const r=await fetch(`api.php?action=search&q=${encodeURIComponent(q)}`);
    const j=await r.json(), box=$('#searchResults');
    if(!j.ok||!j.results?.length){
      box.innerHTML='<div class="p-3 text-xs font-semibold text-slate-400">No places found</div>';
      box.classList.remove('hidden'); return;
    }
    box.innerHTML=j.results.map((x,i)=>`<button class="place-result" data-i="${i}">
      <strong>${esc(x.label)}</strong><span>${esc(x.display_name)}</span>
    </button>`).join('');
    box._rows=j.results; box.classList.remove('hidden');
    box.querySelectorAll('.place-result').forEach(btn=>btn.onclick=()=>{
      const x=box._rows[Number(btn.dataset.i)];
      state.lat=x.lat;state.lon=x.lon;state.city=x.label;
      $('#locationPanel').classList.add('hidden');
      calculate();
    });
  }catch(e){toast('City search is temporarily unavailable')}
}

document.addEventListener('click',e=>{
  if(!e.target.closest('#locationPanel')&&!e.target.closest('#locationBtn')&&!e.target.closest('#mobileLocationBtn')){
    $('#locationPanel')?.classList.add('hidden');
  }
});

useLocation(true);
