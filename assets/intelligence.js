(() => {
  'use strict';
  const base = window.TITHIKA_BASE || '/';
  const $ = (s, root=document) => root.querySelector(s);
  const $$ = (s, root=document) => [...root.querySelectorAll(s)];
  const state = {
    view: 'ask',
    lat: 18.5204,
    lon: 73.8567,
    city: 'Pune, Maharashtra, India',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata',
    searchTimer: null,
  };

  const titles = {
    ask: ['Conversational Tithika','Ask across the whole stack.'],
    advisor: ['Panchang / Muhurat Advisor','Rank verified timing windows.'],
    jyotish: ['Jyotish Intelligence','Fuse the chart, strength and timing layers.'],
    profile: ['Recommendation / Profile','Make ranking preference-aware.'],
    quality: ['Quality AI','Audit cross-engine consistency.'],
  };

  function todayISO(){
    const parts=new Intl.DateTimeFormat('en-CA',{timeZone:state.timezone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
    const m=Object.fromEntries(parts.map(x=>[x.type,x.value]));
    return `${m.year}-${m.month}-${m.day}`;
  }
  function esc(v=''){
    return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  function setView(view){
    if(!titles[view]) return;
    state.view=view;
    $$('.ti-nav-link,.ti-layer').forEach(x=>x.classList.toggle('is-active',x.dataset.view===view));
    $('#tiStageKicker').textContent=titles[view][0];
    $('#tiStageTitle').textContent=titles[view][1];
    $('#tiEmpty').hidden=false; $('#tiResult').hidden=true; $('#tiLoading').hidden=true;
  }
  $$('.ti-nav-link,.ti-layer').forEach(x=>x.addEventListener('click',()=>setView(x.dataset.view)));

  function payload(extra={}){
    return {
      lat:state.lat,lon:state.lon,city:state.city,timezone:state.timezone,
      date:$('#tiDate').value,time:$('#tiTime').value,
      target_date:todayISO(),
      purpose:$('#tiPurpose').value,range:$('#tiRange').value,
      node_model:'mean',hour24:false,
      ...extra
    };
  }

  async function call(mode, extra={}){
    const response=await fetch(`${base}api.php?action=ai-${encodeURIComponent(mode)}`,{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload({mode,...extra}))
    });
    let data;
    try{data=await response.json()}catch(e){throw new Error(`Intelligence endpoint returned HTTP ${response.status}`)}
    if(!response.ok || !data.ok) throw new Error(data.error||`Intelligence request failed (${response.status})`);
    return data;
  }

  function loading(message='Building an explainable answer…'){
    $('#tiEmpty').hidden=true; $('#tiResult').hidden=true; $('#tiLoading').hidden=false;
    $('#tiLoadingText').textContent=message;
  }
  function fail(message){
    $('#tiLoading').hidden=true;$('#tiResult').hidden=false;
    $('#tiResult').innerHTML=`<div class="ti-result-hero"><small>Request needs attention</small><h3>Unable to complete this intelligence pass.</h3><p>${esc(message)}</p></div>`;
  }

  function renderEvidence(data){
    const intel=data.intelligence||{};
    const conf=intel.confidence||{};
    const score=Math.round(Number(conf.score||0)*100);
    $('#tiConfidence').textContent=score?`${score}%`:'—';
    $('#tiConfidenceBar').style.width=`${score}%`;
    const rows=intel.provenance||[];
    $('#tiProvenance').innerHTML=rows.length?rows.map(s=>`
      <div class="ti-source">
        <b>${esc(s.engine||'Unknown engine')}</b>
        <span>v${esc(s.version||'unknown')}</span>
        <em>${esc((s.category||'source').replaceAll('-',' '))}</em>
      </div>`).join(''):'<p>No deterministic engine was needed for this response.</p>';
  }

  function recommendations(rows=[]){
    if(!rows.length)return '<div class="ti-fact"><small>Result</small><b>No ranked window found</b><p>Try another date, range or purpose.</p></div>';
    return `<div class="ti-cards">${rows.slice(0,8).map((r,i)=>`
      <article class="ti-rec">
        <div class="ti-rec-rank">${String(i+1).padStart(2,'0')}</div>
        <div><b>${esc(r.name||'Timing window')}</b><small>${esc(r.date||'')} · ${esc(r.start_label||'')} – ${esc(r.end_label||'')} ${r.cautions?.length?'· '+esc(r.cautions.join(', ')):''}</small></div>
        <div class="ti-rec-score"><b>${esc(r.personal_score??r.score??'—')}</b><small>rank</small></div>
      </article>`).join('')}</div>`;
  }

  function renderAdvisor(a){
    return `<div class="ti-result-hero"><small>Traditional timing advisor</small><h3>${esc(a.purpose||'General')} · ${esc(a.range||'today')}</h3><p>${esc(a.summary||a.method||'')}</p></div>${recommendations(a.recommendations||[])}`;
  }
  function renderJyotish(j){
    const sig=j.birth_signature||{}, strengths=j.strengths||[], d=j.current_dasha||{};
    return `
      <div class="ti-result-hero"><small>Multi-engine Jyotish synthesis</small><h3>${esc(sig.lagna?.rashi||'Chart')} · ${esc(sig.moon_rashi||'')} Moon</h3><p>${esc(j.summary||'')}</p></div>
      <div class="ti-grid2">
        <div class="ti-fact"><small>Birth signature</small><b>${esc(sig.nakshatra||'—')} ${sig.nakshatra_pada?'· Pada '+esc(sig.nakshatra_pada):''}</b><p>Sun ${esc(sig.sun_rashi||'—')} · Moon ${esc(sig.moon_rashi||'—')}</p></div>
        <div class="ti-fact"><small>Current Vimshottari</small><b>${esc(d.mahadasha||'—')} ${d.antardasha?'→ '+esc(d.antardasha):''}</b><p>Current Mahadasha / Antardasha from the deterministic Dasha engine.</p></div>
      </div>
      <div class="ti-cards">${strengths.slice(0,7).map((r,i)=>`<article class="ti-rec"><div class="ti-rec-rank">${String(i+1).padStart(2,'0')}</div><div><b>${esc(r.planet)}</b><small>${r.meets_required?'Meets':'Below'} declared Shadbala threshold · ${esc(r.rupa??'—')} Rupa</small></div><div class="ti-rec-score"><b>${Number(r.ratio||0).toFixed(2)}×</b><small>strength</small></div></article>`).join('')}</div>`;
  }
  function renderQuality(q){
    return `<div class="ti-result-hero"><small>Cross-engine audit</small><h3>Status: ${esc(String(q.status||'unknown').toUpperCase())}</h3><p>${esc(q.policy||'')}</p></div><div class="ti-cards">${(q.checks||[]).map((r,i)=>`<article class="ti-rec"><div class="ti-rec-rank">${r.level==='error'?'!':r.level==='warning'?'△':'✓'}</div><div><b>${esc(r.check||'check')}</b><small>${esc(r.message||'')}</small></div><div class="ti-rec-score"><small>${esc(r.level||'info')}</small></div></article>`).join('')}</div>`;
  }
  function renderProfile(p){
    return `<div class="ti-result-hero"><small>Preference-aware ranking</small><h3>${esc(p.preferences?.purpose||'General')} profile</h3><p>${esc(p.explanation||'')}</p></div>${recommendations(p.recommendations||[])}`;
  }
  function renderConversation(c){
    let nested='';
    if(c.result?.recommendations) nested=recommendations(c.result.recommendations);
    else if(c.result?.strengths) nested=renderJyotish(c.result);
    else if(c.result?.checks) nested=renderQuality(c.result);
    return `<div class="ti-result-hero"><small>${esc(c.intent||'conversation')}</small><h3>${esc(c.answer||'Tithika Intelligence')}</h3><p>${esc(c.question||'')}</p></div>${nested}`;
  }
  function render(data){
    $('#tiLoading').hidden=true;$('#tiEmpty').hidden=true;$('#tiResult').hidden=false;
    renderEvidence(data);
    let html='';
    if(data.conversation)html=renderConversation(data.conversation);
    else if(data.advisor)html=renderAdvisor(data.advisor);
    else if(data.jyotish)html=renderJyotish(data.jyotish);
    else if(data.profile)html=renderProfile(data.profile);
    else if(data.quality)html=renderQuality(data.quality);
    else html='<div class="ti-result-hero"><small>Intelligence</small><h3>Request complete.</h3><p>The verified intelligence layer returned successfully.</p></div>';
    $('#tiResult').innerHTML=html;
  }

  async function run(mode=state.view){
    try{
      if(mode==='ask'){
        const question=$('#tiQuestion').value.trim();
        if(!question){$('#tiQuestion').focus();return}
        loading('Routing your question across the intelligence stack…');
        render(await call('ask',{question}));
      }else if(mode==='advisor'){
        loading('Ranking Panchang and Muhurat windows…'); render(await call('advisor'));
      }else if(mode==='jyotish'){
        loading('Fusing Kundali, Shadbala, D9, Yogas, Dasha and transits…'); render(await call('jyotish'));
      }else if(mode==='profile'){
        loading('Applying preferences after verified timing calculations…');
        render(await call('profile',{preferences:{purpose:$('#tiPurpose').value,range:$('#tiRange').value,prefer_daytime:true,language:'en'}}));
      }else if(mode==='quality'){
        loading('Comparing independent engine invariants…'); render(await call('quality'));
      }
    }catch(e){fail(e.message||'Unknown intelligence error')}
  }
  $('#tiAsk').addEventListener('click',()=>{setView('ask');run('ask')});
  $('#tiRunCurrent').addEventListener('click',()=>run());
  $('#tiQuestion').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();setView('ask');run('ask')}});
  $$('[data-prompt]').forEach(b=>b.addEventListener('click',()=>{$('#tiQuestion').value=b.dataset.prompt;setView('ask');run('ask')}));

  $('#tiTheme').addEventListener('click',()=>{
    const html=document.documentElement;
    const next=html.dataset.theme==='dark'?'light':'dark';
    html.dataset.theme=next;localStorage.setItem('tithika-intelligence-theme',next);
  });
  const savedTheme=localStorage.getItem('tithika-intelligence-theme');
  if(savedTheme==='light'||savedTheme==='dark')document.documentElement.dataset.theme=savedTheme;

  async function health(){
    try{
      const data=await call('health');
      $('#tiSystemStatus').classList.add('is-online');
      $('#tiSystemStatus').innerHTML='<i></i>Intelligence online';
      $('#tiEngineCount').textContent=`${data.health?.engines?.length||0} engines`;
    }catch(e){
      $('#tiSystemStatus').innerHTML='<i></i>Core unavailable';
    }
  }

  async function resolveTimezone(){
    try{
      const r=await fetch(`${base}api.php?action=timezone&lat=${encodeURIComponent(state.lat)}&lon=${encodeURIComponent(state.lon)}`);
      const j=await r.json();if(j.ok&&j.timezone)state.timezone=j.timezone;
    }catch(e){}
  }
  async function reverse(){
    try{
      const r=await fetch(`${base}api.php?action=reverse&lat=${encodeURIComponent(state.lat)}&lon=${encodeURIComponent(state.lon)}`);
      const j=await r.json();if(j.ok&&j.label){state.city=j.label;$('#tiCity').value=j.label}
    }catch(e){}
  }
  $('#tiLocate').addEventListener('click',()=>{
    if(!navigator.geolocation)return;
    navigator.geolocation.getCurrentPosition(async p=>{
      state.lat=p.coords.latitude;state.lon=p.coords.longitude;
      await Promise.all([reverse(),resolveTimezone()]);
    },()=>{}, {timeout:7000,maximumAge:600000});
  });

  $('#tiCity').addEventListener('input',e=>{
    clearTimeout(state.searchTimer);
    const q=e.target.value.trim(), box=$('#tiPlaces');
    if(q.length<2){box.hidden=true;return}
    state.searchTimer=setTimeout(async()=>{
      try{
        const r=await fetch(`${base}api.php?action=search&q=${encodeURIComponent(q)}`);
        const j=await r.json();
        const rows=j.results||[];box._rows=rows;
        box.innerHTML=rows.map((x,i)=>`<button class="ti-place" data-i="${i}" type="button"><b>${esc(x.label)}</b><small>${esc(x.display_name)}</small></button>`).join('');
        box.hidden=!rows.length;
        $$('.ti-place',box).forEach(btn=>btn.addEventListener('click',async()=>{
          const x=box._rows[Number(btn.dataset.i)];
          state.lat=Number(x.lat);state.lon=Number(x.lon);state.city=x.label;$('#tiCity').value=x.label;box.hidden=true;
          await resolveTimezone();
        }));
      }catch(err){box.hidden=true}
    },280);
  });
  document.addEventListener('click',e=>{if(!e.target.closest('#tiCity')&&!e.target.closest('#tiPlaces'))$('#tiPlaces').hidden=true});

  health();
})();