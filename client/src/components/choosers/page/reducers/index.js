import _ from 'lodash';


const defaultState = {
    isFetching: false,
    pages: [],
    pageTypes: {},
    viewName: null,
    viewOptions: {}
};


export default function pageChooser(state = defaultState, action) {
    switch (action.type) {
        case 'SET_VIEW':
            return _.assign({}, state, {
                pages: [],
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
                pageTypes: _.assign({}, state.pageTypes, action.payload.json.__types),
            });

        default:
            return state;
    }
}
