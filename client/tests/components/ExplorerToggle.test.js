import React from 'react';
import { createStore } from 'redux';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import '../stubs';

import ExplorerToggle from '../../src/components/explorer/ExplorerToggle';
import rootReducer from '../../src/components/explorer/reducers';

const store = createStore(rootReducer);

describe('ExplorerToggle', () => {
  it('exists', () => {
    expect(ExplorerToggle).to.be.a('function');
  });

  it('renders without exploding', () => {
    expect(shallow(
      <ExplorerToggle store={store} />
    )).to.have.length(1);
  });

  it('has the right icon', () => {
    expect(shallow(
      <ExplorerToggle store={store} />
    ).html()).to.contain('folder-open-inverse');
  });

  it('changes icon when loading', (done) => {
    store.subscribe(() => {
      expect(shallow(
        <ExplorerToggle store={store} />
      ).html()).to.contain('spinner');

      done();
    });

    store.dispatch({ type: 'FETCH_START' });
  });

  it('supports children', () => {
    expect(shallow(
      <ExplorerToggle store={store}>
        <span className="t-dark">
          To infinity and beyond!
        </span>
      </ExplorerToggle>
    ).childAt(0).text()).to.contain('To infinity and beyond!');
  });
});
