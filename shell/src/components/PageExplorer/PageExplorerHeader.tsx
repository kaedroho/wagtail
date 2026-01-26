import { useContext } from 'react';
import { styled } from '@linaria/react';

import { gettext } from '../../utils/gettext';
import Link from '../Link/Link';
import Icon from '../Icon/Icon';
import { PageState } from './types';
import { LocalesContext, UrlsContext } from '../../contexts';

const HeaderWrapper = styled.div`
  background-color: var(--w-color-surface-menu-item-active);
  color: var(--w-color-text-label-menus-default);
  border-bottom: 1px solid var(--w-color-surface-menus);
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  margin-inline-start: 50px;
  height: 50px;

  @media (min-width: 640px) {
    margin-inline-start: initial;
    height: initial;
  }
`;

const HeaderTitle = styled(Link)`
  color: inherit;

  &:hover,
  &:focus {
    background-color: var(--w-color-surface-menus);
    color: var(--w-color-text-label-menus-active);
  }
`;

const HeaderTitleInner = styled.div`
  display: flex;
  padding: 1em 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  .icon {
    color: var(--w-color-text-label-menus-default);
    margin-inline-end: 0.25rem;
    font-size: 1rem;
  }

  .icon--explorer-header {
    color: var(--w-color-text-label-menus-default);
    margin-right: 0.5rem;
    width: 1.25em;
    height: 1.25em;
    margin-inline-end: 0.25rem;
    vertical-align: text-top;
  }

  @media (min-width: 640px) {
    padding: 1em 1.5em;
  }
`;

const HeaderSelect = styled.div`
  color: var(--w-color-text-label-menus-default);
  background-color: var(--w-color-surface-menus);
  margin-inline-end: 10px;

  > select {
    padding: 5px 30px 5px 10px;
    font-size: 0.875rem;

    &:disabled {
      border: 0;
    }

    &:hover:enabled {
      cursor: pointer;
    }

    &:hover:disabled {
      color: inherit;
      background-color: inherit;
      cursor: inherit;
    }
  }
`;

interface SelectLocaleProps {
  locale?: string;
  translations: Map<string, number>;
  gotoPage(id: number, transition: number): void;
}

function SelectLocale({ locale, translations, gotoPage }: SelectLocaleProps) {
  const locales = useContext(LocalesContext);

  const options = locales
    .filter(({ code }) => code === locale || translations.get(code))
    .map(({ code, display_name }) => (
      <option key={code} value={code}>
        {display_name}
      </option>
    ));

  function onChange(e: React.ChangeEvent<HTMLSelectElement>) {
    e.preventDefault();
    const translation = translations.get(e.target.value);
    if (translation) {
      gotoPage(translation, 0);
    }
  }

  return (
    <HeaderSelect>
      <select value={locale} onChange={onChange} disabled={options.length < 2}>
        {options}
      </select>
    </HeaderSelect>
  );
}

interface PageExplorerHeaderProps {
  page: PageState;
  depth: number;
  onClick(e: React.MouseEvent): void;
  gotoPage(id: number, transition: number): void;
  navigate(url: string): Promise<void>;
}

/**
 * The bar at the top of the explorer, displaying the current level
 * and allowing access back to the parent level.
 */
export default function PageExplorerHeader({
  page,
  depth,
  onClick,
  gotoPage,
  navigate,
}: PageExplorerHeaderProps) {
  const urls = useContext(UrlsContext);
  const isRoot = depth === 0;
  const isSiteRoot = page.id === 0;

  return (
    <HeaderWrapper>
      <HeaderTitle
        href={!isSiteRoot ? `${urls.pages}${page.id}/` : urls.pages}
        onClick={onClick}
        navigate={navigate}
      >
        <HeaderTitleInner>
          <Icon
            name={isRoot ? 'home' : 'arrow-left'}
            className="icon--explorer-header"
          />
          <span>{page.admin_display_title || gettext('Pages')}</span>
        </HeaderTitleInner>
      </HeaderTitle>
      {!isSiteRoot &&
        page.meta.locale &&
        page.translations &&
        page.translations.size > 0 && (
          <SelectLocale
            locale={page.meta.locale}
            translations={page.translations}
            gotoPage={gotoPage}
          />
        )}
    </HeaderWrapper>
  );
}
