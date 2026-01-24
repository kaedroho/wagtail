import * as React from 'react';
import { styled } from '@linaria/react';

const IconSVG = styled.svg`
  fill: currentColor;
`;

// TODO: move to a common styles library
const ScreenReaderOnly = styled.span`
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
`;

export interface IconProps extends React.SVGProps<SVGSVGElement> {
  /** Optional svg `path` instead of the `use` based on the icon name. */
  children?: React.ReactNode;
  className?: string;
  name: string;
  title?: string;
}

/**
 * Provide a `title` as an accessible label intended for screen readers.
 */
const Icon: React.FunctionComponent<IconProps> = ({
  children,
  className,
  name,
  title,
  ...props
}) => (
  <>
    <IconSVG
      {...props}
      className={['icon', `icon-${name}`, className || '']
        .filter(Boolean)
        .join(' ')}
      aria-hidden="true"
    >
      {children || <use href={`#icon-${name}`} />}
    </IconSVG>
    {title && <ScreenReaderOnly>{title}</ScreenReaderOnly>}
  </>
);

export default Icon;
