import React from 'react';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import '../stubs';

import ExplorerEmpty from '../../src/components/explorer/ExplorerEmpty';

describe('ExplorerEmpty', () => {
  it('exists', () => {
    expect(ExplorerEmpty).to.be.a('function');
  });

  it('renders without exploding', () => {
    expect(shallow(<ExplorerEmpty />)).to.have.length(1);
  });
});
