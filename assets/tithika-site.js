(()=> {
  const $=s=>document.querySelector(s);
  const base=window.TITHIKA_BASE||'/';
  const state={
    lat:19.076,lon:72.8777,city:'Mumbai, Maharashtra, India',
    timezone:Intl.DateTimeFormat().resolvedOptions().timeZone||'Asia/Kolkata',
    data:null,searchTimer:null
  };

  function isoToday(){
    const d=new Date();
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
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

  async function calculate(){
    const dateInput=$('#tkDate');
    try{
      const r=await fetch(`${base}api.php?action=calculate`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          lat:state.lat,lon:state.lon,city:state.city,
          date:dateInput?.value||isoToday(),timezone:state.timezone,hour24:false
        })
      });
      const j=await r.json();
      if(!j.ok)throw new Error(j.error||'Unable to calculate solar context');
      state.data=j;render(j);
    }catch(e){toast(e.message||'Unable to load location context')}
  }

  function render(d){
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

  async function locate(silent=false){
    if(!navigator.geolocation){calculate();return}
    navigator.geolocation.getCurrentPosition(async p=>{
      state.lat=p.coords.latitude;state.lon=p.coords.longitude;state.city='Current location';
      await reverse(state.lat,state.lon);
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
      box.querySelectorAll('.tk-search-item[data-i]').forEach(btn=>btn.addEventListener('click',()=>{
        const x=box._rows[Number(btn.dataset.i)];
        state.lat=x.lat;state.lon=x.lon;state.city=x.label;panel.hidden=true;calculate();
      }));
    }catch(e){toast('City search is temporarily unavailable')}
  }

  $('#tkDate')?.addEventListener('change',calculate);
  document.querySelectorAll('[data-shift-date]').forEach(btn=>btn.addEventListener('click',()=>{
    const input=$('#tkDate');if(!input)return;
    const d=new Date((input.value||isoToday())+'T12:00:00');
    d.setDate(d.getDate()+Number(btn.dataset.shiftDate||0));
    input.value=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    calculate();
  }));
  $('#tkToday')?.addEventListener('click',()=>{const input=$('#tkDate');if(input)input.value=isoToday();calculate()});

  const input=$('#tkDate');if(input&&!input.value)input.value=isoToday();
  locate(true);
})();