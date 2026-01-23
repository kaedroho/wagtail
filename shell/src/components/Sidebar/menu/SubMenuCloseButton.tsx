import * as React from 'react';
import { createPortal } from 'react-dom';
import { styled } from '@linaria/react';

import Icon from '../../Icon/Icon';
import { gettext } from '../../../utils/gettext';
import { MenuAction } from '../modules/MainMenu';

const CloseButton = styled.button`
  display: grid;
  place-items: center;
  color: rgba(255, 255, 255, 0.8);
  padding: 0;
  z-index: 91; /* sidebar toggle z-index */
  border: 1px solid transparent;
  position: fixed;
  background-color: rgb(46, 31, 94);
  top: 0;
  left: 0;
  height: 50px;
  width: 50px;
  border-radius: 0;

  &:hover {
    background-color: rgba(0, 0, 0, 0.2);
    color: white;
  }

  /* Hide on desktop (sm breakpoint and up) */
  @media (min-width: 800px) {
    display: none;
  }

  svg {
    width: 15px;
    height: 1rem;
  }
`;

interface SubMenuCloseButtonProps {
  isVisible: boolean;
  dispatch(action: MenuAction): void;
}

export default function SubMenuCloseButton({
  isVisible,
  dispatch,
}: SubMenuCloseButtonProps) {
  if (!isVisible) {
    return null;
  }
  return createPortal(
    <CloseButton
      type="button"
      onClick={() =>
        dispatch({
          type: 'set-navigation-path',
          path: '',
        })
      }
      aria-label={gettext('Close')}
    >
      <Icon name="cross" />
    </CloseButton>,
    document.body,
  );
}
