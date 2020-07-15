import PropTypes from 'prop-types';
import React from 'react';
import { ADMIN_URLS, STRINGS } from '../../config/wagtailConfig';

import Button from '../../components/Button/Button';
import Icon from '../../components/Icon/Icon';


const SelectLocale = ({initial, switchLocale}) => {
  const options = wagtailConfig.LOCALES.map(({code, display_name}) => {
    return <option value={code}>{display_name}</option>;
  });

  let onChange = (e) => {
    e.preventDefault();
    switchLocale(e.target.value)
  };

  return <select value={initial} onChange={onChange}>{options}</select>;
}

/**
 * The bar at the top of the explorer, displaying the current level
 * and allowing access back to the parent level.
 */
const ExplorerHeader = ({ page, depth, onClick, switchLocale }) => {
  const isRoot = depth === 1;

  return (
    <Button
      className="c-explorer__header"
    >
      <div className="c-explorer__header__inner">
        <Icon
          name={isRoot ? 'home' : 'arrow-left'}
          className="icon--explorer-header"
        />
        <span>{page.admin_display_title || STRINGS.PAGES}</span>
        <SelectLocale initial={page.meta.locale || wagtailConfig.ACTIVE_LOCALE} switchLocale={switchLocale} />
      </div>
    </Button>
  );
};

ExplorerHeader.propTypes = {
  page: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    admin_display_title: PropTypes.string,
  }).isRequired,
  depth: PropTypes.number.isRequired,
  onClick: PropTypes.func.isRequired,
};

export default ExplorerHeader;
