import * as React from 'react';
import { styled } from '@linaria/react';

import Tippy from '@tippyjs/react';
import { gettext } from '../../../utils/gettext';
import Icon from '../../Icon/Icon';

import { LinkMenuItemDefinition } from '../menu/LinkMenuItem';
import { MenuItemDefinition } from '../menu/MenuItem';
import { SubMenuItemDefinition } from '../menu/SubMenuItem';
import { ModuleDefinition } from '../Sidebar';

export function renderMenu(
  path: string,
  items: MenuItemDefinition[],
  slim: boolean,
  state: MenuState,
  dispatch: (action: MenuAction) => void,
  navigate: (url: string) => Promise<void>,
) {
  return (
    <>
      {items.map((item) =>
        item.render({
          path: `${path}.${item.name}`,
          slim,
          state,
          dispatch,
          navigate,
        }),
      )}
    </>
  );
}

export function isDismissed(item: MenuItemDefinition, state: MenuState) {
  return (
    // Non-dismissibles are considered as dismissed
    !item.attrs['data-w-dismissible-id-value'] ||
    // Dismissed on the server
    'data-w-dismissible-dismissed-value' in item.attrs ||
    // Dismissed on the client
    state.dismissibles[item.name]
  );
}

interface SetActivePath {
  type: 'set-active-path';
  path: string;
}

interface SetNavigationPath {
  type: 'set-navigation-path';
  path: string;
}

interface SetDismissibleState {
  type: 'set-dismissible-state';
  item: MenuItemDefinition;
  value?: boolean;
}

export type MenuAction =
  | SetActivePath
  | SetNavigationPath
  | SetDismissibleState;

export interface MenuState {
  navigationPath: string;
  activePath: string;
  dismissibles: Record<string, boolean>;
}

function walkDismissibleMenuItems(
  menuItems: MenuItemDefinition[],
  action: (item: MenuItemDefinition) => void,
) {
  menuItems.forEach((menuItem) => {
    const id = menuItem.attrs['data-w-dismissible-id-value'];
    if (id) {
      action(menuItem);
    }

    if (menuItem instanceof SubMenuItemDefinition) {
      walkDismissibleMenuItems(menuItem.menuItems, action);
    }
  });
}

function computeDismissibleState(
  state: MenuState,
  { item, value = true }: SetDismissibleState,
) {
  const update: Record<string, boolean> = {};

  // Recursively update all dismissible items
  walkDismissibleMenuItems([item], (menuItem) => {
    update[menuItem.attrs['data-w-dismissible-id-value']] = value;
  });

  // Send the update to the server
  if (Object.keys(update).length > 0) {
    // updateDismissibles(update);
  }

  // Only update the top-level item in the client state so that the submenus
  // are not immediately dismissed until the next page load
  return { ...state.dismissibles, [item.name]: value };
}

function menuReducer(state: MenuState, action: MenuAction) {
  const newState = { ...state };

  switch (action.type) {
    case 'set-active-path':
      newState.activePath = action.path;
      break;
    case 'set-navigation-path':
      newState.navigationPath = action.path;
      break;
    case 'set-dismissible-state':
      newState.dismissibles = computeDismissibleState(state, action);
      break;
    default:
      break;
  }

  return newState;
}

function getInitialDismissibleState(menuItems: MenuItemDefinition[]) {
  const result: Record<string, boolean> = {};

  walkDismissibleMenuItems(menuItems, (menuItem) => {
    result[menuItem.attrs['data-w-dismissible-id-value']] =
      'data-w-dismissible-dismissed-value' in menuItem.attrs;
  });

  return result;
}

// Styled components

interface MainMenuNavProps {
  accountSettingsOpen: boolean;
}

const MainMenuNav = styled.nav<MainMenuNavProps>`
  overflow: auto;
  overflow-x: hidden;

  /* Thin scrollbar */
  scrollbar-width: thin;
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.3);
    border-radius: 3px;
  }

  *:focus {
    outline: 2px solid var(--w-color-focus, #00b0b1);
    outline-offset: -2px;
  }

  .icon--submenu-header {
    display: block;
    width: 4rem;
    height: 4rem;
    margin: 0 auto 0.8em;
    opacity: 0.15;
  }

  > ul > li > a {
    transition: padding var(--sidebar-transition-duration) ease-in-out !important;
  }

  .menuitem-label {
    transition: opacity var(--sidebar-transition-duration) ease-in-out;
  }
`;

