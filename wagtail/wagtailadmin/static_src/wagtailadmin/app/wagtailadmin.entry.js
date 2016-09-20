import 'babel-polyfill';

import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware, compose } from 'redux';
import createLogger from 'redux-logger';
import thunkMiddleware from 'redux-thunk';

import Explorer from 'components/explorer/Explorer';
import ExplorerToggle from 'components/explorer/toggle';
import rootReducer from 'components/explorer/reducers';

/**
 * Admin JS entry point. Add in here code to run once the page is loaded.
 */
document.addEventListener('DOMContentLoaded', () => {
  const explorerNode = document.querySelector('#explorer');
  const toggleNode = document.querySelector('[data-explorer-menu-url]');

  const middleware = [
    // TODO Get rid of redux-logger, solely use the Chrome DevTools extension?
    createLogger(),
    thunkMiddleware,
  ];

  const store = createStore(rootReducer, {}, compose(
    applyMiddleware(...middleware),
    // Expose store to Redux DevTools extension.
    window.devToolsExtension ? window.devToolsExtension() : f => f
  ));

  const toggle = (
    <Provider store={store}>
      <ExplorerToggle label={toggleNode.innerText} />
    </Provider>
  );

  const explorer = (
    <Provider store={store}>
      <Explorer type="sidebar" defaultPage={1} />
    </Provider>
  );

  ReactDOM.render(toggle, toggleNode.parentNode);
  ReactDOM.render(explorer, explorerNode);
});
