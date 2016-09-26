import React from 'react';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import '../stubs';

import ExplorerItem from '../../src/components/explorer/ExplorerItem';

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
