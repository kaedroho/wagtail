import * as React from 'react';
import { styled } from '@linaria/react';

import Tippy from '@tippyjs/react';
import Icon from '../../Icon/Icon';

import { isDismissed, renderMenu } from '../modules/MainMenu';
import SidebarPanel from '../SidebarPanel';
import { SIDEBAR_TRANSITION_DURATION } from '../Sidebar';
import {
  MenuItemDefinition,
  MenuItemProps,
  MenuItemWrapper,
  MenuItemButton,
  MenuItemLabel,
} from './MenuItem';
import { gettext } from '../../../utils/gettext';
import SubMenuCloseButton from './SubMenuCloseButton';

interface SubMenuItemWrapperProps {
  isActive: boolean;
  isInSubMenu: boolean;
  slim: boolean;
  isOpen: boolean;
}

const SubMenuItemWrapper = styled(MenuItemWrapper)<SubMenuItemWrapperProps>`
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

const SubMenuPanel = styled.div`
  display: flex;
  flex-direction: column;
  background-color: rgba(0, 0, 0, 0.2);
  height: 100vh;
  width: var(--sidebar-subpanel-width);
  transition:
    transform var(--sidebar-transition-duration) ease-in-out,
    visibility var(--sidebar-transition-duration) ease-in-out;

  > h2 {
    min-height: 180px;
    padding-left: 1rem;
    padding-right: 1rem;
    box-sizing: border-box;
    text-align: center;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 0;
    display: inline-flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: var(--sidebar-subpanel-width);
    transition:
      transform var(--sidebar-transition-duration) ease-in-out,
      visibility var(--sidebar-transition-duration) ease-in-out;
  }

  > ul {
    flex-grow: 1;
    padding: 0;
    margin: 0;
    overflow-y: auto;

    > li {
      transition: border-color var(--sidebar-transition-duration) ease-in-out;
      position: relative;
    }
  }
`;

const SubMenuPanelFooter = styled.p`
  margin: 0;
  padding: 0.9em 1.7em;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
