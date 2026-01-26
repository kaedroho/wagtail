import { useState, useEffect, useCallback } from 'react';
import FocusTrap from 'focus-trap-react';
import { styled } from '@linaria/react';

import { gettext } from '../../utils/gettext';

import LoadingSpinner from '../LoadingSpinner/LoadingSpinner';
import Transition, { PUSH, POP } from '../Transition/Transition';
import PageExplorerHeader from './PageExplorerHeader';
import PageExplorerItem from './PageExplorerItem';
import PageCount from './PageCount';
import { NodesState, PageState } from './types';
import { MAX_EXPLORER_PAGES } from './PageExplorer';

const ExplorerWrapper = styled.div`
  background-color: var(--w-color-surface-menu-item-active);
  max-width: 485px;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  flex: 1;

  *:focus {
    outline: var(--w-color-focus) solid 3px;
    outline-offset: -3px;
  }

  @media (min-width: 640px) {
    width: 485px;
    box-shadow: 2px 2px 5px var(--w-color-black-50);
  }

  > div {
    display: flex;
    flex-direction: column;
    height: 100%;
    z-index: 350;
  }
`;

const Drawer = styled.div`
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
`;

const Placeholder = styled.div`
  padding: 1em;
  color: var(--w-color-text-label-menus-default);

  @media (min-width: 640px) {
    padding: 1em 1.75em;
  }
`;

interface PageExplorerPanelProps {
  nodes: NodesState;
  depth: number;
  page: PageState;
  onClose(): void;
  gotoPage(id: number, transition: number): void;
  navigate(url: string): Promise<void>;
}

export default function PageExplorerPanel({
  nodes,
  depth,
  page,
  onClose,
  gotoPage,
  navigate,
}: PageExplorerPanelProps) {
  const [transition, setTransition] = useState<typeof PUSH | typeof POP>(PUSH);
  const [prevDepth, setPrevDepth] = useState(depth);

  useEffect(() => {
    if (depth !== prevDepth) {
      setTransition(depth > prevDepth ? PUSH : POP);
      setPrevDepth(depth);
    }
  }, [depth, prevDepth]);

  const onItemClick = useCallback(
    (id: number, e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      gotoPage(id, 1);
    },
    [gotoPage],
  );

  const onHeaderClick = useCallback(
    (e: React.MouseEvent) => {
      const parent = page.meta.parent?.id;

      if (depth > 0 && parent) {
        e.preventDefault();
        e.stopPropagation();
        gotoPage(parent, -1);
      }
    },
    [page, depth, gotoPage],
  );

  const renderChildren = () => {
    let children;

    if (!page.isFetchingChildren && !page.children.items) {
      children = <Placeholder key="empty">{gettext('No results')}</Placeholder>;
    } else {
      children = (
        <div key="children">
          {page.children.items.map((id) => (
            <PageExplorerItem
              key={id}
              item={nodes[id]}
              onClick={(e) => onItemClick(id, e)}
              navigate={navigate}
            />
          ))}
        </div>
      );
    }

    return (
      <Drawer>
        {children}
        {page.isFetchingChildren || page.isFetchingTranslations ? (
          <Placeholder key="fetching">
            <LoadingSpinner />
          </Placeholder>
        ) : null}
        {page.isError ? (
          <Placeholder key="error">{gettext('Server Error')}</Placeholder>
        ) : null}
      </Drawer>
    );
  };

  return (
    /*<FocusTrap
      paused={!page || page.isFetchingChildren || page.isFetchingTranslations}
      focusTrapOptions={{
        onDeactivate: onClose,
        clickOutsideDeactivates: false,
        allowOutsideClick: true,
      }}
    >*/
    <div role="dialog" aria-label={gettext('Page explorer')}>
      <ExplorerWrapper>
        <Transition name={transition}>
          <div key={depth}>
            <PageExplorerHeader
              depth={depth}
              page={page}
              onClick={onHeaderClick}
              gotoPage={gotoPage}
              navigate={navigate}
            />

            {renderChildren()}

            {page.isError ||
            (page.children.items &&
              page.children.count > MAX_EXPLORER_PAGES) ? (
              <PageCount page={page} />
            ) : null}
          </div>
        </Transition>
      </ExplorerWrapper>
    </div>
    /*</FocusTrap>*/
  );
}
