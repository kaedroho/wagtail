export const API = global.wagtailConfig.api;
export const API_PAGES = global.wagtailConfig.api.pages;

export const PAGES_ROOT_ID = 'root';

export const STRINGS = global.wagtailConfig.strings;

export const EXPLORER_ANIM_DURATION = 220;

export const ADMIN_PAGES = global.wagtailConfig.urls.pages;

// TODO Add back in when we want to support explorer that displays pages
// without children (API call without has_children=1).
export const EXPLORER_FILTERS = [
  // { id: 1, label: 'A', filter: null },
  // { id: 2, label: 'B', filter: 'has_children=1' }
];
