import React, { useContext } from 'react';

import { gettext } from '../../utils/gettext';
import Icon from '../Icon/Icon';
import { UrlsContext } from '../../contexts';

interface PageCountProps {
  page: {
    id: number;
    children: {
      count: number;
    };
  };
}

const PageCount: React.FunctionComponent<PageCountProps> = ({ page }) => {
  const urls = useContext(UrlsContext);
  const count = page.children.count;

  return (
    <a href={`${urls.pages}${page.id}/`} className="c-page-explorer__see-more">
      {gettext('See all')}
      <span>{` ${count} ${
        count === 1
          ? gettext('Page').toLowerCase()
          : gettext('Pages').toLowerCase()
      }`}</span>
      <Icon name="arrow-right" />
    </a>
  );
};

export default PageCount;
