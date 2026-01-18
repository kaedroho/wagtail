import client from './client';

import { AdminApiConfig } from '../contexts';

export interface WagtailPageAPI {
  id: number;
  meta: {
    status: {
      status: string;
      live: boolean;

      has_unpublished_changes: boolean;
    };
    children: any;
    parent: {
      id: number;
    } | null;
    locale?: string;
    translations?: any;
  };

  admin_display_title?: string;
}

interface WagtailPageListAPI {
  meta: {
    total_count: number;
  };
  items: WagtailPageAPI[];
}

export const getPage: (
  adminApi: AdminApiConfig,
  id: number,
) => Promise<WagtailPageAPI> = (adminApi, id) => {
  const url = `${adminApi.pagesBaseUrl}${id}/`;

  return client.get(url);
};

interface GetPageChildrenOptions {
  fields?: string[];
  onlyWithChildren?: boolean;
  offset?: number;
}

type GetPageChildren = (
  adminApi: AdminApiConfig,
  id: number,
  options: GetPageChildrenOptions,
) => Promise<WagtailPageListAPI>;
export const getPageChildren: GetPageChildren = (
  adminApi,
  id,
  options = {},
) => {
  let url = `${adminApi.pagesBaseUrl}?child_of=${id}&for_explorer=1`;

  if (options.fields) {
    url += `&fields=parent,${window.encodeURIComponent(
      options.fields.join(','),
    )}`;
  } else {
    url += '&fields=parent';
  }

  if (options.onlyWithChildren) {
    url += '&has_children=1';
  }

  if (options.offset) {
    url += `&offset=${options.offset}`;
  }

  url += adminApi.extraChildrenParameters;

  return client.get(url);
};

interface GetPageTranslationsOptions {
  fields?: string[];
  onlyWithChildren?: boolean;
  offset?: number;
}
type GetPageTranslations = (
  adminApi: AdminApiConfig,
  id: number,
  options: GetPageTranslationsOptions,
) => Promise<WagtailPageListAPI>;
export const getPageTranslations: GetPageTranslations = (
  adminApi,
  id,
  options = {},
) => {
  let url = `${adminApi.pagesBaseUrl}?translation_of=${id}&limit=20`;

  if (options.fields) {
    url += `&fields=parent,${global.encodeURIComponent(
      options.fields.join(','),
    )}`;
  } else {
    url += '&fields=parent';
  }

  if (options.onlyWithChildren) {
    url += '&has_children=1';
  }

  if (options.offset) {
    url += `&offset=${options.offset}`;
  }

  return client.get(url);
};

interface GetAllPageTranslationsOptions {
  fields?: string[];
  onlyWithChildren?: boolean;
}

export const getAllPageTranslations = async (
  adminApi: AdminApiConfig,
  id: number,
  options: GetAllPageTranslationsOptions,
) => {
  const items: WagtailPageAPI[] = [];
  let iterLimit = 100;

  for (;;) {
    // eslint-disable-next-line no-await-in-loop
    const page = await getPageTranslations(adminApi, id, {
      offset: items.length,
      ...options,
    });

    page.items.forEach((item) => items.push(item));

    // eslint-disable-next-line no-plusplus
    if (items.length >= page.meta.total_count || iterLimit-- <= 0) {
      return items;
    }
  }
};
