import React, { PropsWithChildren, useContext } from 'react';
import { css } from '@linaria/core';
import { styled } from '@linaria/react';
import {
  MessagesContext,
  NavigationContext,
  Message,
} from '@django-bridge/react';
import Sidebar from './Sidebar/Sidebar';
import { SidebarContext } from '../contexts';
import { useLocalStorage } from '../utils/hooks';
import Icon from './Icon/Icon';

export const globals = css`
  :global() {
    :root {
      --font-sans:
        -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, Roboto,
        'Helvetica Neue', Arial, sans-serif, Apple Color Emoji,
        'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
    }
    body {
      font-family: var(--font-sans);
      font-size: 85%;
      line-height: 1.5em;
      box-sizing: border-box;
    }
    * {
      box-sizing: inherit;
    }
  }
`;

const Wrapper = styled.div<{
  sidebarEnabled: boolean;
  sidebarCollapsed: boolean;
}>`
  --sidebar-direction-factor: 1;
  --sidebar-full-width: 200px;
  --sidebar-slim-width: 60px;
  --sidebar-width: ${(props) =>
    props.sidebarEnabled
      ? props.sidebarCollapsed
        ? 'var(--sidebar-slim-width)'
        : 'var(--sidebar-full-width)'
      : '0px'};
  --sidebar-subpanel-width: 200px;
  --sidebar-transition-duration: 150ms;
  --sidebar-background-color: rgb(46, 31, 94);
  display: flex;
  flex-flow: row nowrap;
`;

const MessagesWrapper = styled.ul`
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-flow: column nowrap;
  gap: 12px;
  list-style-type: none;
  padding: 0;
  margin: 0;
`;

const messageColors = {
  // Palette 3
  success: {
    background: '#effcf6',
    border: '#199473',
    icon: '#199473',
    foreground: 'hsl(254.3 50.4% 24.5%)',
  },
  // Palette 2
  error: {
    background: '#ffeeee',
    border: '#a61b1b',
    icon: '#a61b1b',
    foreground: '#a61b1b',
  },
  // TODO: Check colours
  warning: {
    background: '#fffbeb',
    border: '#fcd34d',
    icon: '#d97706',
    foreground: 'hsl(254.3 50.4% 24.5%)',
  },
  // TODO: Check colours
  info: {
    background: '#eff6ff',
    border: '#93c5fd',
    icon: '#2563eb',
    foreground: 'hsl(254.3 50.4% 24.5%)',
  },
};

const MessageItem = styled.li<{ level: Message['level'] }>`
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  width: 360px;
  border: 1px solid
    ${(props) =>
      messageColors[props.level]?.border ?? messageColors.info.border};
  background-color: ${(props) =>
    messageColors[props.level]?.background ?? messageColors.info.background};
  border-radius: 8px;
  padding: 12px 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.3s ease-in-out;
  transition: all 0.3s ease-in-out;

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(100%);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  > .message-content {
    flex: 1;

    color: ${(props) =>
      messageColors[props.level]?.foreground ?? messageColors.info.foreground};
  }

  svg {
    width: 1.125rem;
    height: 1.125rem;
    min-width: 1.125rem;
    margin-top: 0.0625rem;
    color: ${(props) =>
      messageColors[props.level]?.icon ?? messageColors.info.icon};
  }

  .buttons {
    display: flex;
    flex-flow: row nowrap;
    margin-top: 0.5rem;
  }

  a.button {
    display: inline-flex;
    align-items: center;
    padding: 0.125rem 0.625rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-decoration: none;
    border-radius: 4px;
    color: white;
    border: 1px solid
      ${(props) =>
        messageColors[props.level]?.border ?? messageColors.info.border};
    background-color: ${(props) =>
      messageColors[props.level]?.border ?? messageColors.info.border};
    transition: all 0.15s ease;
    white-space: nowrap;

    &:hover {
      color: ${(props) =>
        messageColors[props.level]?.border ?? messageColors.info.border};
      background-color: transparent;
    }

    & + a.button {
      margin-left: 0.375rem;
    }
  }
`;

const DismissButton = styled.button`
  background: none;
  border: none;
  padding: 0;
  margin-left: 0.5rem;
  cursor: pointer;
  transition: opacity 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    svg {
      color: rgb(46, 31, 94);
    }
  }

  svg {
    width: 1rem;
    height: 1rem;
    color: rgb(92, 92, 92);
  }
`;

const MainContentWrapper = styled.div`
  position: absolute;
  width: calc(100% - var(--sidebar-width));
  height: 100%;
  left: var(--sidebar-width);
  top: 0;
  transition:
    width var(--sidebar-transition-duration) ease-in-out,
    left var(--sidebar-transition-duration) ease-in-out;
`;

export default function Layout({ children }: PropsWithChildren) {
  const { navigate, path } = useContext(NavigationContext);
  const { enabled: sidebarEnabled } = useContext(SidebarContext);
  const [sidebarCollapsed, setSidebarCollapsed] = useLocalStorage(
    'wagtail-sidebar-collapsed',
    false,
  );
  const { messages } = useContext(MessagesContext);

  return (
    <Wrapper
      sidebarEnabled={sidebarEnabled}
      sidebarCollapsed={sidebarCollapsed}
    >
      {sidebarEnabled && (
        <Sidebar
          currentPath={path}
          navigate={navigate}
          collapsed={sidebarCollapsed}
          setCollapsed={setSidebarCollapsed}
        />
      )}
      <MessagesWrapper>
        {messages.map((message) => (
          <MessageItem level={message.level}>
            {(message.level === 'error' || message.level === 'warning') && (
              <Icon name="warning" />
            )}
            {message.level === 'success' && <Icon name="success" />}
            {message.level === 'info' && <Icon name="info" />}
            {'html' in message && (
              <div
                className="message-content"
                dangerouslySetInnerHTML={{ __html: message.html }}
              />
            )}
            {'text' in message && (
              <div className="message-content">{message.text}</div>
            )}
            <DismissButton aria-label="Dismiss message">
              <Icon name="cross" />
            </DismissButton>
          </MessageItem>
        ))}
      </MessagesWrapper>
      <MainContentWrapper>{children}</MainContentWrapper>
    </Wrapper>
  );
}
