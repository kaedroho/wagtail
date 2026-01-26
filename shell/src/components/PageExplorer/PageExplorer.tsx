import { useState, useCallback, useContext, useEffect } from 'react';

import * as admin from '../../api/admin';
import { AdminApiConfigContext } from '../../contexts';
import { PageState, NodesState, defaultPageState } from './types';
import PageExplorerPanel from './PageExplorerPanel';

export const MAX_EXPLORER_PAGES = 200;

interface PageExplorerProps {
  isVisible: boolean;
  startPageId: number;
  onClose(): void;
  navigate(url: string): Promise<void>;
}

export default function PageExplorer({
  isVisible,
  startPageId,
  onClose,
  navigate,
}: PageExplorerProps) {
  const adminApi = useContext(AdminApiConfigContext);

  const [depth, setDepth] = useState(0);
  const [currentPageId, setCurrentPageId] = useState<number | null>(null);
  const [nodes, setNodes] = useState<NodesState>({});

  const updateNode = useCallback((id: number, updates: Partial<PageState>) => {
    setNodes((prev) => ({
      ...prev,
      [id]: { ...prev[id], ...updates },
    }));
  }, []);

  const getPage = useCallback(
    async (id: number) => {
      try {
        const data = await admin.getPage(adminApi, id);
        updateNode(id, { ...data, isError: false });
      } catch {
        updateNode(id, { isError: true });
      }
    },
    [adminApi, updateNode],
  );

  const getChildren = useCallback(
    async (id: number, offset = 0) => {
      updateNode(id, { isFetchingChildren: true });

      try {
        const { items, meta } = await admin.getPageChildren(adminApi, id, {
          offset,
        });

        setNodes((prev) => {
          const currentNode = prev[id] || { ...defaultPageState };
          const newNodes = { ...prev };

          newNodes[id] = {
            ...currentNode,
            isFetchingChildren: false,
            isError: false,
            children: {
              items: currentNode.children.items.concat(
                items.map((item) => item.id),
              ),
              count: meta.total_count,
            },
          };

          items.forEach((item) => {
            newNodes[item.id] = { ...defaultPageState, ...item };
          });

          return newNodes;
        });

        const nbPages = offset + items.length;
        if (nbPages < meta.total_count && nbPages < MAX_EXPLORER_PAGES) {
          getChildren(id, nbPages);
        }
      } catch {
        updateNode(id, {
          isFetchingChildren: false,
          isError: true,
        });
      }
    },
    [adminApi, updateNode],
  );

  const getTranslations = useCallback(
    async (id: number) => {
      updateNode(id, { isFetchingTranslations: true });

      try {
        const items = await admin.getAllPageTranslations(adminApi, id, {
          onlyWithChildren: true,
        });

        const translations = new Map<string, number>();
        items.forEach((item) => {
          if (item.meta.locale) {
            translations.set(item.meta.locale, item.id);
          }
        });

        setNodes((prev) => {
          const newNodes = { ...prev };

          newNodes[id] = {
            ...newNodes[id],
            isFetchingTranslations: false,
            isError: false,
            translations,
          };

          items.forEach((item) => {
            newNodes[item.id] = { ...defaultPageState, ...item };
          });

          return newNodes;
        });
      } catch {
        updateNode(id, {
          isFetchingTranslations: false,
          isError: true,
        });
      }
    },
    [adminApi, updateNode],
  );

  const openExplorer = useCallback(
    (id: number) => {
      setDepth(0);
      setCurrentPageId(id);

      setNodes((prev) => ({
        ...prev,
        [id]: { ...defaultPageState },
      }));

      getChildren(id);

      if (id !== 1) {
        getTranslations(id);
        getPage(id);
      }
    },
    [getChildren, getTranslations, getPage],
  );

  const closeExplorer = useCallback(() => {
    setDepth(0);
    setCurrentPageId(null);
    setNodes({});
  }, []);

  const gotoPage = useCallback(
    (id: number, transition: number) => {
      setDepth((prev) => prev + transition);
      setCurrentPageId(id);

      const page = nodes[id];

      if (page && !page.isFetchingChildren && !(page.children.count > 0)) {
        getChildren(id);
      }

      if (page && !page.isFetchingTranslations && page.translations == null) {
        getTranslations(id);
      }
    },
    [nodes, getChildren, getTranslations],
  );

  useEffect(() => {
    if (isVisible) {
      openExplorer(startPageId);
    } else {
      closeExplorer();
    }
  }, [isVisible, startPageId, openExplorer, closeExplorer]);

  if (!isVisible || !currentPageId || !nodes[currentPageId]) {
    return null;
  }

  return (
    <PageExplorerPanel
      depth={depth}
      page={nodes[currentPageId]}
      nodes={nodes}
      gotoPage={gotoPage}
      onClose={onClose}
      navigate={navigate}
    />
  );
}
