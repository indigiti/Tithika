(() => {
  'use strict';
  const settings=window.TithikaSettings;
  if(!settings)return;
  const $=s=>document.querySelector(s);
  const $$=s=>[...document.querySelectorAll(s)];

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
    $('#tkSettingsLocationName').textContent=loc&&loc.city?loc.city:'No saved location';
    $('#tkSettingsLocationMeta').textContent=loc
      ? (loc.timezone+' · '+Number(loc.lat).toFixed(4)+', '+Number(loc.lon).toFixed(4))
      : 'Tithika will continue using geolocation or the standard fallback.';
  }

  $$('[data-setting] [data-value]').forEach(btn=>btn.addEventListener('click',()=>{
    const group=btn.closest('[data-setting]');
    if(!group)return;
    settings.set({[group.dataset.setting]:btn.dataset.value});
    render();
  }));

  $('#tkSaveCurrentLocation')?.addEventListener('click',()=>{
    const current=window.TithikaContext?.get?.();
    if(current && Number.isFinite(Number(current.lat)) && Number.isFinite(Number(current.lon))){
      settings.saveLocation(current);
      render();
      window.dispatchEvent(new CustomEvent('tithika:toast',{detail:'Default location saved on this device.'}));
    }
  });

  $('#tkClearSavedLocation')?.addEventListener('click',()=>{
    settings.clearLocation();
    render();
  });

  render();
})();