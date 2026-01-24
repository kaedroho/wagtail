import * as React from 'react';
import { styled } from '@linaria/react';

import Tippy from '@tippyjs/react';
import { gettext } from '../../../utils/gettext';
import Icon from '../../Icon/Icon';
import { ModuleDefinition, SIDEBAR_TRANSITION_DURATION } from '../Sidebar';

const SearchForm = styled.form`
  height: 42px;
  position: relative;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;
  flex-shrink: 0;
`;

const SearchInner = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 100%;
`;

interface SearchButtonProps {
  slim: boolean;
}

const SearchButton = styled.button<SearchButtonProps>`
  width: 100%;
  padding-left: 23px;
  padding-right: ${(props) => (props.slim ? '18px' : '0')};
  height: 35px;
  background: transparent;
  border: 0;
  border-radius: 0;
  color: rgba(255, 255, 255, 0.8);
  z-index: 10;
  cursor: pointer;

  // Centre the icon
  svg {
    transform: translateX(-3px) translateY(4px);
  }

  &:hover,
  &:focus {
    color: white;
    background: transparent;
  }

  &:focus {
    outline: 2px solid #00b0b1;
    outline-offset: -2px;
  }
`;

interface SearchInputProps {
  isHidden: boolean;
}

const SearchInputField = styled.input<SearchInputProps>`
  transition: opacity var(--sidebar-transition-duration) ease-in-out;
  opacity: ${(props) => (props.isHidden ? '0' : '1')};
  padding-left: 51px;
  padding-top: 15px;
  padding-bottom: 13px;
  -webkit-font-smoothing: subpixel-antialiased;
  position: absolute;
  left: 0;
  top: 0;
  font-weight: 400;
  font-size: 0.875rem;
  background: transparent;
  border: 0;
  border-radius: 0;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1;
  width: 100%;

  &:focus {
    outline: 2px solid #00b0b1;
    outline-offset: -2px;
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.8);
  }
`;

const ScreenReaderLabel = styled.label`
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

interface SearchInputProps {
  slim: boolean;
  expandingOrCollapsing: boolean;
  onSearchClick: () => void;
  searchUrl: string;
  navigate(url: string): void;
}

export function SearchInput({
  slim,
  expandingOrCollapsing,
  onSearchClick,
  searchUrl,
  navigate,
}: SearchInputProps) {
  const isVisible = !slim || expandingOrCollapsing;
  const searchInput = React.useRef<HTMLInputElement>(null);

  const onSubmitForm = (e: React.FormEvent<HTMLFormElement>) => {
    if (e.target instanceof HTMLFormElement) {
      e.preventDefault();

      if (isVisible) {
        const inputElement = e.target.querySelector(
          'input[name="q"]',
        ) as HTMLInputElement;
        navigate(searchUrl + '?q=' + encodeURIComponent(inputElement.value));
      } else {
        navigate(searchUrl);
      }
    }
  };

  return (
    <SearchForm
      role="search"
      action={searchUrl}
      aria-keyshortcuts="/"
      method="get"
      onSubmit={onSubmitForm}
    >
      <SearchInner>
        <Tippy
          disabled={isVisible || !slim}
          content={gettext('Search')}
          placement="right"
        >
          <SearchButton
            slim={slim}
            type="submit"
            aria-label={gettext('Search')}
            onClick={(e) => {
              if (slim) {
                e.preventDefault();
                onSearchClick();

                // Focus search input after transition when button is clicked in slim mode
                setTimeout(() => {
                  if (searchInput.current) {
                    searchInput.current.focus();
                  }
                }, SIDEBAR_TRANSITION_DURATION);
              }
            }}
          >
            <Icon className="icon--menuitem" name="search" />
          </SearchButton>
        </Tippy>

        <ScreenReaderLabel htmlFor="menu-search-q">
          {gettext('Search')}
        </ScreenReaderLabel>

        <SearchInputField
          isHidden={slim || !isVisible}
          type="text"
          id="menu-search-q"
          name="q"
          placeholder={gettext('Search')}
          ref={searchInput}
        />
      </SearchInner>
    </SearchForm>
  );
}

export class SearchModuleDefinition implements ModuleDefinition {
  searchUrl: string;

  constructor(searchUrl: string) {
    this.searchUrl = searchUrl;
  }

  render({ slim, key, expandingOrCollapsing, onSearchClick, navigate }) {
    return (
      <SearchInput
        searchUrl={this.searchUrl}
        slim={slim}
        key={key}
        expandingOrCollapsing={expandingOrCollapsing}
        onSearchClick={onSearchClick}
        navigate={navigate}
      />
    );
  }
}
