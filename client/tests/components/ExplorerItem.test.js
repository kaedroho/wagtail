import React from 'react';
import { createStore } from 'redux';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import '../stubs';

import ExplorerItem from '../../src/components/explorer/ExplorerItem';
import rootReducer from '../../src/components/explorer/reducers';

const store = createStore(rootReducer);

describe('ExplorerItem', () => {
  it('exists', () => {
    expect(ExplorerItem).to.be.a('function');
  });

  it('renders without exploding', () => {
    expect(shallow(
      <ExplorerItem />
    )).to.have.length(1);
  });
});
