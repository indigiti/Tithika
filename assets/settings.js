(() => {
  'use strict';
  const settings=window.TithikaSettings;
  if(!settings)return;
  const $=s=>document.querySelector(s);
  const $$=s=>[...document.querySelectorAll(s)];
  const messages=window.TITHIKA_I18N?.messages||{};
  const tr=(key,fallback)=>messages[key]||fallback||key;

  function render(){
    const s=settings.get();
    $$('[data-setting]').forEach(group=>{
      const key=group.dataset.setting;
      group.querySelectorAll('[data-value]').forEach(btn=>{
        const active=String(s[key])===String(btn.dataset.value);
        btn.classList.toggle('is-selected',active);
        btn.setAttribute('aria-pressed',active?'true':'false');
      });
    });
    const loc=s.defaultLocation;
    $('#tkSettingsLocationName').textContent=loc&&loc.city?loc.city:tr('settings.no_location','No saved location');
    $('#tkSettingsLocationMeta').textContent=loc
      ? (loc.timezone+' · '+settings.formatDecimal(loc.lat,4)+', '+settings.formatDecimal(loc.lon,4)+' · '+settings.formatNumber(Math.round(Number(loc.elevation||0)))+' m')
      : tr('settings.location_fallback','Tithika will continue using geolocation or the standard fallback.');
    if(loc){
      if($('#tkManualCity')) $('#tkManualCity').value=loc.city||'';
      if($('#tkManualLat')) $('#tkManualLat').value=Number(loc.lat).toFixed(6);
      if($('#tkManualLon')) $('#tkManualLon').value=Number(loc.lon).toFixed(6);
      if($('#tkManualTimezone')) $('#tkManualTimezone').value=loc.timezone||'';
      if($('#tkManualElevation')) $('#tkManualElevation').value=String(Math.round(Number(loc.elevation||0)));
    }
  }

  $$('[data-setting] [data-value]').forEach(btn=>btn.addEventListener('click',()=>{
    const group=btn.closest('[data-setting]');
    if(!group)return;
    const key=group.dataset.setting;
    const before=settings.get()[key];
    settings.set({[key]:btn.dataset.value});
    render();
    if(key==='language' && before!==btn.dataset.value){
      const url=new URL(window.location.href);
      url.searchParams.set('lang',btn.dataset.value);
      window.location.href=url.toString();
    }
  }));

  $('#tkSaveCurrentLocation')?.addEventListener('click',()=>{
    const current=window.TithikaContext?.get?.();
    if(current && Number.isFinite(Number(current.lat)) && Number.isFinite(Number(current.lon))){
      settings.saveLocation(current);
      render();
      window.dispatchEvent(new CustomEvent('tithika:toast',{detail:tr('dynamic.location_saved','Default location saved on this device.')}));
    }
  });

  $('#tkClearSavedLocation')?.addEventListener('click',()=>{
    settings.clearLocation();
    render();
  });

  function timezoneValid(value){
    try{
      new Intl.DateTimeFormat('en-US',{timeZone:value}).format(new Date());
      return true;
    }catch(e){return false}
  }

  $('#tkSaveManualLocation')?.addEventListener('click',()=>{
    const lat=Number($('#tkManualLat')?.value);
    const lon=Number($('#tkManualLon')?.value);
    const elevation=Number($('#tkManualElevation')?.value||0);
    const timezone=String($('#tkManualTimezone')?.value||'').trim();
    const city=String($('#tkManualCity')?.value||'Manual location').trim().slice(0,120)||'Manual location';
    const valid=Number.isFinite(lat)&&lat>=-90&&lat<=90&&Number.isFinite(lon)&&lon>=-180&&lon<=180&&Number.isFinite(elevation)&&elevation>=-500&&elevation<=9000&&timezoneValid(timezone);
    if(!valid){
      window.dispatchEvent(new CustomEvent('tithika:toast',{detail:tr('settings.invalid_location','Enter valid latitude, longitude, timezone and elevation.')}));
      return;
    }
    const loc={lat,lon,city,timezone,elevation};
    settings.saveLocation(loc);
    window.TithikaContext?.set?.(loc);
    render();
    window.dispatchEvent(new CustomEvent('tithika:toast',{detail:tr('settings.manual_saved','Manual location saved on this device.')}));
  });

  render();
})();