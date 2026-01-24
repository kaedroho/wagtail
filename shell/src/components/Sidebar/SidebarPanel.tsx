import * as React from 'react';
import { styled } from '@linaria/react';

interface PanelWrapperProps {
  isVisible: boolean;
  isOpen: boolean;
  zIndex: number;
  widthPx?: number;
  slim: boolean;
  isMobile: boolean;
  isNested: boolean;
}

const PanelWrapper = styled.div<PanelWrapperProps>`
  --sidebar-subpanel-width: ${(props) =>
    props.widthPx ? `${props.widthPx}px` : '200px'};

  background-color: var(--sidebar-background-color);
  transform: ${(props) =>
    props.isOpen
      ? 'translateX(0)'
      : 'translateX(calc(var(--sidebar-direction-factor) * -100%))'};
  position: fixed;
  height: 100vh;
  padding: 0;
  top: 0;
  inset-inline-start: 0;
  z-index: 400;
  display: flex;
  flex-direction: column;
  transition:
    transform var(--sidebar-transition-duration) ease-in-out,
    inset-inline-start var(--sidebar-transition-duration) ease-in-out;
  box-shadow: ${(props) =>
    props.isOpen ? '2px 0 2px rgba(0, 0, 0, 0.35)' : 'none'};
  visibility: ${(props) => (props.isVisible ? 'visible' : 'hidden')};
  inset-inline-start: var(--sidebar-width);

  @media (forced-colors: active) {
    border-inline-start: 1px solid transparent;
    border-inline-end: 1px solid transparent;
  }

  /* Desktop styles */
  @media (min-width: 800px) {
    z-index: ${(props) => props.zIndex};
    width: var(--sidebar-subpanel-width);
  }
`;

export interface SidebarPanelProps {
  isVisible: boolean;
  isOpen: boolean;
  depth: number;
  widthPx?: number;
  slim: boolean;
  isMobile: boolean;
}

export default function SidebarPanel({
  isVisible,
  isOpen,
  depth,
  widthPx,
  slim,
  isMobile,
  children,
}: React.PropsWithChildren<SidebarPanelProps>) {
  let zIndex = -depth * 2;

  const isClosing = isVisible && !isOpen;
  if (isClosing) {
    // When closing, make sure this panel displays behind any new panel that is opening
    zIndex -= 1;
  }

  const isNested = depth > 1;

  return (
    <PanelWrapper
      isVisible={isVisible}
      isOpen={isOpen}
      zIndex={zIndex}
      widthPx={widthPx}
      slim={slim}
      isMobile={isMobile}
      isNested={isNested}
    >
      {children}
    </PanelWrapper>
  );
}