`;

interface SubMenuItemProps extends MenuItemProps<SubMenuItemDefinition> {
  slim: boolean;
  isMobile?: boolean;
}

export function SubMenuItem({
  path,
  item,
  slim,
  state,
  dispatch,
  navigate,
  isMobile = false,
}: SubMenuItemProps) {
  const isOpen = state.navigationPath.startsWith(path);
  const isActive = isOpen || state.activePath.startsWith(path);
  const depth = path.split('.').length;
  const [isVisible, setIsVisible] = React.useState(false);
  const [hasBeenOpened, setHasBeenOpened] = React.useState(false);

  const dismissibleCount = item.menuItems.filter(
    (subItem) => !isDismissed(subItem, state),
  ).length;

  React.useEffect(() => {
    if (isOpen) {
      // isOpen is set at the moment the user clicks the menu item
      setIsVisible(true);
    } else if (!isOpen && isVisible) {
      // When a submenu is closed, we have to wait for the close animation
      // to finish before making it invisible
      setTimeout(() => {
        setIsVisible(false);
      }, SIDEBAR_TRANSITION_DURATION);
    }
  }, [isOpen]);

  const onClick = () => {
    // Only dispatch set-dismissible-state when there are dismissible items
    // in the submenu and the submenu has not been opened before. Note that
    // the term "submenu" for this component means that this menu item *has*
    // "sub" items (children), rather than the actual "sub" menu items inside it.
    if (!hasBeenOpened && dismissibleCount > 0) {
      // Dispatching set-dismissible-state from this submenu also collect
      // all dismissible items in the submenu and set their state to dismissed
      // on the server, so that those child items won't show up as "new" again on
      // the next load.
      // However, the client state for the child items is only updated on the
      // next reload or if the individual items are clicked, so that the user
      // has the chance to see the "new" badge for those items.
      // After clicking this at least once, even if hasBeenOpened is false on
      // the next load, all the child items have been dismissed (dismissibleCount == 0),
      // so the "new" badge will not show up again (unless the server adds a new item).
      dispatch({
        type: 'set-dismissible-state',
        item,
      });
    }

    if (isOpen) {
      const pathComponents = path.split('.');
      pathComponents.pop();
      const parentPath = pathComponents.join('.');
      dispatch({
        type: 'set-navigation-path',
        path: parentPath,
      });
    } else {
      dispatch({
        type: 'set-navigation-path',
        path,
      });
      setHasBeenOpened(true);
    }
  };

  const isInSubMenu = depth > 2;

  return (
    <SubMenuItemWrapper
      isActive={isActive}
      isInSubMenu={isInSubMenu}
      slim={slim}
      isOpen={isOpen}
    >
      <Tippy disabled={isOpen || !slim} content={item.label} placement="right">
        <MenuItemButton
          {...item.attrs}
          onClick={onClick}
          aria-haspopup="menu"
          aria-expanded={isOpen ? 'true' : 'false'}
          type="button"
          isInSubMenu={isInSubMenu}
          slim={slim}
        >
          {item.iconName && (
            <Icon name={item.iconName} className="icon--menuitem" />
          )}
          <MenuItemLabel slim={slim} isInSubMenu={isInSubMenu}>
            {item.label}
          </MenuItemLabel>

          {
            // Only show the dismissible badge if the menu item has not been
            // opened yet, so it's less distracting after the user has opened it.
          }
          {dismissibleCount > 0 && !hasBeenOpened && (
            <span className="w-dismissible-badge w-dismissible-badge--count">
              <span aria-hidden="true">{dismissibleCount}</span>
              <span className="w-sr-only">
                {dismissibleCount === 1
                  ? gettext('(1 new item in this menu)')
                  : gettext('(%(number)s new items in this menu)').replace(
                      '%(number)s',
                      `${dismissibleCount}`,
                    )}
              </span>
            </span>
          )}
          <TriggerIcon name="arrow-right" isOpen={isOpen} slim={slim} />
        </MenuItemButton>
      </Tippy>
      <SidebarPanel
        isVisible={isVisible}
        isOpen={isOpen}
        depth={depth}
        slim={slim}
        isMobile={isMobile}
      >
        <SubMenuPanel>
          <SubMenuCloseButton isVisible={isVisible} dispatch={dispatch} />
          <h2
            id={`wagtail-sidebar-submenu${path.split('.').join('-')}-title`}
            className={item.classNames}
          >
            {item.iconName && (
              <Icon name={item.iconName} className="icon--submenu-header" />
            )}
            {item.label}
          </h2>
          <ul
            aria-labelledby={`wagtail-sidebar-submenu${path
              .split('.')
              .join('-')}-title`}
          >
            {renderMenu(path, item.menuItems, slim, state, dispatch, navigate)}
          </ul>
          {item.footerText && (
            <SubMenuPanelFooter>{item.footerText}</SubMenuPanelFooter>
          )}
        </SubMenuPanel>
      </SidebarPanel>
    </SubMenuItemWrapper>
  );
}

export class SubMenuItemDefinition implements MenuItemDefinition {
  name: string;
  label: string;
  menuItems: MenuItemDefinition[];
  attrs: { [key: string]: any };
  iconName: string | null;
  classNames?: string;
  footerText: string;

  constructor(
    {
      name,
      label,
      attrs = {},
      icon_name: iconName = null,
      classname = undefined,
      footer_text: footerText = '',
    }: any,
    menuItems: MenuItemDefinition[],
  ) {
    this.name = name;
    this.label = label;
    this.menuItems = menuItems;
    this.attrs = attrs;
    this.iconName = iconName;
    this.classNames = classname;
    this.footerText = footerText;
  }

  render({ path, slim, state, dispatch, navigate }) {
    return (
      <SubMenuItem
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
