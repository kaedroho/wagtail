import React, { MutableRefObject } from 'react';
import ReactDOM from 'react-dom';

import {Logo, LogoImages} from './Logo';
import {SearchInput} from './SearchInput';
import {Menu} from './Menu';
import {ContentWrapper} from './ContentWrapper';
import {shellFetch} from './navigator';

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
    homeUrl: string;
    logoImages: LogoImages
    explorerStartPageId: number | null;
    searchUrl: string;
    menuItems: any;
    contentElement: HTMLScriptElement;
}

function htmlDecode(input: string): string {
    var e = document.createElement('div');
    e.innerHTML = input;
    return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue || "";
}

const Shell: React.FunctionComponent<ShellProps> = ({homeUrl, logoImages, explorerStartPageId, searchUrl, menuItems, contentElement}) => {
    const explorerWrapperRef = React.useRef<HTMLDivElement | null>(null);
    const [html, setHtml] = React.useState(htmlDecode(contentElement.innerHTML));

    // These two need to be globally mutable and not trigger UI refreshes on update
    // If two requests are fired off at around the same time, this makes sure the later
    // always takes precedence over the earlier one
    const nextFetchId = React.useRef(1);
    const lastReceivedFetchId = React.useRef(0);

    const navigate = (url: string, pushState: boolean = true) => {
        // Get a fetch ID
        // We do this so that if responses come back in a different order to
        // when the requests were sent, the older requests don't replace newer ones
        let thisFetchId = nextFetchId.current++;

        shellFetch(url).then(response => {
            if (thisFetchId < lastReceivedFetchId.current) {
                // A subsequent fetch was made but its response came in before this one
                // So ignore this response
                return;
            }

            lastReceivedFetchId.current = thisFetchId;

            if (response.status == 'load-it') {
                window.location.href = url;
            } else if (response.status == 'render-html') {
                if (pushState) {
                    history.pushState({}, "", url);
                }

                setHtml(response.html);
            }
        });
    }

    // Add listener for popState
    // This event is fired when the user hits the back/forward links in their browser
    React.useEffect(() => {
        window.addEventListener('popstate', () => {
            navigate(document.location.pathname, false);
        });
    }, []);

    return (
        <>
            <aside className="nav-wrapper" data-nav-primary={true}>
                <div className="inner">
                    <Logo images={logoImages} homeUrl={homeUrl} navigate={navigate} />

                    <SearchInput searchUrl={searchUrl} navigate={navigate} />

                    <ExplorerContext.Provider value={{startPageId: explorerStartPageId, wrapperRef: explorerWrapperRef}}>
                        <Menu menuItems={menuItems} navigate={navigate} />
                    </ExplorerContext.Provider>
                </div>
                <div className="explorer__wrapper" ref={explorerWrapperRef}></div>
            </aside>

            <ContentWrapper html={html} navigate={navigate} setTitle={(title: string) => document.title = title} />
        </>
    );
}

export function initShell() {
    const shellElement = document.getElementById('wagtailshell-root');
    const contentElement = document.getElementById('wagtailshell-content');

    if (shellElement instanceof HTMLElement && contentElement instanceof HTMLElement && shellElement.dataset.props) {
        ReactDOM.render(
            <Shell {...JSON.parse(shellElement.dataset.props)} contentElement={contentElement} />,
            shellElement
        )
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initShell();
});
