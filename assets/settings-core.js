(() => {
  'use strict';
  const KEY='tithika.settings.v1';
  const defaults={
    schema:1,
    theme:'system',
    clock:'12',
    lunarMonth:'amanta',
    tradition:'smarta',
    language:'en',
    defaultLocation:null
  };
  const allowed={
    theme:new Set(['system','light','dark']),
    clock:new Set(['12','24']),
    lunarMonth:new Set(['amanta','purnimanta']),
    tradition:new Set(['smarta','vaishnava','iskcon']),
    language:new Set(['en'])
  };
  function safe(raw){
    const out={...defaults};
    if(!raw||typeof raw!=='object')return out;
    for(const key of Object.keys(allowed)){
      if(allowed[key].has(String(raw[key]??'')))out[key]=String(raw[key]);
    }
    const loc=raw.defaultLocation;
    if(loc&&Number.isFinite(Number(loc.lat))&&Number.isFinite(Number(loc.lon))&&typeof loc.city==='string'&&typeof loc.timezone==='string'){
      out.defaultLocation={
        lat:Number(loc.lat),lon:Number(loc.lon),
        city:loc.city.slice(0,120),timezone:loc.timezone.slice(0,80)
      };
    }
    return out;
  }
  function read(){
    try{return safe(JSON.parse(localStorage.getItem(KEY)||'{}'))}catch(e){return {...defaults}}
  }
  let state=read();
  function persist(){try{localStorage.setItem(KEY,JSON.stringify(state))}catch(e){}}
  function resolvedTheme(){
    if(state.theme!=='system')return state.theme;
    return window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
  }
  function apply(){
    document.documentElement.dataset.tkTheme=resolvedTheme();
    document.documentElement.style.colorScheme=resolvedTheme();
  }
  function set(patch){
    state=safe({...state,...patch});persist();apply();
    window.dispatchEvent(new CustomEvent('tithika:settings',{detail:get()}));
    return get();
  }
  function saveLocation(location){
    if(!location)return set({defaultLocation:null});
    return set({defaultLocation:{
      lat:Number(location.lat),lon:Number(location.lon),
      city:String(location.city||'Saved location').slice(0,120),
      timezone:String(location.timezone||'Asia/Kolkata').slice(0,80)
    }});
  }
  function get(){return JSON.parse(JSON.stringify(state))}
  function hour24(){return state.clock==='24'}
  function formatNumber(value){
    return new Intl.NumberFormat(state.language==='en'?'en-IN':'en-IN').format(value);
  }
  window.TithikaSettings={get,set,saveLocation,clearLocation:()=>saveLocation(null),apply,hour24,formatNumber,key:KEY};
  apply();
  if(window.matchMedia){
    const media=window.matchMedia('(prefers-color-scheme: dark)');
    media.addEventListener?.('change',()=>{if(state.theme==='system')apply()});
  }
})();