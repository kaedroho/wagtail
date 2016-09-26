import { expect } from 'chai';
import '../stubs';

import { Explorer, LoadingIndicator } from '../../src/index';

describe('wagtail package API', () => {
  describe('Explorer', () => {
    it('exists', () => {
      expect(Explorer).to.be.a('function');
    });
  });

  describe('LoadingIndicator', () => {
    it('exists', () => {
      expect(LoadingIndicator).to.be.a('function');
    });
  });
});
