import { css } from '@linaria/core';
import { styled } from '@linaria/react';

import { MenuAction, MenuState } from '../modules/MainMenu';
import { SIDEBAR_TRANSITION_DURATION } from '../Sidebar';

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

  ${(props) =>
    props.isActive
      ? `
    background-color: rgba(0, 0, 0, 0.2);
    text-shadow: -1px -1px 0 rgba(0, 0, 0, 0.35);
    border-inline-start-color: #00b0b1;

    > a, > form button {
      color: white;
    }
  `
      : ''}
`;

interface MenuItemLinkProps {
  isInSubMenu: boolean;
  slim: boolean;
}

const commonMenuItemStyles = `
  font-size: 0.875rem;
  line-height: 1;
  transition:
    border-color ${SIDEBAR_TRANSITION_DURATION}ms ease,
    background-color ${SIDEBAR_TRANSITION_DURATION}ms ease;
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
  padding: 13px 15px 13px 20px;
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
  ${(props) =>
    props.isInSubMenu
      ? `
      line-height: 1.25;
      white-space: normal;
      align-items: flex-start;
    `
      : ''}

  ${(props) =>
    props.slim && !props.isInSubMenu
      ? `
      margin-inline-start: auto;
      display: inline-flex;

      .sidebar-sub-menu-trigger-icon {
        margin-inline-start: 0;
      }
    `
      : ''}

    ${(props) =>
    props.slim && props.isInSubMenu
      ? `
      justify-content: flex-start;
    `
      : ''}
`;

export const MenuItemButton = styled.button<MenuItemLinkProps>`
  ${commonMenuItemStyles}
  ${(props) =>
    props.isInSubMenu
      ? `
        line-height: 1.25;
        white-space: normal;
        align-items: flex-start;
      `
      : ''}

  ${(props) =>
    props.slim && !props.isInSubMenu
      ? `
        margin-inline-start: auto;
        display: inline-flex;

        .sidebar-sub-menu-trigger-icon {
          margin-inline-start: 0;
        }
      `
      : ''}

      ${(props) =>
    props.slim && props.isInSubMenu
      ? `
        justify-content: flex-start;
      `
      : ''}
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
  transition: opacity ${SIDEBAR_TRANSITION_DURATION}ms ease;
  margin-inline-start: 0.875rem;
  line-height: 1.25;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;

  ${(props) =>
    props.slim && !props.isInSubMenu
      ? `
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  `
      : ''}

  ${(props) =>
    props.slim && props.isInSubMenu
      ? `
    position: static;
    width: auto;
    height: auto;
    padding: 0;
    margin: 0;
    margin-inline-start: 1rem;
    overflow: visible;
    clip: auto;
    white-space: normal;
  `
      : ''}
`;
