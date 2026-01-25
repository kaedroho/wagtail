import * as React from 'react';
import { useContext } from 'react';
import { styled } from '@linaria/react';

import { gettext } from '../../utils/gettext';
import Icon from '../Icon/Icon';
import { SidebarContext } from '../../contexts';

export const SIDEBAR_TRANSITION_DURATION = 150;

export interface ModuleRenderContext {
  key: number;
  slim: boolean;
  expandingOrCollapsing: boolean;
  onHideMobile: () => void;
  onSearchClick: () => void;
  currentPath: string;
  navigate(url: string): Promise<void>;
}

export interface ModuleDefinition {
  render(context: ModuleRenderContext): React.ReactFragment;
}

interface WrapperProps {
  slim: boolean;
  isMobile: boolean;
  hidden: boolean;
  closed: boolean;
}

const Wrapper = styled.aside<WrapperProps>`
  position: fixed;
  display: flex;
  flex-direction: column;
  width: var(--sidebar-width);
  height: 100%;
  inset-inline-start: 0;
  z-index: 90; /* sidebar z-index */
  transition:
    width var(--sidebar-transition-duration) ease-in-out,
    inset-inline-start var(--sidebar-transition-duration) ease-in-out;
  background-color: var(--sidebar-background-color);

  @media (forced-colors: active) {
    border-inline-end: 1px solid transparent;
  }

  .icon--menuitem {
    width: 1rem;
    height: 1rem;
    min-width: 1rem;
    margin: 0.046875rem 0;
  }
`;

const SidebarInner = styled.div`
  height: 100%;
  background-color: var(--sidebar-background-color);
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
`;

interface CollapseToggleProps {
  slim: boolean;
}

const CollapseToggle = styled.button<CollapseToggleProps>`
  transition: background-color var(--sidebar-transition-duration) ease-in-out;
  position: static;
  color: rgba(255, 255, 255, 0.8);
  width: 35px;
  height: 35px;
  background: transparent;
  place-items: center;
  padding: 0;
  border-radius: 50%;
  border: 1px solid transparent;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: ${(props) => (props.slim ? '10px' : '1rem')};
  cursor: pointer;

  svg {
    width: 15px;
    height: 16px;
  }

  &:hover {
    background-color: rgba(0, 0, 0, 0.2);
    color: white;
    opacity: 1;
  }
`;

interface NavToggleProps {
  isMobile: boolean;
  isOpen: boolean;
}

const NavToggle = styled.button<NavToggleProps>`
  transition: background-color var(--sidebar-toggle-duration) ease-in-out;
  position: absolute;
  top: 12px;
  inset-inline-start: 12px;
  color: rgba(255, 255, 255, 0.8);
  width: 35px;
  height: 35px;
  background: transparent;
  place-items: center;
  padding: 0;
  border-radius: 50%;
  border: 1px solid transparent;
  z-index: 91; /* above sidebar */
  display: none;

  svg {
    width: 15px;
    height: 16px;
  }

  ${(props) =>
    props.isMobile
      ? `
    display: grid;
    background-color: var(--sidebar-background-color);
    top: 0;
    left: 0;
    height: 50px;
    width: 50px;
    border-radius: 0;

    &:hover {
      background-color: rgba(0, 0, 0, 0.2);
    }
  `
      : ''}

  ${(props) =>
    props.isOpen
      ? `
    position: fixed;

    &:hover {
      background-color: rgba(0, 0, 0, 0.2);
      color: white;
    }
  `
      : ''}
`;

const CollapseToggleWrapper = styled.div<{ slim: boolean }>`
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-top: 0.5rem;

  @media (min-width: 800px) {
    margin-top: 0.5rem;
  }
`;

export interface SidebarProps {
  currentPath: string;
  navigate(url: string): Promise<void>;
  collapsed: boolean;
  setCollapsed(collapsed: boolean): void;
}

