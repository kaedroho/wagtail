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
export const fetchPagesSuccess = createAction('FETCH_SUCCESS', (itemsJson, parentJson) => ({ itemsJson, parentJson }));


export function browse(parentPageID, pageNumber) {
  // HACK: Assuming page 1 is the root page
  if (parentPageID == 1) { parentPageID = 'root'; }

  return (dispatch, getState) => {
    dispatch(setView('browse', { parentPageID, pageNumber }));
    dispatch(fetchPagesStart());

    let limit = 20;
    let offset = (pageNumber - 1) * limit;
    let itemsUrl = `${API_PAGES}?child_of=${parentPageID}&fields=parent,children&limit=${limit}&offset=${offset}`;
    let parentUrl = `${API_PAGES}${parentPageID}/?fields=ancestors`;

    // HACK: The admin API currently doesn't serve the root page
    if (parentPageID == 'root') {
       return get(itemsUrl)
         .then(itemsJson => dispatch(fetchPagesSuccess(itemsJson, null)));
    }

    return Promise.all([get(itemsUrl), get(parentUrl)])
      .then(([itemsJson, parentJson]) => dispatch(fetchPagesSuccess(itemsJson, parentJson)));
  };

  dispatch
}


export function search(queryString, restrictPageTypes, pageNumber) {
  return (dispatch, getState) => {
    dispatch(setView('search', { queryString, pageNumber }));
    dispatch(fetchPagesStart());

    let limit = 20;
    let offset = (pageNumber - 1) * limit;
    let url = `${API_PAGES}?fields=parent&search=${queryString}&limit=${limit}&offset=${offset}`;

    console.log(restrictPageTypes)

    if (restrictPageTypes != null) {
      url += '&type=' + restrictPageTypes.join(',');
    }

    return get(url)
      .then(json => dispatch(fetchPagesSuccess(json, null)));
  };

  dispatch
}
