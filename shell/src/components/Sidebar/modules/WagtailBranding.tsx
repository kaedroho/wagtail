import * as React from 'react';
import { styled } from '@linaria/react';
import { css } from '@linaria/core';

import { gettext } from '../../../utils/gettext';
import { ModuleDefinition } from '../Sidebar';
import WagtailLogo from './WagtailLogo';

const LOGO_SIZE = '110px';

// Tail wagging animation
const tailWagKeyframes = css`
  @keyframes tail-wag {
    from {
      transform: rotate(-3deg);
    }
    to {
      transform: rotate(20deg) translate(30%, -25%) scale(1.1);
    }
  }
`;

interface BrandingLinkProps {
  slim: boolean;
  isWagging: boolean;
}

const BrandingLink = styled.a<BrandingLinkProps>`
  position: relative;
  display: block;
  align-items: center;
  -webkit-font-smoothing: auto;
  margin: 50px auto 2.75rem;
  text-align: center;
  width: ${(props) => (props.slim ? '40px' : LOGO_SIZE)};
  height: ${(props) => (props.slim ? '110px' : LOGO_SIZE)};
  transition:
    transform 150ms cubic-bezier(0.28, 0.15, 0, 2.1),
    width var(--sidebar-transition-duration) ease-in-out,
    height var(--sidebar-transition-duration) ease-in-out,
    padding-top var(--sidebar-transition-duration) ease-in-out;
  border-radius: 100%;

  @media (min-width: 800px) {
    margin-top: 0.5rem;
  }

  ${(props) =>
    props.slim
      ? `
    &:focus {
      outline: 2px solid #00b0b1;
      outline-offset: -2px;
    }
  `
      : ''}

  ${(props) =>
    props.isWagging
      ? `
    &:hover {
      transition: transform 1.2s ease;

      [data-part='tail'] {
        animation: tail-wag 0.1s alternate;
        animation-iteration-count: infinite;
      }

      [data-part='eye--open'] {
        display: none !important;
      }

      [data-part='eye--closed'] {
        display: inline !important;
      }
    }
  `
      : ''}
`;

interface IconWrapperProps {
  slim: boolean;
}

const IconWrapper = styled.div<IconWrapperProps>`
  background-color: rgba(255, 255, 255, 0.15);
  position: relative;
  overflow: hidden;
  margin: auto;
  width: ${(props) => (props.slim ? '40px' : LOGO_SIZE)};
  height: ${(props) => (props.slim ? '40px' : LOGO_SIZE)};
  border-radius: 50%;
  transition: all var(--sidebar-transition-duration) ease-in-out;

  &:hover {
    overflow: visible;
  }
`;

interface CustomBrandingLinkProps {
  slim: boolean;
}

const CustomBrandingLink = styled.a<CustomBrandingLinkProps>`
  display: block;
  align-items: center;
  -webkit-font-smoothing: auto;
  position: relative;
  margin: 2em auto;
  text-align: center;
  padding: ${(props) => (props.slim ? '40px 0' : '10px 0')};
  transition: padding var(--sidebar-transition-duration) ease-in-out;

  &:hover {
    color: white;
  }
`;

interface WagtailBrandingProps {
  homeUrl: string;
  slim: boolean;
  currentPath: string;
  navigate(url: string): void;
}

export function WagtailBranding({
  homeUrl,
  slim,
  currentPath,
  navigate,
}: WagtailBrandingProps) {
  const brandingLogo = React.useMemo(
    () =>
      document.querySelector<HTMLTemplateElement>(
        '[data-wagtail-sidebar-branding-logo]',
      ),
    [],
  );
  const hasCustomBranding = brandingLogo && brandingLogo.innerHTML !== '';

  const onClick = (e: React.MouseEvent) => {
    // Do not capture click events with modifier keys or non-main buttons.
    if (e.ctrlKey || e.shiftKey || e.metaKey || (e.button && e.button !== 0)) {
      return;
    }

    e.preventDefault();
    navigate(homeUrl);
  };

  // Render differently if custom branding is provided.
  // This will only ever render once, so rendering before hooks is ok.
  if (hasCustomBranding) {
    return (
      <CustomBrandingLink
        href={homeUrl}
        aria-label={gettext('Dashboard')}
        aria-current={currentPath === homeUrl ? 'page' : undefined}
        slim={slim}
        dangerouslySetInnerHTML={{
          __html: brandingLogo ? brandingLogo.innerHTML : '',
        }}
      />
    );
  }

  // Tail wagging
  // If the pointer changes direction 8 or more times without leaving, wag the tail!
  const lastMouseX = React.useRef(0);
  const lastDir = React.useRef<'r' | 'l'>('r');
  const dirChangeCount = React.useRef(0);
  const [isWagging, setIsWagging] = React.useState(false);

  const onMouseMove = (e: React.MouseEvent) => {
    const mouseX = e.pageX;
    const dir: 'r' | 'l' = mouseX > lastMouseX.current ? 'r' : 'l';

    if (mouseX !== lastMouseX.current && dir !== lastDir.current) {
      dirChangeCount.current += 1;
    }

    if (dirChangeCount.current > 8) {
      setIsWagging(true);
    }

    lastMouseX.current = mouseX;
    lastDir.current = dir;
  };

  const onMouseLeave = () => {
    setIsWagging(false);
    dirChangeCount.current = 0;
  };

  return (
    <BrandingLink
      className={tailWagKeyframes}
      href={homeUrl}
      aria-label={gettext('Dashboard')}
      aria-current={currentPath === homeUrl ? 'page' : undefined}
      onClick={onClick}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      slim={slim}
      isWagging={isWagging}
    >
      <IconWrapper slim={slim}>
        <WagtailLogo slim={slim} />
      </IconWrapper>
    </BrandingLink>
  );
}

export class WagtailBrandingModuleDefinition implements ModuleDefinition {
  homeUrl: string;

  constructor(homeUrl: string) {
    this.homeUrl = homeUrl;
  }

  render({ slim, key, navigate, currentPath }) {
    return (
      <WagtailBranding
        key={key}
        homeUrl={this.homeUrl}
        slim={slim}
        navigate={navigate}
        currentPath={currentPath}
      />
    );
  }
}
