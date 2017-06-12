const defaultState = {
  isFetching: false,
  error: null,
  parent: null,
  items: [],
  totalItems: 0,
  pageTypes: {},
  viewName: 'browse',
  viewOptions: {
    parentPageID: 'root',
    pageNumber: 1,
  }
};

export default function pageChooser(state = defaultState, action) {
  switch (action.type) {
    case 'SET_VIEW':
      return Object.assign({}, state, {
        viewName: action.payload.viewName,
        viewOptions: action.payload.viewOptions,
      });

    case 'FETCH_START':
      return Object.assign({}, state, {
        isFetching: true,
        error: null,
      });

    case 'FETCH_SUCCESS':
      return Object.assign({}, state, {
        isFetching: false,
        parent: action.payload.parentJson,
        items: action.payload.itemsJson.items,
        totalItems: action.payload.itemsJson.meta.total_count,
        pageTypes: Object.assign({}, state.pageTypes, action.payload.itemsJson.__types),
      });

    case 'FETCH_FAILURE':
      return Object.assign({}, state, {
        isFetching: false,
        error: action.payload.message,
        items: [],
        totalItems: 0,
      });

    default:
      return state;
  }
}
