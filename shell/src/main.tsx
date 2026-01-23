import React from 'react';
import ReactDOM from 'react-dom/client';
import * as DjangoBridge from '@django-bridge/react';

import HTMLPageView from './views/HTMLPage';
import { ActionMenuItemDefinition } from './components/Sidebar/menu/ActionMenuItem';
import { LinkMenuItemDefinition } from './components/Sidebar/menu/LinkMenuItem';
import { SubMenuItemDefinition } from './components/Sidebar/menu/SubMenuItem';
import { PageExplorerMenuItemDefinition } from './components/Sidebar/menu/PageExplorerMenuItem';
import { WagtailBrandingModuleDefinition } from './components/Sidebar/modules/WagtailBranding';
import { SearchModuleDefinition } from './components/Sidebar/modules/Search';
import { MainMenuModuleDefinition } from './components/Sidebar/modules/MainMenu';
import {
  AdminApiConfigContext,
  CsrfTokenContext,
  LocalesContext,
  SidebarContext,
  UrlsContext,
} from './contexts';

import './normalize.css';

const config = new DjangoBridge.Config();

config.addView('HTMLPage', HTMLPageView);

config.addContextProvider('csrf_token', CsrfTokenContext);
config.addContextProvider('urls', UrlsContext);
config.addContextProvider('locales', LocalesContext);
config.addContextProvider('admin_api', AdminApiConfigContext);
config.addContextProvider('sidebar', SidebarContext);

config.addAdapter('wagtail.sidebar.ActionMenuItem', ActionMenuItemDefinition);
config.addAdapter('wagtail.sidebar.LinkMenuItem', LinkMenuItemDefinition);
config.addAdapter('wagtail.sidebar.SubMenuItem', SubMenuItemDefinition);
config.addAdapter(
  'wagtail.sidebar.PageExplorerMenuItem',
  PageExplorerMenuItemDefinition,
);

config.addAdapter(
  'wagtail.sidebar.WagtailBrandingModule',
  WagtailBrandingModuleDefinition,
);
config.addAdapter('wagtail.sidebar.SearchModule', SearchModuleDefinition);
config.addAdapter('wagtail.sidebar.MainMenuModule', MainMenuModuleDefinition);

const rootElement = document.getElementById('root')!;
const initialResponse = JSON.parse(
  document.getElementById('initial-response')!.textContent!,
);

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <DjangoBridge.App config={config} initialResponse={initialResponse} />
  </React.StrictMode>,
);
