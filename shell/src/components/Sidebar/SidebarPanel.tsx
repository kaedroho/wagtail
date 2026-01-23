import * as React from 'react';
import { styled } from '@linaria/react';

const MENU_WIDTH = '200px';
const MENU_WIDTH_SLIM = '70px';

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
  --width: ${(props) => (props.widthPx ? `${props.widthPx}px` : MENU_WIDTH)};
  --w-direction-factor: 1;

  transform: translateX(calc(var(--sidebar-direction-factor) * -100%));
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
    inset-inline-start var(--sidebar-transition-duration) ease-in-out,
    visibility var(--sidebar-transition-duration) ease-in-out;

  @media (forced-colors: active) {
    border-inline-start: 1px solid transparent;
    border-inline-end: 1px solid transparent;
  }

  /* Desktop styles */
  @media (min-width: 800px) {
    z-index: ${(props) => props.zIndex};
    width: var(--width);
  }

  /* Visible state */
  ${(props) =>
    props.isVisible
      ? `
    visibility: visible;
    box-shadow: 2px 0 2px rgba(0, 0, 0, 0.35);
  `
      : 'visibility: hidden;'}

  /* Mobile open state */
  ${(props) =>
    props.isMobile && props.isOpen
      ? `
    transform: translateX(0);
  `
      : ''}

  /* Desktop: slim sidebar positioning (only for top-level panels) */
  @media (min-width: 800px) {
    ${(props) =>
      props.slim && !props.isNested
        ? `
      inset-inline-start: ${MENU_WIDTH_SLIM};
    `
        : ''}

    /* Desktop: nested panels in slim mode */
    ${(props) =>
      props.slim && props.isNested
        ? `
      inset-inline-start: 0;
    `
        : ''}

    /* Desktop: open state */
    ${(props) =>
      !props.isMobile && props.isOpen
        ? `
      transform: translateX(0);
      inset-inline-start: ${props.isNested ? (props.slim ? MENU_WIDTH_SLIM : '0') : MENU_WIDTH};
    `
        : ''}

    /* Desktop: open state in slim mode (top-level) */
    ${(props) =>
      !props.isMobile && props.isOpen && props.slim && !props.isNested
        ? `
      inset-inline-start: ${MENU_WIDTH_SLIM};
    `
        : ''}
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
