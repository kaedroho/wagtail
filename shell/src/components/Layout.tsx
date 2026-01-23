import React, { PropsWithChildren, useContext, useState } from 'react';
import { css } from '@linaria/core';
import { styled } from '@linaria/react';
import { NavigationContext } from '@django-bridge/react';

import Sidebar from './Sidebar/Sidebar';

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
    }
  }
`;

const Wrapper = styled.div<{ sidebarCollapsed: boolean }>`
  --sidebar-direction-factor: 1;
  --sidebar-full-width: 200px;
  --sidebar-slim-width: 60px;
  --sidebar-width: ${(props) =>
    props.sidebarCollapsed
      ? 'var(--sidebar-slim-width)'
      : 'var(--sidebar-full-width)'};
  --sidebar-subpanel-width: 200px;
  --sidebar-transition-duration: 150ms;
  --sidebar-background-color: rgb(46, 31, 94);

  display: flex;
  flex-flow: row nowrap;
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
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <Wrapper sidebarCollapsed={sidebarCollapsed}>
      <Sidebar
        currentPath={path}
        navigate={navigate}
        onExpandCollapse={setSidebarCollapsed}
      />
      <MainContentWrapper>{children}</MainContentWrapper>
    </Wrapper>
  );
}
