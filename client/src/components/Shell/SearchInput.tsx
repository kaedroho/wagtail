import React from 'react';
import { gettext } from './Shell';

interface SearchInputProps {
    searchUrl: string;
}

export const SearchInput: React.FunctionComponent<SearchInputProps> = ({searchUrl}) => {
    return (
        <form className="nav-search" action={searchUrl} method="get">
            <div>
                <label htmlFor="menu-search-q">{gettext('Search')}</label>
                <input type="text" id="menu-search-q" name="q" placeholder={gettext('Search')} />
                <button className="button" type="submit">{gettext('Search')}</button>
            </div>
        </form>
    );
}
