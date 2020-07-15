const defaultPageState = {
  isFetchingChildren: false,
  isFetchingTranslations: false,
  isError: false,
  children: {
    items: [],
    count: 0,
  },
  translations: {
    items: [],
    count: 0,
  },
  meta: {
    children: {},
  },
};

/**
 * A single page node in the explorer.
 */
const node = (state = defaultPageState, { type, payload }) => {
  switch (type) {
  case 'OPEN_EXPLORER':
    return state || defaultPageState;

  case 'GET_PAGE_SUCCESS':
    return Object.assign({}, state, payload.data, {
      isError: false,
    });

  case 'GET_CHILDREN_START':
    return Object.assign({}, state, {
      isFetchingChildren: true,
    });

  case 'GET_TRANSLATIONS_START':
    return Object.assign({}, state, {
      isFetchingTranslations: true,
    });

  case 'GET_CHILDREN_SUCCESS':
    return Object.assign({}, state, {
      isFetchingChildren: false,
      isError: false,
      children: {
        items: state.children.items.slice().concat(payload.items.map(item => item.id)),
        count: payload.meta.total_count,
      },
    });

  case 'GET_TRANSLATIONS_SUCCESS':
    return Object.assign({}, state, {
      isFetchingTranslations: false,
      isError: false,
      translations: {
        items: state.translations.items.slice().concat(payload.items.map(item => item.id)),
        count: payload.meta.total_count,
      },
    });

  case 'GET_PAGE_FAILURE':
  case 'GET_CHILDREN_FAILURE':
  case 'GET_TRANSLATIONS_FAILURE':
    return Object.assign({}, state, {
      isFetchingChildren: false,
      isFetchingTranslations: false,
      isError: true,
    });

  default:
    return state;
  }
};

const defaultState = {};

/**
 * Contains all of the page nodes in one object.
 */
export default function nodes(state = defaultState, { type, payload }) {
  switch (type) {
  case 'OPEN_EXPLORER':
  case 'GET_PAGE_SUCCESS':
  case 'GET_CHILDREN_START':
  case 'GET_TRANSLATIONS_START':
  case 'GET_PAGE_FAILURE':
  case 'GET_CHILDREN_FAILURE':
  case 'GET_TRANSLATIONS_FAILURE':
    if (payload.id == 1 && type == 'OPEN_EXPLORER') {
      state = Object.assign({}, state, {
        // Delegate logic to single-node reducer.
        [payload.id]: node(state[payload.id], { type, payload }),
      });

      wagtailConfig.LOCALES.map(({code}) => {
        state = Object.assign({}, state, {
          // Delegate logic to single-node reducer.
          [`${payload.id}-${code}`]: node(state[`${payload.id}-${code}`], { type, payload }),
        });
      });

      return state;
    } else {
      return Object.assign({}, state, {
        // Delegate logic to single-node reducer.
        [payload.id]: node(state[payload.id], { type, payload }),
      });
    }

  // eslint-disable-next-line no-case-declarations
  case 'GET_CHILDREN_SUCCESS':
  case 'GET_TRANSLATIONS_SUCCESS':
    const newState = Object.assign({}, state, {
      [payload.id]: node(state[payload.id], { type, payload }),
    });

    payload.items.forEach((item) => {
      newState[item.id] = Object.assign({}, defaultPageState, item);
    });

    return newState;

  default:
    return state;
  }
}
