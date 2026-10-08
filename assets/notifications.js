(() => {
  'use strict';

  const settings=window.TithikaSettings;
  if(!settings)return;

  const base=window.TITHIKA_BASE||'/';
  const page=document.getElementById('tkNotificationCenter');
  const list=document.getElementById('tkNotifyAgendaList');
  const feed=document.getElementById('tkNotifyFeed');
  const feedPreview=document.getElementById('tkNotifyFeedPreview');
  const copyFeed=document.getElementById('tkNotifyCopyFeed');
  const permissionButton=document.getElementById('tkNotifyPermission');
  const permissionState=document.getElementById('tkNotifyPermissionState');
  const messages=window.TITHIKA_I18N?.messages||{};
  const tr=(key,fallback)=>messages[key]||fallback||key;
  const esc=(value='')=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const routeUrl=route=>base+String(route||'').replace(/^\/+|\/+$/g,'')+'/';
  const defaultCategories=['ekadashi','purnima','amavasya','sankashti','pradosh','shivaratri','sankranti','festivals','transit','retrograde'];
  let activeContext=null;
  let controller=null;
  let lastAgendaKey='';

  function selectedCategories(){
    const value=settings.get().notificationCategories;
    return Array.isArray(value)&&value.length?value:defaultCategories;
  }

  function context(){
    const live=window.TithikaContext?.get?.();
    if(live&&Number.isFinite(Number(live.lat))&&Number.isFinite(Number(live.lon))) return live;
    const saved=settings.get().defaultLocation;
    if(saved) return {...saved,date:new Date().toISOString().slice(0,10)};
    return {lat:19.0760,lon:72.8777,city:'Current location',timezone:'Asia/Kolkata',date:new Date().toISOString().slice(0,10)};
  }

  function payload(ctx,horizon=90){
    const s=settings.get();
    return {
      lat:Number(ctx.lat),lon:Number(ctx.lon),city:String(ctx.city||'Current location'),
      timezone:String(ctx.timezone||'Asia/Kolkata'),date:String(ctx.date||new Date().toISOString().slice(0,10)),
      horizon_days:horizon,tradition:s.tradition||'smarta',hour24:s.clock==='24',
      categories:selectedCategories()
    };
  }

  function calendarUrl(ctx){
    const p=payload(ctx,90);
    const url=new URL(base+'calendar.ics',window.location.origin);
    url.searchParams.set('lat',String(p.lat));
    url.searchParams.set('lon',String(p.lon));
    url.searchParams.set('city',p.city);
    url.searchParams.set('timezone',p.timezone);
    url.searchParams.set('date',p.date);
    url.searchParams.set('days','90');
    url.searchParams.set('tradition',p.tradition);
    url.searchParams.set('categories',p.categories.join(','));
    return url.toString();
  }

  function applyCategoryButtons(){
    if(!page)return;
    const selected=new Set(selectedCategories());
    document.querySelectorAll('[data-notify-category]').forEach(button=>{
      const on=selected.has(button.dataset.notifyCategory);
      button.classList.toggle('is-selected',on);
      button.setAttribute('aria-pressed',on?'true':'false');
    });
  }

  function updateFeed(ctx){
    if(!page)return;
    const url=calendarUrl(ctx);
    if(feed)feed.href=url;
    if(feedPreview)feedPreview.textContent=url;
  }

  function formatDate(value,timeZone){
    try{
      const s=settings.get();
      return new Intl.DateTimeFormat(settings.locale(),{
        numberingSystem:settings.numberingSystem(),timeZone:timeZone||'Asia/Kolkata',
        weekday:'short',day:'numeric',month:'short'
      }).format(new Date(value+'T12:00:00'));
    }catch(e){return value}
  }

  function formatTime(value,timeZone){
    if(!value)return '';
    try{
      const s=settings.get();
      return new Intl.DateTimeFormat(settings.locale(),{
        numberingSystem:settings.numberingSystem(),timeZone:timeZone||'Asia/Kolkata',
        hour:'numeric',minute:'2-digit',hour12:s.clock!=='24'
      }).format(new Date(value));
    }catch(e){return ''}
  }

  function renderAgenda(data){
    if(!list)return;
    const rows=data.events||[];
    const tz=data.location?.timezone||'Asia/Kolkata';
    if(!rows.length){
      list.innerHTML='<div class="tk-upcoming-empty">'+esc(tr('notifications.empty','No selected events fall inside this horizon.'))+'</div>';
      return;
    }
    list.innerHTML=rows.map(row=>{
      const time=row.all_day?'':formatTime(row.start,tz);
      return '<a class="tk-notify-event kind-'+esc(row.kind||'event')+'" href="'+esc(routeUrl(row.route))+'">'+
        '<time><b>'+esc(formatDate(row.date,tz))+'</b><small>'+esc(time)+'</small></time>'+
        '<div><span>'+esc(row.kind||'event')+'</span><h3>'+esc(row.title||'Tithika event')+'</h3><p>'+esc(row.subtitle||'Verified Tithika event')+'</p></div>'+
        '<i aria-hidden="true">↗</i></a>';
    }).join('');
  }

  async function fetchAgenda(ctx,horizon=90,render=true){
    const p=payload(ctx,horizon);
    const key=JSON.stringify(p);
    if(render&&key===lastAgendaKey)return null;
    if(render)lastAgendaKey=key;
    controller?.abort();
    controller=new AbortController();
    try{
      const response=await fetch(base+'api.php?action=notification-agenda',{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p),signal:controller.signal
      });
      const data=await response.json();
      if(!response.ok||!data.ok)throw new Error(data.error||'Notification agenda unavailable');
      if(render)renderAgenda(data);
      return data;
    }catch(error){
      if(error.name==='AbortError')return null;
      if(render&&list)list.innerHTML='<div class="tk-upcoming-empty">'+esc(tr('notifications.error','The notification agenda could not be loaded.'))+'</div>';
      return null;
    }
  }

  function permissionLabel(){
    if(!permissionButton||!permissionState)return;
    if(!('Notification' in window)){
      permissionButton.hidden=true;
      permissionState.textContent='Browser notifications are not supported.';
      return;
    }
    const s=settings.get();
    if(Notification.permission==='granted'){
      permissionButton.textContent=s.onsiteAlerts?tr('notifications.disable','Turn off on-site alerts'):tr('notifications.enable','Enable browser permission');
      permissionState.textContent=tr('notifications.permission_granted','Browser permission granted');
    }else if(Notification.permission==='denied'){
      permissionButton.textContent=tr('notifications.enable','Enable browser permission');
      permissionState.textContent=tr('notifications.permission_denied','Browser permission is blocked');
    }else{
      permissionButton.textContent=tr('notifications.enable','Enable browser permission');
      permissionState.textContent='';
    }
  }

  async function requestAlerts(){
    if(!('Notification' in window))return;
    const current=settings.get();
    if(Notification.permission==='granted'&&current.onsiteAlerts){
      settings.set({onsiteAlerts:false});
      permissionLabel();
      return;
    }
    const result=await Notification.requestPermission();
    settings.set({onsiteAlerts:result==='granted'});
    permissionLabel();
    if(result==='granted')surfaceAlerts(activeContext||context());
  }

  function notifiedStore(){
    try{return JSON.parse(localStorage.getItem('tithika.notified.v1')||'{}')}catch(e){return {}}
  }

  function saveNotified(store){
    const cutoff=new Date();cutoff.setDate(cutoff.getDate()-14);
    const trimmed={};
    for(const [key,value] of Object.entries(store)){
      if(typeof value==='string'&&value>=cutoff.toISOString().slice(0,10))trimmed[key]=value;
    }
    try{localStorage.setItem('tithika.notified.v1',JSON.stringify(trimmed))}catch(e){}
  }

  async function surfaceAlerts(ctx){
    const s=settings.get();
    if(!s.onsiteAlerts||!('Notification' in window)||Notification.permission!=='granted')return;
    const data=await fetchAgenda(ctx,2,false);
    if(!data)return;
    const today=String(ctx.date||new Date().toISOString().slice(0,10));
    const tomorrow=new Date(today+'T12:00:00');tomorrow.setDate(tomorrow.getDate()+1);
    const tomorrowIso=tomorrow.toISOString().slice(0,10);
    const store=notifiedStore();
    let shown=0;
    for(const row of data.events||[]){
      if(shown>=3)break;
      if(row.date!==today&&row.date!==tomorrowIso)continue;
      const key=row.id+'|'+row.date;
      if(store[key])continue;
      const n=new Notification(row.title||'Tithika reminder',{
        body:(row.date===today?tr('dynamic.today','Today'):tr('dynamic.tomorrow','Tomorrow'))+(row.subtitle?' · '+row.subtitle:''),
        tag:'tithika-'+row.id
      });
      n.onclick=()=>{window.focus();window.location.href=routeUrl(row.route);n.close();};
      store[key]=today;shown++;
    }
    if(shown)saveNotified(store);
  }

  document.querySelectorAll('[data-notify-category]').forEach(button=>button.addEventListener('click',()=>{
    const selected=new Set(selectedCategories());
    const key=button.dataset.notifyCategory;
    if(selected.has(key)&&selected.size>1)selected.delete(key);else selected.add(key);
    settings.set({notificationCategories:[...selected]});
    lastAgendaKey='';
    applyCategoryButtons();
    const ctx=activeContext||context();
    updateFeed(ctx);
    fetchAgenda(ctx);
  }));

  permissionButton?.addEventListener('click',requestAlerts);
  copyFeed?.addEventListener('click',async()=>{
    const url=calendarUrl(activeContext||context());
    try{
      await navigator.clipboard.writeText(url);
      window.dispatchEvent(new CustomEvent('tithika:toast',{detail:tr('notifications.copied','Feed URL copied')}));
    }catch(e){
      if(feedPreview){const range=document.createRange();range.selectNodeContents(feedPreview);const sel=window.getSelection();sel.removeAllRanges();sel.addRange(range);}
    }
  });

  function activate(ctx){
    activeContext=ctx||context();
    if(page){
      applyCategoryButtons();
      permissionLabel();
      updateFeed(activeContext);
      lastAgendaKey='';
      fetchAgenda(activeContext);
    }
    surfaceAlerts(activeContext);
  }

  window.addEventListener('tithika:context',e=>activate(e.detail||context()));
  window.addEventListener('tithika:settings',()=>{
    applyCategoryButtons();
    const ctx=activeContext||context();
    updateFeed(ctx);
    lastAgendaKey='';
    if(page)fetchAgenda(ctx);
  });
  setTimeout(()=>activate(context()),0);
})();