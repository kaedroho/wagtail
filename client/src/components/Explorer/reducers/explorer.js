const defaultState = {
  isVisible: false,
  locale: wagtailConfig.ACTIVE_LOCALE,
  path: [],
};

/**
 * Oversees the state of the explorer. Defines:
 * - Where in the page tree the explorer is at.
 * - Whether the explorer is open or not.
 */
export default function explorer(prevState = defaultState, { type, payload }) {
  console.log(type, payload);
  switch (type) {
  case 'OPEN_EXPLORER': {
    // Build object containing IDs of the page in all locales
    let pageIds = new Map();
    let locale;

    if (payload.id == 1) {
      locale = '*';
      // Let root be accessible in all locales
      // The root page is a special case because it contains pages in multiple languages.
      // So to allow us to represent multiple sets of children for this page, we make up
      // a bunch of different ids. The regular ID will return all children where as a made
      // up ID with the locale (eg 1-en) will return pages with a single language.
      // These IDs are set as translations to allow the language switcher to work.
      pageIds.set('*', payload.id);
      wagtailConfig.LOCALES.map(({code}) => {
        pageIds.set(code, `${payload.id}-${code}`);
      });
    } else {
      locale = payload.locale;
      pageIds.set(payload.locale, payload.id);
    }

    // Provide a starting page when opening the explorer.
    return {
      isVisible: true,
      locale: locale,
      path: [pageIds],
    };
  }
  case 'CLOSE_EXPLORER':
    return defaultState;

  case 'PUSH_PAGE': {
    // Build object containing IDs of the page in all locales
    let pageIds = new Map();
    pageIds.set(prevState.locale, payload.id);
    payload.translations.forEach(({id, meta: {locale}}) => {
      pageIds.set(locale, id);
    });

    return {
      isVisible: prevState.isVisible,
      locale: prevState.locale,
      path: prevState.path.concat([pageIds]),
    };
  }
  case 'POP_PAGE':
    return {
      isVisible: prevState.isVisible,
      locale: prevState.locale,
      path: prevState.path.slice(0, -1),
    };

  case 'SWITCH_LOCALE':
    return {
      isVisible: prevState.isVisible,
      locale: payload.locale,
      path: prevState.path,
    };

  default:
    return prevState;
  }
}
