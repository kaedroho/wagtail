import * as React from 'react';
import { useContext } from 'react';

import Tippy from '@tippyjs/react';
import Icon from '../../Icon/Icon';
import {
  MenuItemDefinition,
  MenuItemProps,
  MenuItemWrapper,
  MenuItemButton,
  MenuItem,
  MenuItemLabel,
} from './MenuItem';
import { gettext } from '../../../utils/gettext';
import { isDismissed } from '../modules/MainMenu';
import { CsrfTokenContext } from '../../../contexts';

export function ActionMenuItem({
  item,
  slim,
  path,
  state,
  dispatch,
}: MenuItemProps<ActionMenuItemDefinition>) {
  const csrfToken = useContext(CsrfTokenContext);
  const isActive = state.activePath.startsWith(path);
  const isInSubMenu = path.split('.').length > 2;

  const onClick = (e: React.MouseEvent<HTMLButtonElement>) => {
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
  };

  return (
    <MenuItemWrapper isActive={isActive} isInSubMenu={isInSubMenu} slim={slim}>
      <Tippy
        disabled={!slim || isInSubMenu}
        content={item.label}
        placement="right"
      >
        <form {...item.attrs} method={item.method} action={item.action}>
          <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
          <MenuItemButton
            type="submit"
            onClick={onClick}
            isInSubMenu={isInSubMenu}
            slim={slim}
          >
            {item.iconName && (
              <Icon name={item.iconName} className="icon--menuitem" />
            )}
            <MenuItem as="span">
              <MenuItemLabel slim={slim} isInSubMenu={isInSubMenu}>
                {item.label}
              </MenuItemLabel>
            </MenuItem>
          </MenuItemButton>
        </form>
      </Tippy>
    </MenuItemWrapper>
  );
}

export class ActionMenuItemDefinition implements MenuItemDefinition {
  name: string;
  label: string;
  action: string;
  attrs: { [key: string]: any };
  iconName: string | null;
  classNames?: string;
  method: string;

  constructor({
    name,
    label,
    action,
    attrs = {},
    icon_name: iconName = null,
    classname = undefined,
    method = 'POST',
  }) {
    this.name = name;
    this.label = label;
    this.action = action;
    this.attrs = attrs;
    this.iconName = iconName;
    this.classNames = classname;
    this.method = method;
  }

  render({ path, slim, state, dispatch, navigate }) {
    return (
      <ActionMenuItem
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
