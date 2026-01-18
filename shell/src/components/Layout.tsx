import { NavigationContext } from '@django-bridge/react';
import React, { PropsWithChildren, useContext, useState } from 'react';
import { Sidebar } from './Sidebar/Sidebar';

const SIDEBAR_TRANSITION = '0.2s ease-in-out';

export default function Layout({ children }: PropsWithChildren) {
  const { navigate, path } = useContext(NavigationContext);
  const [sidebarExpanded, setSidebarExpanded] = useState(false);

  return (
    <div
      style={{
        'display': 'flex',
        'flexFlow': 'row nowrap',
        '--sidebar-width': sidebarExpanded ? '200px' : '70px',
      }}
    >
      <aside
        style={{
          position: 'absolute',
          width: 'var(--sidebar-width)',
          height: '100%',
          left: '0',
          top: '0',
          transition: `width ${SIDEBAR_TRANSITION}`,
          backgroundColor: 'rgb(46, 31, 94)',
        }}
      >
        <Sidebar
          modules={[]}
          collapsedOnLoad={false}
          currentPath={path}
          navigate={navigate}
        />
      </aside>
      <div
        style={{
          position: 'absolute',
          width: 'calc(100% - var(--sidebar-width))',
          height: '100%',
          left: 'var(--sidebar-width)',
          top: '0',
          transition: `width ${SIDEBAR_TRANSITION}, left ${SIDEBAR_TRANSITION}`,
        }}
      >
        {children}
      </div>
    </div>
  );
}
