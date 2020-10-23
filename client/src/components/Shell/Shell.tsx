import React, { MutableRefObject } from 'react';
import ReactDOM from 'react-dom';

import {Logo, LogoImages} from './Logo';
import {SearchInput} from './SearchInput';
import {Menu} from './Menu';
import {ContentWrapper} from './ContentWrapper';

// Just a dummy for now
export const gettext = (text: string) => text;

export const url = (_name: string) => '/';

// A React context to pass some data down to the ExplorerMenuItem component
interface ExplorerContext {
    startPageId: number | null;
    wrapperRef: MutableRefObject<HTMLDivElement | null> | null;
}
export const ExplorerContext = React.createContext<ExplorerContext>({startPageId: null, wrapperRef: null});

interface ShellProps {
    logoImages: LogoImages
    explorerStartPageId: number | null;
    searchUrl: string;
    menuItems: any;
}

const Shell: React.FunctionComponent<ShellProps> = ({logoImages, explorerStartPageId, searchUrl, menuItems, children}) => {
    const explorerWrapperRef = React.useRef<HTMLDivElement | null>(null);

    return (
        <>
            <aside className="nav-wrapper" data-nav-primary={true}>
                <div className="inner">
                    <Logo images={logoImages} />

                    <SearchInput searchUrl={searchUrl} />

                    <ExplorerContext.Provider value={{startPageId: explorerStartPageId, wrapperRef: explorerWrapperRef}}>
                        <Menu menuItems={menuItems} />
                    </ExplorerContext.Provider>
                </div>
                <div className="explorer__wrapper" ref={explorerWrapperRef}></div>
            </aside>

            <main className="content-wrapper" role="main" id="main">
                <div className="content">
                    {/* Always show messages div so it can be appended to by JS */}

                    <div id="nav-toggle" className="nav-toggle icon text-replace">{gettext('Menu')}</div>

                    {children}
                </div>
            </main>
        </>
    );
}

export function initShell() {
    const shellElement = document.querySelector('.js-shell');
    const contentElement = shellElement?.querySelector('.js-content');

    if (shellElement instanceof HTMLElement && contentElement instanceof HTMLElement && shellElement.dataset.props) {
        ReactDOM.render(
            <Shell {...JSON.parse(shellElement.dataset.props)}>
                <ContentWrapper contentElement={contentElement} />
            </Shell>,
            shellElement
        )
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initShell();
});
