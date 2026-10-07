(()=>{"use strict";
const $=s=>document.querySelector(s),base=window.TITHIKA_BASE||'/';
let ctx=null,timer=null,data=null;
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmtDate=d=>{try{return new Intl.DateTimeFormat('en-IN',{dateStyle:'medium',timeZone:ctx?.timezone||'Asia/Kolkata'}).format(new Date(d+'T12:00:00'))}catch{return d}};
function set(id,v){const el=$(id);if(el)el.textContent=v??'—'}
async function load(){
 if(!ctx)return;
 try{
  const r=await fetch(`${base}api.php?action=home-dashboard`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(ctx)});
  const j=await r.json();if(!r.ok||!j.ok)throw new Error(j.error||'Dashboard unavailable');data=j;render(j);$('#tkHomeError').hidden=true;
 }catch(e){$('#tkHomeError').hidden=false}
}
function render(d){
 const t=d.today||{},c=d.choghadiya||{},a=d.advisor||{},u=d.upcoming||{};
 set('#tkHomePlace',(d.location?.city||'Current location').split(',').slice(0,2).join(', '));
 set('#tkHomeDate',`${t.weekday||''} · ${fmtDate(d.date)}`);
 set('#tkHomeCache',d.cache==='hit'?'15 min smart cache':'Fresh engine pass');
 set('#tkHomeTithi',t.tithi);set('#tkHomePaksha',t.paksha);set('#tkHomeNakshatra',t.nakshatra);
 set('#tkHomeYoga',t.yoga);set('#tkHomeKarana',`Karana ${t.karana||'—'}`);
 set('#tkHomeMoon',t.moon_rashi);set('#tkHomeMonth',`Lunar month ${t.lunar_month||'—'}`);
 set('#tkHomeSunrise',t.sunrise);set('#tkHomeSunset',`Sunset ${t.sunset||'—'}`);
 const rk=t.rahu_kaal||{};set('#tkHomeRahu',rk.start_label&&rk.end_label?`${rk.start_label} – ${rk.end_label}`:'—');
 const cur=c.active||c.next_auspicious||{};
 set('#tkHomeCurrentName',cur.name||'Solar day');
 set('#tkHomeCurrentLabel',cur.label||'Traditional timing context');
 set('#tkHomeCurrentRange',cur.start_label&&cur.end_label?`${cur.start_label} – ${cur.end_label}`:'—');
 set('#tkHomeCurrentSide',cur.side?cur.side+' period':'Today');
 if(cur.start&&cur.end){const now=new Date(),s=new Date(cur.start),e=new Date(cur.end),pct=Math.max(0,Math.min(100,(now-s)/(e-s)*100));$('#tkHomeCurrentProgress').style.width=pct+'%'}
 set('#tkHomeAdvisorSummary',a.summary||'Verified timing recommendations for the next seven days.');
 const rec=a.recommendations||[];
 $('#tkHomeRecommendations').innerHTML=rec.length?rec.map((r,i)=>`<article class="tk-home-rec"><div><i>${String(i+1).padStart(2,'0')}</i><span><b>${esc(r.name||'Timing window')}</b><small>${esc(fmtDate(r.date))} · ${esc(r.start_label||'')}–${esc(r.end_label||'')}</small></span></div><em>${esc(r.score??'—')}</em></article>`).join(''):'<p class="tk-home-empty">No ranked window found in this range.</p>';
 const cal=u.calendar||[];
 $('#tkHomeCalendar').innerHTML=cal.length?cal.map(r=>`<a class="tk-home-event" href="${base}festivals/hindu/"><time>${esc(fmtDate(r.date))}</time><span><b>${esc(r.title)}</b><small>${r.days_away===0?'Today':r.days_away===1?'Tomorrow':r.days_away+' days away'}${r.meta?' · '+esc(r.meta):''}</small></span><i>→</i></a>`).join(''):'<p class="tk-home-empty">No upcoming calculated observance found.</p>';
 const planets=u.planets||[];
 $('#tkHomePlanets').innerHTML=planets.length?planets.map(r=>`<a class="tk-home-event" href="${base}planets/transit/"><time>${esc(fmtDate(r.date))}</time><span><b>${esc(r.title)}</b><small>${esc(r.direction||'')} · ${r.days_away===0?'Today':r.days_away+' days away'}</small></span><i>→</i></a>`).join(''):'<p class="tk-home-empty">No major transit in the next 60 days.</p>';
 $('#tkHomeProvenance').innerHTML=(d.provenance||[]).map(s=>`<span><b>${esc(s.engine)}</b> v${esc(s.version)}</span>`).join('');
}
window.addEventListener('tithika:context',e=>{ctx=e.detail;clearTimeout(timer);timer=setTimeout(load,120)});
setInterval(()=>{if(data)render(data)},60000);
})();