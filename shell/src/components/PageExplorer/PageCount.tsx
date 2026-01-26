import { useContext } from 'react';
import { styled } from '@linaria/react';

import { gettext } from '../../utils/gettext';
import Icon from '../Icon/Icon';
import { UrlsContext } from '../../contexts';

const SeeMoreLink = styled.a`
  display: block;
  padding: 1em;
  background: var(--w-color-black-35);
  color: var(--w-color-text-label-menus-default);

  &:focus {
    color: var(--w-color-text-label-menus-active);
    background: var(--w-color-black-50);
  }

  &:hover {
    color: var(--w-color-text-label-menus-active);
    background: var(--w-color-black-50);
  }

  @media (min-width: 640px) {
    padding: 1em 1.75em;
    height: 50px;
  }
`;

interface PageCountProps {
  page: {
    id: number;
    children: {
      count: number;
    };
  };
}

export default function PageCount({ page }: PageCountProps) {
  const urls = useContext(UrlsContext);
  const count = page.children.count;

  return (
    <SeeMoreLink href={`${urls.pages}${page.id}/`}>
      {gettext('See all')}
      <span>{` ${count} ${
        count === 1
          ? gettext('Page').toLowerCase()
          : gettext('Pages').toLowerCase()
      }`}</span>
      <Icon name="arrow-right" />
    </SeeMoreLink>
  );
}
