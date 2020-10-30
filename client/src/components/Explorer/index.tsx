import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, combineReducers, applyMiddleware, compose } from 'redux';
import thunkMiddleware, {ThunkDispatch} from 'redux-thunk';

// import { perfMiddleware } from '../../utils/performance';
import Explorer from './Explorer';
import explorer from './reducers/explorer';
import nodes from './reducers/nodes';
import * as actions from './actions';
import { Action, State } from './reducers';

/**
 * Initialises the explorer component on the given nodes.
 */
const initExplorer = (explorerNode, navigate) => {
  const rootReducer = combineReducers({
    explorer,
    nodes,
  });

  const middleware = [
    thunkMiddleware,
  ];

  // Uncomment this to use performance measurements.
  // if (process.env.NODE_ENV !== 'production') {
  //   middleware.push(perfMiddleware);
  // }

  const store = createStore(rootReducer, {}, compose(
    applyMiddleware(...middleware),
    // Expose store to Redux DevTools extension.
    window.__REDUX_DEVTOOLS_EXTENSION__ ? window.__REDUX_DEVTOOLS_EXTENSION__() : func => func
  ));

  ReactDOM.render((
    <Provider store={store}>
      <Explorer navigate={navigate} />
    </Provider>
  ), explorerNode);

  const dispatch = store.dispatch as ThunkDispatch<State, unknown, Action>;
  return (page: number) => { dispatch(actions.toggleExplorer(page)); }
};

export default Explorer;

export {
  initExplorer,
};
