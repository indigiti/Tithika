(()=>{"use strict";
const root=document.getElementById('tkKundaliWorkspace');if(!root)return;
const base=window.TITHIKA_BASE||'/',$=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const STORE='tithika.kundalis.v1',MAX=20;
let kundali=null,analysis=null,lastPayload=null,tab='charts';

const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function read(){try{const v=JSON.parse(localStorage.getItem(STORE)||'[]');return Array.isArray(v)?v.slice(0,MAX):[]}catch{return[]}}
function write(rows){try{localStorage.setItem(STORE,JSON.stringify(rows.slice(0,MAX)))}catch{}}
function saved(){const rows=read(),sel=$('#tkKundaliSaved');if(!sel)return;const current=sel.value;sel.innerHTML='<option value="">Open saved…</option>'+rows.map(x=>`<option value="${esc(x.id)}">${esc(x.name)} · ${esc(x.date)}</option>`).join('');if(rows.some(x=>x.id===current))sel.value=current}
function setStatus(msg){const el=$('#tkKundaliWorkspaceStatus');if(el)el.textContent=msg}

function planetText(cell){return (cell?.planets||[]).map(p=>esc(p.name)+(p.retrograde?' ℞':'')).join(' · ')||'—'}
function signMap(cells){return new Map((cells||[]).map(x=>[Number(x.rashi_id),x]))}
function houseMap(cells){return new Map((cells||[]).map(x=>[Number(x.house),x]))}

function south(cells,label){
 const order=[11,0,1,2,10,null,null,3,9,null,null,4,8,7,6,5],by=signMap(cells);
 return `<section class="tk-kw-chart"><header><b>${esc(label)}</b><small>South Indian · sign-fixed</small></header><div class="tk-kw-south">${order.map((id,i)=>id===null?`<div class="tk-kw-center">${i===5?esc(label):''}</div>`:(()=>{const x=by.get(id)||{};return `<div class="tk-kw-cell"><small>${esc(x.rashi||'')} · H${x.house||'—'}</small><strong>${planetText(x)}</strong></div>`})()).join('')}</div></section>`;
}
function north(cells,label){
 const by=houseMap(cells),order=[12,1,2,11,0,0,3,10,0,0,4,9,8,7,6,5];
 return `<section class="tk-kw-chart"><header><b>${esc(label)}</b><small>North Indian · house-focused</small></header><div class="tk-kw-north">${order.map(h=>h===0?'<div class="tk-kw-center"></div>':(()=>{const x=by.get(h)||{};return `<div class="tk-kw-cell"><small>H${h} · ${esc(x.rashi||'')}</small><strong>${planetText(x)}</strong></div>`})()).join('')}</div></section>`;
}
function east(cells,label){
 const by=signMap(cells),order=[0,1,2,3,11,null,null,4,10,null,null,5,9,8,7,6];
 return `<section class="tk-kw-chart"><header><b>${esc(label)}</b><small>East Indian · sign-grid presentation</small></header><div class="tk-kw-east">${order.map(id=>id===null?'<div class="tk-kw-center"></div>':(()=>{const x=by.get(id)||{};return `<div class="tk-kw-cell"><small>${esc(x.rashi||'')} · H${x.house||'—'}</small><strong>${planetText(x)}</strong></div>`})()).join('')}</div></section>`;
}
function west(cells,label){
 const by=houseMap(cells),items=[];
 for(let h=1;h<=12;h++){const x=by.get(h)||{},angle=(h-1)*30-90;items.push(`<div class="tk-kw-wheel-cell" style="--a:${angle}deg"><span><small>H${h} · ${esc(x.rashi||'')}</small><strong>${planetText(x)}</strong></span></div>`)}
 return `<section class="tk-kw-chart"><header><b>${esc(label)}</b><small>Western-style wheel · house order</small></header><div class="tk-kw-wheel">${items.join('')}<div class="tk-kw-wheel-center">${esc(label)}</div></div></section>`;
}
function chart(cells,label){
 const layout=$('#tkKundaliLayout')?.value||'south';
 return layout==='north'?north(cells,label):layout==='east'?east(cells,label):layout==='west'?west(cells,label):south(cells,label);
}

function renderCharts(){
 const charts=analysis?.charts||{};
 const d1=charts.D1?.cells||kundali?.d1?.cells||[],d9=charts.D9?.cells||kundali?.d9?.cells||[],d10=charts.D10?.cells||[];
 return `<div class="tk-kw-note">Layout changes presentation only; planetary longitudes, houses and all derived calculations remain unchanged.</div><div class="tk-kw-chart-grid">${chart(d1,'D1 · Rashi')}${chart(d9,'D9 · Navamsha')}${d10.length?chart(d10,'D10 · Dashamsha'):''}</div>`;
}
function renderGraha(){
 const rows=kundali?.d1?.placements||analysis?.charts?.D1?.placements||[];
 return `<div class="tk-kw-table"><div class="head"><b>Graha</b><b>Rashi</b><b>House</b><b>Degree</b><b>Motion</b></div>${rows.map(x=>`<div><strong>${esc(x.name)}</strong><span>${esc(x.rashi)}</span><span>H${x.house||'—'}</span><span>${Number(x.degree_in_rashi||0).toFixed(2)}°</span><span>${x.retrograde?'Retrograde':'Direct'}</span></div>`).join('')}</div>`;
}
function renderYogas(){
 const rows=analysis?.yogas?.items||[];
 return rows.length?`<div class="tk-yoga-list">${rows.map(y=>`<article><div class="tk-yoga-title"><span>${esc(y.category)}</span><h4>${esc(y.name)}</h4></div><p>${esc(y.rule)}</p></article>`).join('')}</div>`:'<div class="tk-panchang-empty">No Yoga from the current curated detector was returned.</div>';
}
function renderDasha(){
 const current=analysis?.dasha?.current||{},md=current.mahadasha||{},ad=current.antardasha||{},pd=ad.current_pratyantardasha||{};
 const active=analysis?.timing?.active_dasha_lords||[];
 return `<div class="tk-kw-summary"><article><small>Mahadasha</small><b>${esc(md.lord||'—')}</b><span>${esc(md.full_end||md.end||'')}</span></article><article><small>Antardasha</small><b>${esc(ad.lord||'—')}</b><span>${esc(ad.full_end||ad.end||'')}</span></article><article><small>Pratyantardasha</small><b>${esc(pd.lord||'—')}</b><span>${esc(pd.full_end||pd.end||'')}</span></article></div><div class="tk-analysis-timing">${active.map(x=>`<article><b>${esc(x.level)} · ${esc(x.planet)}</b><span>Natal H${x.natal_house||'—'} · ${esc(x.natal_rashi||'—')} · strength ${x.strength_ratio==null?'—':Number(x.strength_ratio).toFixed(2)+'×'}</span></article>`).join('')}</div>`;
}
function renderShadbala(){
 const rows=analysis?.strengths||[];
 return `<div class="tk-analysis-strengths">${rows.map(x=>`<span><b>${esc(x.planet)}</b><strong class="${x.meets_required?'pass':'fail'}">${Number(x.ratio||0).toFixed(2)}×</strong><small>${Number(x.total_rupa||0).toFixed(2)} / ${Number(x.required_rupa||0).toFixed(1)} Rupa</small></span>`).join('')}</div><div class="tk-kw-note">Shadbala measures planetary capacity; it does not by itself classify a planet as beneficial or harmful.</div>`;
}
function renderAshta(){
 const a=analysis?.ashtakavarga||{},rows=a.rows||[];
 return `<div class="tk-kw-summary"><article><small>SAV total</small><b>${a.sav_total??'—'}</b><span>Expected 337</span></article><article><small>Integrity</small><b>${a.integrity_valid?'Valid':'Review'}</b><span>Raw BAV/SAV checks</span></article></div><div class="tk-kw-ashta">${rows.map(x=>`<span><small>H${x.house} · ${esc(x.rashi)}</small><b>${x.sav}</b></span>`).join('')}</div>`;
}
function render(){
 const panel=$('#tkKundaliWorkspacePanel');if(!panel)return;
 if(!kundali){panel.innerHTML='<div class="tk-panchang-empty">Build a Kundali to load this workspace.</div>';return}
 const map={charts:renderCharts,graha:renderGraha,yogas:renderYogas,dasha:renderDasha,shadbala:renderShadbala,ashtakavarga:renderAshta};
 panel.innerHTML=(map[tab]||renderCharts)();
}
async function fullAnalysis(payload){
 setStatus('Loading D1/D9/D10, Yogas, Dasha, Shadbala and Ashtakavarga…');
 try{
  const r=await fetch(`${base}api.php?action=horoscope-analysis`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const j=await r.json();if(!r.ok||!j.ok)throw new Error(j.error||'Full analysis unavailable');
  analysis=j;setStatus('Full evidence workspace ready · Lahiri / Chitrapaksha · whole-sign houses');render();
 }catch(e){analysis=null;setStatus('Basic Kundali ready; full evidence workspace could not load.');render()}
}

window.addEventListener('tithika:kundali',e=>{
 kundali=e.detail?.data||null;lastPayload=e.detail?.payload||null;analysis=null;
 if(kundali&&lastPayload){setStatus('Kundali ready; loading full evidence workspace…');render();fullAnalysis(lastPayload)}
});

$$('[data-kundali-tab]').forEach(btn=>btn.addEventListener('click',()=>{tab=btn.dataset.kundaliTab;$$('[data-kundali-tab]').forEach(x=>x.classList.toggle('is-active',x===btn));render()}));
$('#tkKundaliLayout')?.addEventListener('change',render);

$('#tkKundaliSave')?.addEventListener('click',()=>{
 if(!lastPayload)return setStatus('Build the Kundali before saving.');
 const name=String($('#tkKundaliName')?.value||'').trim()||'Saved Kundali';
 const ctx=window.TithikaContext?.get?.()||{};
 const row={id:'k'+Date.now(),name:name.slice(0,60),date:lastPayload.date||ctx.date,time:lastPayload.time||$('#tkKundaliTime')?.value||'12:00:00',node_model:lastPayload.node_model||'mean',lat:Number(lastPayload.lat??ctx.lat),lon:Number(lastPayload.lon??ctx.lon),city:String(lastPayload.city||ctx.city||'Saved location').slice(0,120),timezone:String(lastPayload.timezone||ctx.timezone||'Asia/Kolkata').slice(0,80),layout:$('#tkKundaliLayout')?.value||'south'};
 const rows=read();rows.unshift(row);write(rows.filter((x,i,a)=>a.findIndex(y=>y.id===x.id)===i));saved();$('#tkKundaliSaved').value=row.id;setStatus(`${name} saved on this device only.`);
});

$('#tkKundaliSaved')?.addEventListener('change',async e=>{
 const row=read().find(x=>x.id===e.target.value);if(!row)return;
 $('#tkKundaliName').value=row.name||'';$('#tkKundaliTime').value=row.time||'12:00:00';$('#tkKundaliNode').value=row.node_model||'mean';$('#tkKundaliLayout').value=row.layout||'south';
 setStatus(`Opening ${row.name}…`);
 const ok=await window.TithikaContext?.set?.(row);
 if(!ok)setStatus('Could not apply the saved chart context.');
});
$('#tkKundaliDelete')?.addEventListener('click',()=>{
 const id=$('#tkKundaliSaved')?.value;if(!id)return;
 write(read().filter(x=>x.id!==id));saved();$('#tkKundaliName').value='';setStatus('Saved Kundali removed from this device.');
});

saved();render();
})();