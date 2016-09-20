import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware } from 'redux';
import createLogger from 'redux-logger';
import thunkMiddleware from 'redux-thunk';

import Explorer from 'components/explorer/Explorer';
import ExplorerToggle from 'components/explorer/toggle';
import rootReducer from 'components/explorer/reducers';

document.addEventListener('DOMContentLoaded', () => {
  const explorerNode = document.querySelector('#explorer');
  const toggleNode = document.querySelector('[data-explorer-menu-url]');

  const loggerMiddleware = createLogger();

  const store = createStore(
    rootReducer,
    applyMiddleware(loggerMiddleware, thunkMiddleware)
  );

  const toggle = (
    <Provider store={store}>
      <ExplorerToggle label={toggleNode.innerText} />
    </Provider>
  );

  const explorer = (
    <Provider store={store}>
      <Explorer
        type="sidebar"
        top={0}
        left={toggleNode.getBoundingClientRect().right}
        defaultPage={1}
      />
    </Provider>
  );

  ReactDOM.render(toggle, toggleNode.parentNode);
  ReactDOM.render(explorer, explorerNode);
});
