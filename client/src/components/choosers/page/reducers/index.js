import _ from 'lodash';


const defaultState = {
    isFetching: false,
    pages: [],
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
            return _.assign({}, state, {
                pages: [],
                totalItems: 0,
                viewName: action.payload.viewName,
                viewOptions: action.payload.viewOptions,
            });

        case 'FETCH_PAGES_START':
            return _.assign({}, state, {
                isFetching: true,
            });

        case 'FETCH_PAGES_SUCCESS':
            return _.assign({}, state, {
                isFetching: false,
                pages: action.payload.json.items,
                totalItems: action.payload.json.meta.total_count,
                pageTypes: _.assign({}, state.pageTypes, action.payload.json.__types),
            });

        default:
            return state;
    }
}
