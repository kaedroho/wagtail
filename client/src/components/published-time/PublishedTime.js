import React from 'react';
import moment from 'moment';

// TODO Should be a format function not a React component?
const PublishedTime = ({ publishedAt }) => {
  const date = moment(publishedAt);
  const str = publishedAt ?  date.format('DD.MM.YYYY') : 'No date';

  return (
    <span>{str}</span>
  );
};

PublishedTime.propTypes = {
  publishedAt: React.PropTypes.string,
};

export default PublishedTime;
