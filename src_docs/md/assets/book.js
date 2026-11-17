// this_file: src_docs/md/assets/book.js
(() => {
  // MaterialX 10.1.8 observes keyup; paste, autofill and assistive input need input.
  document.querySelector('[data-md-component="search-query"]')?.addEventListener('input', event => {
    event.target.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
  });
  const repairLandmarks = () => {
    document.querySelector('.md-search[role="dialog"]')?.setAttribute('aria-label', 'Search');
    document.querySelectorAll('.md-option[aria-hidden="true"]').forEach(input => {
      input.tabIndex = -1;
    });
    document.querySelectorAll('nav.md-code__nav').forEach((nav, index) => {
      nav.setAttribute('aria-label', `Code block ${index + 1} controls`);
    });
  };
  repairLandmarks();
  // Copy controls are inserted after the theme bundle starts.
  if (typeof document$ !== 'undefined') document$.subscribe(repairLandmarks);
})();
