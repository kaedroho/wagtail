import React from 'react';

const PublishStatus = ({ status }) => (status ? (
  <span className={`o-pill c-status${status.live ? ' c-status--live' : ''}`}>
    {status.status}
  </span>
) : null);

PublishStatus.propTypes = {
  status: React.PropTypes.object,
};

export default PublishStatus;
