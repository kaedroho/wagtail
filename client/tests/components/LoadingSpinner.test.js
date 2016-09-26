import React from 'react';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import '../stubs';

import LoadingSpinner from '../../src/components/explorer/LoadingSpinner';

describe('LoadingSpinner', () => {
  it('exists', () => {
    expect(LoadingSpinner).to.be.a('function');
  });

  it('renders without exploding', () => {
    expect(shallow(<LoadingSpinner />)).to.have.length(1);
  });
});
