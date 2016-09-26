import React from 'react';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import '../stubs';

import LoadingIndicator from '../../src/components/loading-indicator/LoadingIndicator';

describe('LoadingIndicator', () => {
  it('exists', () => {
    expect(LoadingIndicator).to.be.a('function');
  });

  it('renders without exploding', () => {
    expect(shallow(<LoadingIndicator />)).to.have.length(1);
  });
});
