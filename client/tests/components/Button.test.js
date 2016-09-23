import React from 'react';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import '../stubs';

import Button from '../../src/components/Button/Button';

describe('Button', () => {
  it('exists', () => {
    expect(Button).to.be.a('function');
  });

  it('renders without exploding', () => {
    expect(shallow(<Button />)).to.have.length(1);
  });

  it('has as a label', () => {
    expect(shallow(
      <Button>
        To infinity and beyond!
      </Button>
    ).text()).to.contain('To infinity and beyond!');
  });

  it('has a visually hidden label when provided accessibleLabel', () => {
    expect(shallow(
      <Button accessibleLabel="I am here in the shadows" />
    ).html()).to.contain('visuallyhidden');
  });

  it('has icons', () => {
    expect(shallow(
      <Button icon="test-icon" />
    ).html()).to.contain('test-icon');
  });

  it('changes icon when loading', () => {
    expect(shallow(
      <Button icon="test-icon" isLoading={true} />
    ).html()).to.contain('spinner');
  });

  it('is clickable', (done) => {
    shallow(<Button onClick={() => done()} />).simulate('click', {
      preventDefault() {},
      stopPropagation() {},
    });
  });
});
