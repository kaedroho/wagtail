import { useContext } from 'react';
import { styled } from '@linaria/react';

import { gettext } from '../../utils/gettext';
import Icon from '../Icon/Icon';
import Link from '../Link/Link';
import PublicationStatus from '../PublicationStatus/PublicationStatus';
import { PageState } from './types';
import { UrlsContext, LocalesContext } from '../../contexts';

const ItemWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  border: 0;
  border-bottom-width: 1px;
  border-style: solid;
  border-color: var(--w-color-surface-menus);

  > * + * {
    border-left: 1px solid var(--w-color-surface-menus);
  }
`;

const ItemLink = styled(Link)`
  display: inline-flex;
  align-items: flex-start;
  flex-wrap: wrap;
  flex-grow: 1;
  cursor: pointer;
  gap: 0.25rem;
  transition:
    background-color 150ms ease,
    color 150ms ease;
  padding: 1.45em 1em;
  color: var(--w-color-text-label-menus-default);

  &:hover,
  &:focus {
    background-color: var(--w-color-surface-menus);
    color: var(--w-color-text-label-menus-active);
  }

  .icon {
    color: var(--w-color-text-label-menus-default);
    width: 2em;
    height: 2em;
    margin-inline-end: 0.75rem;
  }

  @media (min-width: 640px) {
    align-items: center;
    padding: 1.45em 1.75em;
  }
`;

const ItemTitle = styled.h3`
  margin: 0;
  color: var(--w-color-text-label-menus-default);
  display: inline-block;
`;

const ItemAction = styled(Link)<{ small?: boolean }>`
  color: var(--w-color-text-label-menus-default);
  transition:
    background-color 150ms ease,
    color 150ms ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 50px;
  padding: 0 0.5em;
  line-height: 1;
  font-size: ${(props) => (props.small ? '1.2em' : '2em')};
  cursor: pointer;

  &:hover,
  &:focus {
    background-color: var(--w-color-surface-menus);
    color: var(--w-color-text-label-menus-active);
  }

  .icon {
    width: 1em;
    height: 1em;
  }
`;

const MetaWrapper = styled.span`
  display: flex;
  gap: 0.5rem;
  color: var(--w-color-text-label-menus-default);
  font-size: 12px;
`;

// Hoist icons in the explorer item, as it is re-rendered many times.
const childrenIcon = <Icon name="folder-inverse" className="icon--menuitem" />;

interface PageExplorerItemProps {
  item: PageState;
  onClick(e: React.MouseEvent): void;
  navigate(url: string): Promise<void>;
}

/**
 * One menu item in the page explorer, with different available actions
 * and information depending on the metadata of the page.
 */
export default function PageExplorerItem({
  item,
  onClick,
  navigate,
}: PageExplorerItemProps) {
  const urls = useContext(UrlsContext);
  const locales = useContext(LocalesContext);
  const { id, admin_display_title: title, meta } = item;
  const hasChildren = meta.children.count > 0;
  const isPublished = meta.status.live && !meta.status.has_unpublished_changes;
  const localeName =
    meta.parent?.id === 1 &&
    meta.locale &&
    (locales.get(meta.locale)?.name || meta.locale);

  return (
    <ItemWrapper>
      <ItemLink href={`${urls.pages}${id}/`} navigate={navigate}>
        {hasChildren ? childrenIcon : null}
        <ItemTitle>{title}</ItemTitle>

        {(!isPublished || localeName) && (
          <MetaWrapper>
            {localeName && <span className="c-status">{localeName}</span>}
            {!isPublished && <PublicationStatus status={meta.status} />}
          </MetaWrapper>
        )}
      </ItemLink>
      <ItemAction
        href={`${urls.pages}${id}/edit/`}
        navigate={navigate}
        small
      >
        <Icon
          name="edit"
          title={gettext("Edit '%(title)s'").replace('%(title)s', title || '')}
        />
      </ItemAction>
      {hasChildren ? (
        <ItemAction onClick={onClick} href={`${urls.pages}${id}/`} navigate={navigate}>
          <Icon
            name="arrow-right"
            title={gettext("View child pages of '%(title)s'").replace(
              '%(title)s',
              title || '',
            )}
          />
        </ItemAction>
      ) : null}
    </ItemWrapper>
  );
}