const MainMenuList = styled.ul`
  margin: 0;
  padding: 0;
  list-style-type: none;
`;

interface SidebarFooterProps {
  isOpen: boolean;
  isVisible: boolean;
}

const SidebarFooter = styled.div<SidebarFooterProps>`
  background-color: rgb(46, 31, 94);
  margin-top: auto;
  transition: width var(--sidebar-transition-duration) ease-in-out !important;

  > ul,
  ul > li {
    margin: 0;
    padding: 0;
    list-style-type: none;
  }

  ul > li {
    position: relative;
  }

  > ul {
    transition: max-height var(--sidebar-transition-duration) ease-in-out;
    visibility: hidden;
    max-height: 0;

    a {
      border-inline-start: 3px solid transparent;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  ${(props) =>
    props.isOpen
      ? `
    > ul {
      max-height: 85px;
      visibility: visible;
    }
  `
      : ''}
`;

interface AccountButtonProps {
  slim: boolean;
}

const AccountButton = styled.button<AccountButtonProps>`
  background-color: var(--sidebar-background-color);
  color: rgba(255, 255, 255, 0.8));
  display: flex;
  align-items: center;
  position: relative;
  width: 100%;
  appearance: none;
  border: 0;
  overflow: hidden;
  padding: 0.75rem ${(props) => (props.slim ? '1rem' : '1.25rem')};
  transition: background-color var(--sidebar-transition-duration) ease-in-out;
  cursor: pointer;

  &:hover,
  &:focus {
    background-color: rgba(0, 0, 0, 0.2);
  }

  &:focus {
    outline: 2px solid var(--w-color-focus, #00b0b1);
    outline-offset: -2px;
  }
`;

interface AccountToggleProps {
  slim: boolean;
}

const AccountToggle = styled.div<AccountToggleProps>`
  padding-left: 0.5rem;
  display: ${(props) => (props.slim ? 'none' : 'inline-flex')};
  justify-content: space-between;
  width: 100%;
  transform: translateX(0);
  transition: all var(--sidebar-transition-duration) ease-in-out;
  min-width: 0;

  .icon {
    flex-shrink: 0;
  }
`;

const AccountLabel = styled.div`
  color: var(--w-color-text-label-menus-default, rgba(255, 255, 255, 0.8));
  text-align: left;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-size: 0.875rem;
  line-height: 1.25;
`;

