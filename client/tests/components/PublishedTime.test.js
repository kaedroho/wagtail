import React from 'react';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import '../stubs';

import PublishedTime from '../../src/components/published-time/PublishedTime';

describe('PublishedTime', () => {
  it('exists', () => {
    expect(PublishedTime).to.be.a('function');
  });

  it('renders without exploding', () => {
    expect(shallow(<PublishedTime />)).to.have.length(1);
  });

  it('has date as a label', () => {
    expect(shallow(<PublishedTime publishedAt="2016-09-19T20:22:33.356623Z" />).childAt(0).text()).to.contain('19.09.2016');
  });

  it('has "no date" label when no date is provided', () => {
    expect(shallow(<PublishedTime />).childAt(0).text()).to.contain('No date');
  });
});
