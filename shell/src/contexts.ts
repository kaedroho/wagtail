import React from 'react';
import { ModuleDefinition } from './components/Sidebar/Sidebar';

export interface Urls {
  pages: string;
}

export interface Locale {
  name: string;
}

export interface AdminApiConfig {
  pagesBaseUrl: string;
  extraChildrenParameters: string;
}

export interface SidebarConfig {
  enabled: boolean;
  collapsed: boolean;
  modules: ModuleDefinition[];
}

export const CsrfTokenContext = React.createContext<string>('');
export const UrlsContext = React.createContext<Urls>({
  pages: '',
});
export const LocalesContext = React.createContext<Locale[]>([]);
export const AdminApiConfigContext = React.createContext<AdminApiConfig>({
  pagesBaseUrl: '',
  extraChildrenParameters: '',
});

export const SidebarContext = React.createContext<SidebarConfig>({
  enabled: false,
  collapsed: false,
  modules: [],
});
