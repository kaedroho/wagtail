import PropTypes from 'prop-types';
import React from 'react';
import { ADMIN_URLS, STRINGS } from '../../config/wagtailConfig';

import Button from '../../components/Button/Button';
import Icon from '../../components/Icon/Icon';


const SelectLocale = ({locale, translations, switchLocale}) => {
  const options = wagtailConfig.LOCALES.filter(({code}) => translations.get(code)).map(({code, display_name}) => {
    return <option value={code}>{display_name}</option>;
  });

  let onChange = (e) => {
    e.preventDefault();
    switchLocale(e.target.value);
  };

  let allOption = '';

  if (translations.get('*')) {
    allOption = <option value="*">All</option>;
  }

  return <select value={locale} onChange={onChange} disabled={options.length < 2}>{allOption}{options}</select>;
}

/**
 * The bar at the top of the explorer, displaying the current level
 * and allowing access back to the parent level.
 */
const ExplorerHeader = ({ page, depth, onClick, translations, locale, switchLocale }) => {
  const isRoot = depth === 1;

  return (
    <div className="c-explorer__header">
      <Button
        href={page.id ? `${ADMIN_URLS.PAGES}${page.id}/` : ADMIN_URLS.PAGES}
        className="c-explorer__header__title"
        onClick={onClick}
      >
        <div className="c-explorer__header__title__inner">
          <Icon
            name={isRoot ? 'home' : 'arrow-left'}
            className="icon--explorer-header"
          />
          <span>{page.admin_display_title || STRINGS.PAGES}</span>

          </div>
      </Button>
      {wagtailConfig.I18N_ENABLED && <SelectLocale locale={locale} translations={translations} switchLocale={switchLocale} />}
    </div>
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
