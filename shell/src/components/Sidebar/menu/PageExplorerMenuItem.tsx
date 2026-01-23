import * as React from 'react';
import { styled } from '@linaria/react';

import { Provider } from 'react-redux';
import Tippy from '@tippyjs/react';
import Icon from '../../Icon/Icon';
import { MenuItemProps } from './MenuItem';
import { LinkMenuItemDefinition } from './LinkMenuItem';
import PageExplorer, { initPageExplorerStore } from '../../PageExplorer';
import {
  openPageExplorer,
  closePageExplorer,
} from '../../PageExplorer/actions';
import SidebarPanel from '../SidebarPanel';
import { SIDEBAR_TRANSITION_DURATION } from '../Sidebar';
import { MenuItemWrapper, MenuItemButton, MenuItemLabel } from './MenuItem';
import SubMenuCloseButton from './SubMenuCloseButton';

interface PageExplorerItemWrapperProps {
  isActive: boolean;
  isInSubMenu: boolean;
  slim: boolean;
  isOpen: boolean;
}

const PageExplorerItemWrapper = styled(
  MenuItemWrapper,
)<PageExplorerItemWrapperProps>`
  ${(props) =>
    props.isOpen
      ? `
    border-inline-start: 2px solid #00b0b1;

    > button {
      text-shadow: -1px -1px 0 rgba(0, 0, 0, 0.35);
    }
  `
      : ''}
`;

interface TriggerIconProps {
  isOpen: boolean;
  slim: boolean;
}

const TriggerIcon = styled(Icon)<TriggerIconProps>`
  transition:
    transform var(--sidebar-transition-duration) ease-in-out,
    width var(--sidebar-transition-duration) ease-in-out,
    height var(--sidebar-transition-duration) ease-in-out;
  display: block;
  width: 1rem;
  height: 1rem;
  inset-inline-end: 15px;
  margin-inline-start: auto;

  ${(props) =>
    props.isOpen
      ? `
    transform-origin: 50% 50%;
    transform: rotate(180deg);
  `
      : ''}

  ${(props) =>
    props.slim
      ? `
    width: 1rem;
    height: 1rem;
    position: absolute;
    inset-inline-end: 0;
  `
      : ''}
`;

interface PageExplorerMenuItemProps
  extends MenuItemProps<PageExplorerMenuItemDefinition> {
  isMobile?: boolean;
}

export function PageExplorerMenuItem({
  path,
  slim,
  item,
  state,
  dispatch,
  navigate,
  isMobile = false,
}: PageExplorerMenuItemProps) {
  const isOpen = state.navigationPath.startsWith(path);
  const isActive = isOpen || state.activePath.startsWith(path);
  const depth = path.split('.').length;
  const isInSubMenu = path.split('.').length > 2;
  const [isVisible, setIsVisible] = React.useState(false);

  const store = React.useRef<any>(null);
  if (!store.current) {
    store.current = initPageExplorerStore();
  }

  const onCloseExplorer = () => {
    // When a submenu is closed, we have to wait for the close animation
    // to finish before making it invisible
    setTimeout(() => {
      setIsVisible(false);
      if (store.current) {
        store.current.dispatch(closePageExplorer());
      }
    }, SIDEBAR_TRANSITION_DURATION);
  };

  React.useEffect(() => {
    if (isOpen) {
      // isOpen is set at the moment the user clicks the menu item
      setIsVisible(true);

      if (store.current) {
        store.current.dispatch(openPageExplorer(item.startPageId));
      }
    } else if (!isOpen && isVisible) {
      onCloseExplorer();
    }
  }, [isOpen]);

  const onClick = () => {
    // Open/close explorer
    if (isOpen) {
      dispatch({
        type: 'set-navigation-path',
        path: '',
      });
    } else {
      dispatch({
        type: 'set-navigation-path',
        path,
      });
    }
  };

  return (
    <PageExplorerItemWrapper
      isActive={isActive}
      isInSubMenu={isInSubMenu}
      slim={slim}
      isOpen={isOpen}
    >
      <Tippy disabled={isOpen || !slim} content={item.label} placement="right">
        <MenuItemButton
          onClick={onClick}
          aria-haspopup="dialog"
          aria-expanded={isOpen ? 'true' : 'false'}
          type="button"
          isInSubMenu={isInSubMenu}
          slim={slim}
        >
          <Icon name="folder-open-inverse" className="icon--menuitem" />
          <MenuItemLabel slim={slim} isInSubMenu={isInSubMenu}>
            {item.label}
          </MenuItemLabel>
          <TriggerIcon name="arrow-right" isOpen={isOpen} slim={slim} />
        </MenuItemButton>
      </Tippy>
      <div>
        <SidebarPanel
          isVisible={isVisible}
          isOpen={isOpen}
          depth={depth}
          widthPx={485}
          slim={slim}
          isMobile={isMobile}
        >
          <SubMenuCloseButton isVisible={isVisible} dispatch={dispatch} />
          {store.current && (
            <Provider store={store.current}>
              <PageExplorer
                isVisible={isVisible}
                navigate={navigate}
                onClose={onCloseExplorer}
              />
            </Provider>
          )}
        </SidebarPanel>
      </div>
    </PageExplorerItemWrapper>
  );
}

export class PageExplorerMenuItemDefinition extends LinkMenuItemDefinition {
  startPageId: number;

  constructor(
    {
      name,
      label,
      url,
      attrs = {},
      icon_name: iconName = null as string | null,
      classname = undefined as string | undefined,
    },
    startPageId: number,
  ) {
    super({ name, label, url, attrs, icon_name: iconName, classname });
    this.startPageId = startPageId;
  }

  render({ path, slim, state, dispatch, navigate }) {
    return (
      <PageExplorerMenuItem
        key={this.name}
        item={this}
        path={path}
        slim={slim}
        state={state}
        dispatch={dispatch}
        navigate={navigate}
      />
    );
  }
}
