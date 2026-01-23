import * as React from 'react';

import Tippy from '@tippyjs/react';
import Icon from '../../Icon/Icon';
import {
  MenuItemDefinition,
  MenuItemProps,
  MenuItemWrapper,
  MenuItemLink,
  MenuItem,
  MenuItemLabel,
} from './MenuItem';
import { gettext } from '../../../utils/gettext';
import { isDismissed } from '../modules/MainMenu';

export function LinkMenuItem({
  item,
  slim,
  path,
  state,
  dispatch,
  navigate,
}: MenuItemProps<LinkMenuItemDefinition>) {
  const isCurrent = state.activePath === path;
  const isActive = state.activePath.startsWith(path);
  const isInSubMenu = path.split('.').length > 2;

  const onClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    // Do not capture click events with modifier keys or non-main buttons.
    if (e.ctrlKey || e.shiftKey || e.metaKey || (e.button && e.button !== 0)) {
      return;
    }

    if (!isDismissed(item, state)) {
      dispatch({
        type: 'set-dismissible-state',
        item,
      });
    }

    // For compatibility purposes – do not capture clicks for links with a target.
    if (item.attrs.target) {
      return;
    }

    e.preventDefault();

    navigate(item.url).then(() => {
      // Set active menu item
      dispatch({
        type: 'set-active-path',
        path,
      });

      // Reset navigation path to close any open submenus
      dispatch({
        type: 'set-navigation-path',
        path: '',
      });
    });
  };

  return (
    <MenuItemWrapper isActive={isActive} isInSubMenu={isInSubMenu} slim={slim}>
      <Tippy
        disabled={!slim || isInSubMenu}
        content={item.label}
        placement="right"
      >
        <MenuItemLink
          {...item.attrs}
          href={item.url}
          aria-current={isCurrent ? 'page' : undefined}
          onClick={onClick}
          isInSubMenu={isInSubMenu}
          slim={slim}
        >
          {item.iconName && (
            <Icon name={item.iconName} className="icon--menuitem" />
          )}
          <MenuItem>
            <MenuItemLabel slim={slim} isInSubMenu={isInSubMenu}>
              {item.label}
            </MenuItemLabel>
          </MenuItem>
        </MenuItemLink>
      </Tippy>
    </MenuItemWrapper>
  );
}

export class LinkMenuItemDefinition implements MenuItemDefinition {
  name: string;
  label: string;
  url: string;
  attrs: { [key: string]: any };
  iconName: string | null;
  classNames?: string;

  constructor({
    name,
    label,
    url,
    attrs = {},
    icon_name: iconName = null as string | null,
    classname = undefined as string | undefined,
  }) {
    this.name = name;
    this.label = label;
    this.url = url;
    this.attrs = attrs;
    this.iconName = iconName;
    this.classNames = classname;
  }

  render({ path, slim, state, dispatch, navigate }) {
    return (
      <LinkMenuItem
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
