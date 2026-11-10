(() => {
'use strict';
const root=document.getElementById('tkDailyDepth');if(!root)return;
const base=window.TITHIKA_BASE||'/';
const get=id=>root.querySelector(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const set=(id,v)=>{const e=get(id);if(e)e.textContent=v??'—'};
const empty=s=>'<p class="tk-depth-muted">'+esc(s)+'</p>';
let ctx=null,day=null,request=0,abort=null,scale=60,clockTimer=null;
const dt=v=>{let x=new Date(v);return isNaN(x.getTime())?null:x};
const local=(v,options)=>{let d=dt(v);return d?new Intl.DateTimeFormat('en-IN',{timeZone:ctx?.timezone||'Asia/Kolkata',...(options||{hour:'2-digit',minute:'2-digit',hour12:!window.TithikaSettings?.hour24?.()})}).format(d):'—'};
const payload=()=>({lat:Number(ctx.lat),lon:Number(ctx.lon),date:ctx.date,city:ctx.city,timezone:ctx.timezone,elevation:Number(ctx.elevation||0),hour24:!!window.TithikaSettings?.hour24?.(),tradition:window.TithikaSettings?.get?.()?.tradition||'smarta'});
async function api(action,p,signal){
 const r=await fetch(base+'api.php?action='+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p),signal});
 const j=await r.json();if(!r.ok||!j.ok)throw new Error(j.error||'Calculation unavailable');return j;
}
function timeline(d){
 const sunrise=dt(d.sunrise),sunset=dt(d.sunset),next=dt(d.next_sunrise);
 if(!sunrise||!sunset||!next||next<=sunrise){get('#tkDepthTracks').innerHTML=empty('Invalid solar-day interval');return}
 const total=next-sunrise;
 get('#tkDepthRuler').innerHTML='<span>☀ Sunrise<br><b>'+esc(local(d.sunrise))+'</b></span><span>☾ Sunset<br><b>'+esc(local(d.sunset))+'</b></span><span>☀ Next sunrise<br><b>'+esc(local(d.next_sunrise))+'</b></span>';
 get('#tkDepthRuler').style.setProperty('--tk-depth-sunset',(100*(sunset-sunrise)/total)+'%');
 get('#tkDepthTracks').innerHTML=[['Tithi','tithi'],['Nakshatra','nakshatra'],['Yoga','yoga'],['Karana','karana']].map(pair=>{
  const rows=(d[pair[1]]||[]).filter(x=>dt(x.start)&&dt(x.end));
  const bars=rows.map(x=>{
   const start=Math.max(+sunrise,+dt(x.start)),end=Math.min(+next,+dt(x.end)),width=Math.max(0,100*(end-start)/total);
   if(!width)return '';
   const tip=x.name+' · '+local(x.start,{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'})+' to '+local(x.end,{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'});
   return '<span class="tk-depth-segment" tabindex="0" style="width:'+width.toFixed(5)+'%" title="'+esc(tip)+'" aria-label="'+esc(tip)+'"><b>'+esc(x.name)+'</b><small>'+esc(x.end_label||'')+'</small></span>';
  }).join('');
  return '<div class="tk-depth-track"><strong>'+pair[0]+'</strong><div class="tk-depth-track-bar tk-depth-'+pair[1]+'">'+bars+'</div></div>';
 }).join('');
 set('#tkDepthDaySpan',local(d.sunrise)+' → '+local(d.next_sunrise)+' · sunrise-based Hindu day');
}
function summary(d){
 const s=d.sunrise_state||{},m=d.lunar_month||{};
 const fields=[['Date',(d.weekday||'')+', '+(d.date_label||d.date)],['Sunrise',d.sunrise_label],['Sunset',d.sunset_label],['Moonrise',d.moonrise_label||'Not observed'],['Moonset',d.moonset_label||'Not observed'],['Tithi',(s.tithi||'—')+' · '+(s.paksha||'')],['Nakshatra',(s.nakshatra||'—')+' · Pada '+(s.nakshatra_pada||'—')],['Yoga',s.yoga],['Karana',s.karana],['Amanta month',m.amanta],['Purnimanta month',m.purnimanta],['Sun Rashi',d.sun_rashi],['Moon Rashi',d.moon_rashi]];
 get('#tkDepthSummary').innerHTML=fields.map(x=>'<div><dt>'+esc(x[0])+'</dt><dd>'+esc(x[1]||'—')+'</dd></div>').join('');
 set('#tkDepthMoonSign',d.moon_rashi);
 set('#tkDepthContext',(d.weekday||'')+' · '+(d.date_label||d.date)+' · '+(d.location?.city||ctx.city));
}
function timings(d){
 const m=d.muhurtas||{};
 const groups=[['Auspicious / practice windows',[['Brahma Muhurta','brahma'],['Pratah Sandhya','pratah_sandhya'],['Abhijit Muhurta','abhijit'],['Vijaya Muhurta','vijaya'],['Godhuli','godhuli'],['Sayahna Sandhya','sayahna_sandhya'],['Nishita','nishita']]],['Caution windows',[['Rahu Kala','rahu_kaal'],['Yamaganda','yamaganda'],['Gulika Kala','gulika']]]];
 get('#tkDepthTiming').innerHTML=groups.map((g,i)=>'<section class="tk-depth-timing-col '+(i?'tk-depth-caution':'')+'"><h4>'+esc(g[0])+'</h4><dl>'+g[1].map(x=>'<div><dt>'+esc(x[0])+'</dt><dd>'+esc(m[x[1]]?m[x[1]].start_label+' – '+m[x[1]].end_label:'Not available')+'</dd></div>').join('')+'</dl></section>').join('');
}
function clock(){
 if(!day)return;const a=dt(day.sunrise),b=dt(day.sunset),c=dt(day.next_sunrise),now=new Date();
 if(!a||!b||!c||!(a<b&&b<c))return;
 if(now<a||now>=c){set('#tkDepthClock','00:00:00');set('#tkDepthClockLabel','Selected date · sunrise reference (not a live clock)');return}
 const val=scale===60?60*(now-a)/(c-a):now<b?30*(now-a)/(b-a):30+30*(now-b)/(c-b);
 const count=Math.max(0,Math.min(215999,Math.floor(val*3600))),pad=n=>String(n).padStart(2,'0');
 set('#tkDepthClock',pad(Math.floor(count/3600))+':'+pad(Math.floor(count%3600/60))+':'+pad(count%60));
 set('#tkDepthClockLabel',(scale===60?'Sunrise to next sunrise':now<b?'Daylight half':'Night half')+' · Ghati : Pal : Vipal');
}
function events(d){
 const all=d.upcoming||[];
 function feed(rows){return rows.length?rows.slice(0,5).map(x=>'<a class="tk-depth-event" href="'+esc(base+String(x.route||'').replace(/^\/+|\/+$/g,'')+'/')+'"><time>'+esc(x.date)+'</time><strong>'+esc(x.title)+'</strong><span>'+esc(x.subtitle||'')+'</span></a>').join(''):empty('No events in the selected feed window; this is not an exhaustive calendar.')}
 get('#tkDepthObservances').innerHTML=feed(all.filter(x=>x.type!=='planet'));
 get('#tkDepthPlanets').innerHTML=feed(all.filter(x=>x.type==='planet'));
}
async function load(detail){
 if(!detail?.date||!Number.isFinite(Number(detail.lat))||!Number.isFinite(Number(detail.lon)))return;
 ctx={...detail};const current=++request;abort?.abort();abort=new AbortController();
 if(clockTimer){clearInterval(clockTimer);clockTimer=null}day=null;
 set('#tkDepthContext','Calculating local Panchang…');
 get('#tkDepthTracks').innerHTML=empty('Calculating astronomical transitions…');
 get('#tkDepthObservances').innerHTML=empty('Loading observances…');
 get('#tkDepthPlanets').innerHTML=empty('Loading planetary events…');
 get('#tkDepthChart').innerHTML='';
 const result=await Promise.allSettled([api('panchang',payload(),abort.signal),api('home-dashboard',{...payload(),horizon_days:21},abort.signal)]);
 if(current!==request)return;
 if(result[0].status==='fulfilled'){day=result[0].value;timeline(day);summary(day);timings(day);clock();clockTimer=setInterval(clock,1000)}
 else if(result[0].reason?.name!=='AbortError'){set('#tkDepthContext','Daily Panchang unavailable: '+(result[0].reason?.message||'calculation error'));get('#tkDepthTracks').innerHTML=empty('No calculated transitions are available.');get('#tkDepthTiming').innerHTML=empty('Timings unavailable; example values are never substituted.')}
 if(result[1].status==='fulfilled')events(result[1].value);
 else if(result[1].reason?.name!=='AbortError'){get('#tkDepthObservances').innerHTML=empty('Event service unavailable.');get('#tkDepthPlanets').innerHTML=empty('Planetary events unavailable.')}
}
async function chart(){
 if(!ctx)return;const target=get('#tkDepthChart'),selected=ctx.date,time=get('#tkDepthChartTime').value;
 target.innerHTML=empty('Calculating Lagna and Graha placements…');
 try{
  const d=await api('kundali',{...payload(),time:time+':00'});
  if(selected!==ctx.date)return;
  const cells=d.d1?.cells||[];
  target.innerHTML='<strong>Lagna: '+esc(d.lagna?.rashi||'—')+' '+Number(d.lagna?.degree_in_rashi||0).toFixed(2)+'°</strong><div class="tk-depth-chart-grid">'+cells.map(x=>'<div class="tk-depth-chart-cell"><b>'+esc(x.rashi)+'</b><small>'+esc((x.planets||[]).map(z=>z.name).join(', ')||'—')+'</small></div>').join('')+'</div><small>Whole-sign D1 · Lahiri · '+esc(time)+' local. More layouts in the Kundali workspace.</small>';
 }catch(e){target.innerHTML=empty(e.message||'Chart unavailable')}
}
root.querySelectorAll('[data-depth-clock]').forEach(button=>button.addEventListener('click',()=>{scale=Number(button.dataset.depthClock);root.querySelectorAll('[data-depth-clock]').forEach(x=>x.setAttribute('aria-pressed',String(x===button)));clock()}));
get('#tkDepthLoadChart').addEventListener('click',chart);
window.addEventListener('tithika:context',e=>load(e.detail));
window.addEventListener('tithika:settings',()=>{const next=window.TithikaContext?.get?.();if(next)load(next)});
const initial=window.TithikaContext?.get?.();if(initial)load(initial);
window.addEventListener('pagehide',()=>{abort?.abort();if(clockTimer)clearInterval(clockTimer)},{once:true});
})();