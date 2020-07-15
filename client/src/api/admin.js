import { get } from '../api/client';

import { ADMIN_API } from '../config/wagtailConfig';


export const getPage = (id) => {
  const url = `${ADMIN_API.PAGES}${id}/`;

  return get(url);
};

export const getPageChildren = (id, options = {}) => {
  let locale = null;

  if (typeof id == 'string') {
    [id, locale] = id.split('-');
  }

  let url = `${ADMIN_API.PAGES}?child_of=${id}&for_explorer=1`;

  if (wagtailConfig.I18N_ENABLED && locale) {
    url += `&locale=${locale}`;
  }

  if (options.fields) {
    url += `&fields=translations,${global.encodeURIComponent(options.fields.join(','))}`;
  } else {
    url += `&fields=translations`;
  }

  if (options.onlyWithChildren) {
    url += '&has_children=1';
  }

  if (options.offset) {
    url += `&offset=${options.offset}`;
  }

  url += ADMIN_API.EXTRA_CHILDREN_PARAMETERS;

  console.log(url);

  return get(url);
};

export const getPageTranslations = (id, options = {}) => {
  // TODO: increase max limit for admin API
  let url = `${ADMIN_API.PAGES}?translation_of=${id}&limit=20`;

  if (options.fields) {
    url += `&fields=${global.encodeURIComponent(options.fields.join(','))}`;
  }

  if (options.onlyWithChildren) {
    url += '&has_children=1';
  }

  return get(url);
};
