import _ from 'lodash';


const defaultState = {
    isFetching: false,
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
            return _.assign({}, state, {
                items: [],
                totalItems: 0,
                viewName: action.payload.viewName,
                viewOptions: action.payload.viewOptions,
            });

        case 'FETCH_START':
            return _.assign({}, state, {
                isFetching: true,
            });

        case 'FETCH_SUCCESS':
            return _.assign({}, state, {
                isFetching: false,
                items: action.payload.json.items,
                totalItems: action.payload.json.meta.total_count,
                pageTypes: _.assign({}, state.pageTypes, action.payload.json.__types),
            });

        default:
            return state;
    }
}
