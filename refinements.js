(() => {
  'use strict';

  const ticker = document.querySelector('[data-deal-ticker]');
  const pause = ticker?.querySelector('.ticker-toggle');
  pause?.addEventListener('click', () => {
    const paused = ticker.classList.toggle('is-paused');
    pause.setAttribute('aria-pressed', String(paused));
    pause.setAttribute('aria-label', paused ? 'Play deal ticker' : 'Pause deal ticker');
    pause.textContent = paused ? 'Play' : 'Pause';
  });

  const filters = document.querySelector('[data-filter-controls]');
  if (filters) {
    const buttons = [...filters.querySelectorAll('[data-filter]')];
    const cards = [...document.querySelectorAll('[data-category]')];
    const count = filters.querySelector('[data-filter-count]');
    filters.hidden = false;
    buttons.forEach(button => button.addEventListener('click', () => {
      const category = button.dataset.filter;
      buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      cards.forEach(card => { card.hidden = category !== 'all' && card.dataset.category !== category; });
      const visible = cards.filter(card => !card.hidden).length;
      count.textContent = `${visible} financing ${visible === 1 ? 'option' : 'options'}`;
    }));
  }

  const stageNav = document.querySelector('.stage-nav');
  if (stageNav) {
    const buttons = [...stageNav.querySelectorAll('[data-stage-button]')];
    const panels = [...document.querySelectorAll('[data-stage-panel]')];
    const nextButtons = [...document.querySelectorAll('[data-stage-next]')];
    const activate = (stage, focusHeading = false) => {
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.stageButton === stage)));
      panels.forEach(panel => { panel.hidden = panel.dataset.stagePanel !== stage; });
      if (focusHeading) {
        const heading = panels.find(panel => !panel.hidden)?.querySelector('h2');
        if (heading) { heading.tabIndex = -1; heading.focus({ preventScroll: true }); }
      }
    };
    stageNav.hidden = false;
    stageNav.closest('.process-layout').classList.add('is-interactive');
    nextButtons.forEach(button => {
      button.hidden = false;
      button.addEventListener('click', () => activate(button.dataset.stageNext, true));
    });
    buttons.forEach(button => button.addEventListener('click', () => activate(button.dataset.stageButton)));
    activate('1');
  }
})();
