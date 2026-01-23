import React from 'react';
import { styled } from '@linaria/react';

interface StatusPillProps {
  live: boolean;
}

const StatusPill = styled.span<StatusPillProps>`
  display: inline-block;
  padding: 0.2em 0.5em;
  border-radius: 0.25em;
  vertical-align: middle;
  line-height: 1.5;
  text-transform: uppercase;
  font-size: 0.625rem;
  letter-spacing: -0.025em;
  background-color: rgba(0, 0, 0, 0.5);
  color: var(--w-color-text-label-menus-default, rgba(255, 255, 255, 0.8));
`;

interface PublicationStatusProps {
  status: {
    live: boolean;
    status: string;
  };
}

/**
 * Displays the publication status of a page in a pill.
 */
export default function PublicationStatus({ status }: PublicationStatusProps) {
  return <StatusPill live={status.live}>{status.status}</StatusPill>;
}
