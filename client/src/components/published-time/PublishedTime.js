import React from 'react';
import moment from 'moment';

import { STRINGS } from '../../config';

// TODO Should be a format function not a React component?
const PublishedTime = ({ publishedAt }) => {
  const date = moment(publishedAt);
  const str = publishedAt ?  date.format('DD.MM.YYYY') : STRINGS.NO_DATE;

  return (
    <span>{str}</span>
  );
};

PublishedTime.propTypes = {
  publishedAt: React.PropTypes.string,
};

export default PublishedTime;