export default function Sidebar({
  currentPath,
  navigate,
  collapsed,
  setCollapsed,
}: SidebarProps) {
  const { modules } = useContext(SidebarContext);

  const mobileNavToggleRef = React.useRef<HTMLButtonElement>(null);

  // 'visibleOnMobile' indicates whether the sidebar is currently visible on mobile
  // On mobile, the sidebar is completely hidden by default and must be opened manually
  const [visibleOnMobile, setVisibleOnMobile] = React.useState(false);
  // 'closedOnMobile' is used to set the menu to display none so it can no longer be interacted with by keyboard when its hidden
  const [closedOnMobile, setClosedOnMobile] = React.useState(true);

  // Tracks whether the screen is below 800 pixels. In this state, the menu is completely hidden.
  // State is used here in case the user changes their browser size
  const checkWindowSizeIsMobile = () => window.innerWidth < 800;
  const [isMobile, setIsMobile] = React.useState(checkWindowSizeIsMobile());
  React.useEffect(() => {
    function handleResize() {
      if (checkWindowSizeIsMobile()) {
        setIsMobile(true);
        return null;
      }
      setIsMobile(false);

      // Close the menu and animate out as this state is not used in desktop
      setVisibleOnMobile(false);
      // wait for animation to finish then hide menu from screen readers as well.
      return setTimeout(() => {
        setClosedOnMobile(true);
      }, SIDEBAR_TRANSITION_DURATION);
    }

    window.addEventListener('resize', handleResize);
    const closeTimeout = handleResize();
    return () => {
      window.removeEventListener('resize', handleResize);
      if (closeTimeout) {
        clearTimeout(closeTimeout);
      }
    };
  }, []);

  // Whether or not to display the menu with slim layout.
  const slim = collapsed && !isMobile;

  // 'expandingOrCollapsing' is set to true whilst the menu is transitioning between slim and expanded layouts
  const [expandingOrCollapsing, setExpandingOrCollapsing] =
    React.useState(false);

  React.useEffect(() => {
    setExpandingOrCollapsing(true);
    const finishTimeout = setTimeout(() => {
      setExpandingOrCollapsing(false);
    }, SIDEBAR_TRANSITION_DURATION);

    return () => {
      clearTimeout(finishTimeout);
    };
  }, [slim]);

  const onClickCollapseToggle = () => {
    setCollapsed(!collapsed);
  };

  const onClickOpenCloseToggle = () => {
    setVisibleOnMobile(!visibleOnMobile);
    setExpandingOrCollapsing(true);

    const finishTimeout = setTimeout(() => {
      setExpandingOrCollapsing(false);
      setClosedOnMobile(!closedOnMobile);
    }, SIDEBAR_TRANSITION_DURATION);
    return () => {
      clearTimeout(finishTimeout);
    };
  };

  const [focused, setFocused] = React.useState(false);

  const onBlurHandler = () => {
    if (focused) {
      setFocused(false);
      setCollapsed(true);
    }
  };

  const onFocusHandler = () => {
    if (focused) {
      setCollapsed(false);
      setFocused(true);
    }
  };

  const onSearchClick = () => {
    if (slim) {
      onClickCollapseToggle();
    }
  };

  React.useEffect(() => {
    // wait for animation to finish then hide menu from screen readers as well.
    const finishHidingMenu = setTimeout(() => {
      if (!visibleOnMobile) {
        setClosedOnMobile(true);
      }
    }, SIDEBAR_TRANSITION_DURATION);

    return () => {
      clearTimeout(finishHidingMenu);
    };
  }, [visibleOnMobile]);

  const onHideMobile = () => {
    setVisibleOnMobile(false);

    if (mobileNavToggleRef) {
      // When menu is closed with escape key bring focus back to open close toggle
      mobileNavToggleRef.current?.focus();
    }
  };

  // Render modules
  const renderedModules = modules.map((module, index) =>
    module.render({
      key: index,
      slim,
      expandingOrCollapsing,
      onHideMobile,
      onSearchClick,
      currentPath,
      navigate,
    }),
  );

  return (
    <>
      <NavToggle
        onClick={onClickOpenCloseToggle}
        aria-expanded={visibleOnMobile ? 'true' : 'false'}
        aria-keyshortcuts="["
        aria-label={gettext('Toggle sidebar')}
        type="button"
        ref={mobileNavToggleRef}
        isMobile={isMobile}
        isOpen={visibleOnMobile}
      >
        {visibleOnMobile ? <Icon name="cross" /> : <Icon name="bars" />}
      </NavToggle>
      <Wrapper
        slim={slim}
        isMobile={isMobile}
        hidden={isMobile && !visibleOnMobile}
        closed={isMobile && !visibleOnMobile && closedOnMobile}
        data-wagtail-sidebar
      >
        <SidebarInner onFocus={onFocusHandler} onBlur={onBlurHandler}>
          {!isMobile && (
            <CollapseToggleWrapper slim={slim}>
              <CollapseToggle
                onClick={onClickCollapseToggle}
                aria-expanded={slim ? 'false' : 'true'}
                aria-keyshortcuts="["
                aria-label={gettext('Toggle sidebar')}
                type="button"
                slim={slim}
              >
                <Icon
                  name="expand-right"
                  style={{
                    transform: !collapsed ? 'rotate(-180deg)' : undefined,
                  }}
                />
              </CollapseToggle>
            </CollapseToggleWrapper>
          )}

          {renderedModules}
        </SidebarInner>
      </Wrapper>
    </>
  );
}
