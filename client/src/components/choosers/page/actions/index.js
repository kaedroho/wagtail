import { createAction } from 'redux-actions';

import { API_PAGES, PAGES_ROOT_ID } from '../../../../config';


function getHeaders() {
    const headers = new Headers();
    headers.append('Content-Type', 'application/json');

    return {
        credentials: 'same-origin',
        headers: headers,
        method: 'GET'
    };
}

function get(url) {
    return fetch(url, getHeaders()).then(response => response.json());
}


export const setView = createAction('SET_VIEW', (viewName, viewOptions) => ({ viewName, viewOptions }));

export const fetchPagesStart = createAction('FETCH_START');
export const fetchPagesSuccess = createAction('FETCH_SUCCESS', (json) => ({ json }));


export function browse(parentPageID, pageNumber) {
    return (dispatch, getState) => {
        dispatch(setView('browse', { parentPageID, pageNumber }));
        dispatch(fetchPagesStart());

        let limit = 20;
        let offset = (pageNumber - 1) * limit;
        let url = `${API_PAGES}?child_of=${parentPageID}&fields=parent&limit=${limit}&offset=${offset}`;

        return get(url)
          .then(json => dispatch(fetchPagesSuccess(json)));
    };

    dispatch
}


export function search(queryString, pageNumber) {
    return (dispatch, getState) => {
        dispatch(setView('search', { queryString, pageNumber }));
        dispatch(fetchPagesStart());

        let limit = 20;
        let offset = (pageNumber - 1) * limit;
        let url = `${API_PAGES}?fields=parent&search=${queryString}&limit=${limit}&offset=${offset}`;

        return get(url)
          .then(json => dispatch(fetchPagesSuccess(json)));
    };

    dispatch
}