const Avatar = styled.div`
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

interface MenuProps {
  menuItems: MenuItemDefinition[];
  accountMenuItems: MenuItemDefinition[];
  user: MainMenuModuleDefinition['user'];
  slim: boolean;
  expandingOrCollapsing: boolean;
  onHideMobile: () => void;
  currentPath: string;

  navigate(url: string): Promise<void>;
}

export function Menu({
  menuItems,
  accountMenuItems,
  user,
  expandingOrCollapsing,
  onHideMobile,
  slim,
  currentPath,
  navigate,
}: MenuProps) {
  // navigationPath and activePath are two dot-delimited path's referencing a menu item
  // They are created by concatenating the name fields of all the menu/sub-menu items leading to the relevant one.
  // For example, the "Users" item in the "Settings" sub-menu would have the path 'settings.users'
  // - navigationPath references the current sub-menu that the user currently has open
  // - activePath references the menu item for the page the user is currently on
  const [state, dispatch] = React.useReducer(menuReducer, {
    navigationPath: '',
    activePath: '',
    dismissibles: getInitialDismissibleState(menuItems),
  });
  const isVisible = !slim || expandingOrCollapsing;
  const accountSettingsOpen = state.navigationPath.startsWith('.account');

  React.useEffect(() => {
    // Force account navigation to closed state when in slim mode
    if (slim && accountSettingsOpen) {
      dispatch({
        type: 'set-navigation-path',
        path: '',
      });
    }
  }, [slim]);

  // Whenever currentPath or menu changes, work out new activePath
  React.useEffect(() => {
    const urlPathsToNavigationPaths: [string, string][] = [];
    const walkMenu = (path: string, walkingMenuItems: MenuItemDefinition[]) => {
      walkingMenuItems.forEach((item) => {
        const newPath = `${path}.${item.name}`;

        if (item instanceof LinkMenuItemDefinition) {
          urlPathsToNavigationPaths.push([item.url, newPath]);
        } else if (item instanceof SubMenuItemDefinition) {
          walkMenu(newPath, item.menuItems);
        }
      });
    };

    walkMenu('', menuItems);
    walkMenu('', accountMenuItems);

    let bestMatch: [string, string] | null = null;
    urlPathsToNavigationPaths.forEach(([urlPath, navPath]) => {
      if (currentPath.startsWith(urlPath)) {
        if (bestMatch == null || urlPath.length > bestMatch[0].length) {
          bestMatch = [urlPath, navPath];
        }
      }
    });

    const newActivePath = bestMatch ? bestMatch[1] : '';
    if (newActivePath !== state.activePath) {
      dispatch({
        type: 'set-active-path',
        path: newActivePath,
      });
    }
  }, [currentPath, menuItems]);

  React.useEffect(() => {
    // Close submenus when user presses escape
    const onKeydown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        dispatch({
          type: 'set-navigation-path',
          path: '',
        });

        if (state.navigationPath === '') {
          onHideMobile();
        }
      }
    };

    const onClickOutside = (e: MouseEvent | TouchEvent) => {
      const sidebar = document.querySelector('[data-wagtail-sidebar]');

      const isInside = sidebar && sidebar.contains(e.target as Node);
      if (!isInside && state.navigationPath !== '') {
        dispatch({
          type: 'set-navigation-path',
          path: '',
        });
      }
    };

    document.addEventListener('keydown', onKeydown);
    document.addEventListener('mousedown', onClickOutside);
    document.addEventListener('touchend', onClickOutside);

    return () => {
      document.removeEventListener('keydown', onKeydown);
      document.removeEventListener('mousedown', onClickOutside);
      document.removeEventListener('touchend', onClickOutside);
    };
  }, [state.navigationPath]);

  const onClickAccountSettings = () => {
    // Pass account expand information to Sidebar component

    if (accountSettingsOpen) {
      dispatch({
        type: 'set-navigation-path',
        path: '',
      });
    } else {
      dispatch({
        type: 'set-navigation-path',
        path: '.account',
      });
    }
  };

  return (
    <>
      <MainMenuNav
        accountSettingsOpen={accountSettingsOpen}
        aria-label={gettext('Main menu')}
      >
        <MainMenuList>
          {renderMenu('', menuItems, slim, state, dispatch, navigate)}
        </MainMenuList>
      </MainMenuNav>
      <SidebarFooter isOpen={accountSettingsOpen} isVisible={isVisible}>
        <Tippy disabled={!slim} content={user.name} placement="right">
          <AccountButton
            slim={slim}
            onClick={onClickAccountSettings}
            aria-haspopup="menu"
            aria-expanded={accountSettingsOpen ? 'true' : 'false'}
            type="button"
          >
            <Avatar>
              <img
                src={user.avatarUrl}
                alt=""
                decoding="async"
                loading="lazy"
              />
            </Avatar>
            <AccountToggle slim={slim}>
              <AccountLabel>{user.name}</AccountLabel>
              <Icon name={accountSettingsOpen ? 'arrow-down' : 'arrow-up'} />
            </AccountToggle>
          </AccountButton>
        </Tippy>

        <ul>
          {renderMenu('', accountMenuItems, slim, state, dispatch, navigate)}
        </ul>
      </SidebarFooter>
    </>
  );
}

export class MainMenuModuleDefinition implements ModuleDefinition {
  menuItems: MenuItemDefinition[];
  accountMenuItems: MenuItemDefinition[];
  user: {
    name: string;
    avatarUrl: string;
  };

  constructor(
    menuItems: MenuItemDefinition[],
    accountMenuItems: MenuItemDefinition[],
    user: MainMenuModuleDefinition['user'],
  ) {
    this.menuItems = menuItems;
    this.accountMenuItems = accountMenuItems;
    this.user = user;
  }

  render({
    slim,
    expandingOrCollapsing,
    onHideMobile,
    key,
    currentPath,
    navigate,
  }) {
    return (
      <Menu
        menuItems={this.menuItems}
        accountMenuItems={this.accountMenuItems}
        user={this.user}
        slim={slim}
        expandingOrCollapsing={expandingOrCollapsing}
        onHideMobile={onHideMobile}
        key={key}
        currentPath={currentPath}
        navigate={navigate}
      />
    );
  }
}
