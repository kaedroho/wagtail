import { WagtailPageAPI } from '../../api/admin';

export interface PageState extends WagtailPageAPI {
  isFetchingChildren: boolean;
  isFetchingTranslations: boolean;
  isError: boolean;
  children: {
    items: number[];
    count: number;
  };
  translations?: Map<string, number>;
}

export interface NodesState {
  [id: number]: PageState;
}

export const defaultPageState: PageState = {
  id: 0,
  isFetchingChildren: false,
  isFetchingTranslations: false,
  isError: false,
  children: {
    items: [],
    count: 0,
  },
  meta: {
    status: {
      status: '',
      live: false,
      has_unpublished_changes: true,
    },
    parent: null,
    children: {},
  },
};
