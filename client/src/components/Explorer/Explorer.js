import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import * as actions from './actions';

import ExplorerPanel from './ExplorerPanel';

const Explorer = ({
  isVisible,
  locale,
  nodes,
  path,
  pushPage,
  popPage,
  onClose,
  switchLocale,
}) => {
  console.log(locale, path);
  console.log(nodes)

  if (!path.length || !locale) {
    return null;
  }
  const translations = path[path.length - 1];
  const page = nodes[translations.get(locale)];


  return isVisible ? (
    <ExplorerPanel
      path={path}
      locale={locale}
      page={page}
      translations={translations}
      nodes={nodes}
      onClose={onClose}
      switchLocale={switchLocale}
      popPage={popPage}
      pushPage={pushPage}
    />
  ) : null;
};

Explorer.propTypes = {
  isVisible: PropTypes.bool.isRequired,
  path: PropTypes.array.isRequired,
  nodes: PropTypes.object.isRequired,

  pushPage: PropTypes.func.isRequired,
  popPage: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => ({
  isVisible: state.explorer.isVisible,
  locale: state.explorer.locale,
  path: state.explorer.path,
  nodes: state.nodes,
});

const mapDispatchToProps = (dispatch) => ({
  pushPage: (id) => dispatch(actions.pushPage(id)),
  popPage: () => dispatch(actions.popPage()),
  onClose: () => dispatch(actions.closeExplorer()),
  switchLocale: (locale) => dispatch(actions.switchLocale(locale)),
});

export default connect(mapStateToProps, mapDispatchToProps)(Explorer);
