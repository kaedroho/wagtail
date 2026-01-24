import { css } from '@linaria/core';
import { styled } from '@linaria/react';

import { MenuAction, MenuState } from '../modules/MainMenu';

export interface MenuItemRenderContext {
  path: string;
  state: MenuState;
  slim: boolean;
  dispatch(action: MenuAction): void;
  navigate(url: string): Promise<void>;
}

export interface MenuItemDefinition {
  name: string;
  label: string;
  attrs: { [key: string]: any };
  iconName: string | null;
  classNames?: string;
  render(context: MenuItemRenderContext): React.ReactFragment;
}

export interface MenuItemProps<T> {
  path: string;
  slim: boolean;
  state: MenuState;
  item: T;
  dispatch(action: MenuAction): void;
  navigate(url: string): Promise<void>;
}

// Shared styled components for menu items

interface MenuItemWrapperProps {
  isActive: boolean;
  isInSubMenu: boolean;
  slim: boolean;
}

export const MenuItemWrapper = styled.li<MenuItemWrapperProps>`
  transition: border-color var(--sidebar-transition-duration) ease;
  position: relative;
  background-color: ${(props) =>
    props.isActive ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0)'};
  text-shadow: ${(props) =>
    props.isActive ? '-1px -1px 0 rgba(0, 0, 0, 0.35)' : 'none'};
  border-inline-start: ${(props) =>
    props.isActive ? '2px solid #00b0b1' : '2px solid transparent'};

  > a,
  > form button {
    color: ${(props) =>
      props.isActive ? 'white' : 'rgba(255, 255, 255, 0.8)'};
  }
`;

interface MenuItemLinkProps {
  isInSubMenu: boolean;
  slim: boolean;
}

const commonMenuItemStyles = `
  font-size: 0.875rem;
  transition:
    border-color var(--sidebar-transition-duration) ease-in-out,
    background-color var(--sidebar-transition-duration) ease-in-out;
  position: relative;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  white-space: nowrap;
  border: 0;
  background: transparent;
  text-align: start;
  color: rgba(255, 255, 255, 0.8);
  padding: 12px 15px 12px 20px;
  font-weight: 400;
  overflow: visible;
  -webkit-font-smoothing: auto;
  text-decoration: none;
  cursor: pointer;

  &:hover,
  &:focus {
    color: white;
    text-shadow: -1px -1px 0 rgba(0, 0, 0, 0.35);
  }
`;

export const MenuItemLink = styled.a<MenuItemLinkProps>`
  ${commonMenuItemStyles}
`;

export const MenuItemButton = styled.button<MenuItemLinkProps>`
  ${commonMenuItemStyles}
`;

export const MenuItem = styled.div`
  display: flex;
  justify-content: space-between;
  width: 100%;
`;

interface MenuItemLabelProps {
  slim: boolean;
  isInSubMenu: boolean;
}

export const MenuItemLabel = styled.span<MenuItemLabelProps>`
  transition: opacity var(--sidebar-transition-duration) ease-in-out;
  opacity: ${(props) => (props.slim && !props.isInSubMenu ? '0' : '1')};
  line-height: 1.5;
  white-space: normal;
  margin-inline-start: 0.875rem;
`;
