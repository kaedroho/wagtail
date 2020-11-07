import React, { MutableRefObject } from 'react';
import ReactDOM from 'react-dom';

import {Logo, LogoImages} from './Logo';
import {SearchInput} from './SearchInput';
import {Menu} from './Menu';
import {ContentWrapper} from './ContentWrapper';
import {shellFetch, ShellResponse} from './navigator';

// Just a dummy for now
export const gettext = (text: string) => text;

// A React context to pass some data down to the ExplorerMenuItem component
interface ExplorerContext {
    startPageId: number | null;
    wrapperRef: MutableRefObject<HTMLDivElement | null> | null;
}
export const ExplorerContext = React.createContext<ExplorerContext>({startPageId: null, wrapperRef: null});

export interface ShellProps {
    homeUrl: string;
    logoImages: LogoImages
    explorerStartPageId: number | null;
    searchUrl: string;
    menuItems: any;
    user: {
        name: string;
        avatarUrl: string;
    };
    accountUrl: string;
    logoutUrl: string;
    initialResponse: string;
}

interface SidebarProps extends ShellProps {
    navigate(url: string): void;
}

const Sidebar: React.FunctionComponent<SidebarProps> =  ({homeUrl, logoImages, explorerStartPageId, searchUrl, menuItems, user, accountUrl, logoutUrl, navigate}) => {
    const explorerWrapperRef = React.useRef<HTMLDivElement | null>(null);

    return (
        <aside className="nav-wrapper" data-nav-primary={true}>
            <div className="inner">
                <Logo images={logoImages} homeUrl={homeUrl} navigate={navigate} />

                <SearchInput searchUrl={searchUrl} navigate={navigate} />

                <ExplorerContext.Provider value={{startPageId: explorerStartPageId, wrapperRef: explorerWrapperRef}}>
                    <Menu user={user} accountUrl={accountUrl} logoutUrl={logoutUrl} initialState={menuItems} navigate={navigate} />
                </ExplorerContext.Provider>
            </div>
            <div className="explorer__wrapper" ref={explorerWrapperRef}></div>
        </aside>
    );
};

const Shell: React.FunctionComponent<ShellProps> = (props) => {
    // Need to useRef for these so the values don't get locked in navigate()'s closure
    // TODO: Use a store instead
    const greenUrl = React.useRef(window.location.pathname);
    const blueUrl = React.useRef(window.location.pathname);

    const [greenData, setGreenData] = React.useState<ShellResponse>(JSON.parse(props.initialResponse));
    const [blueData, setBlueData] = React.useState<ShellResponse>({status: 'render-html', html: ''});

    const [currentScreen, setCurrentScreen] = React.useState<'green' | 'blue'>('green');

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

        if (url === greenUrl.current) {
            // TODO: Update document title
            // TODO: Trigger reload?
            setCurrentScreen('green');
            if (pushState) {
                history.pushState({}, "", url);
            }
        } else if (url === blueUrl.current) {
            // TODO: Update document title
            // TODO: Trigger reload?
            setCurrentScreen('blue');
            if (pushState) {
                history.pushState({}, "", url);
            }
        } else {
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

                    if (currentScreen === 'green') {
                        setBlueData(response);
                        blueUrl.current = url;
                    } else {
                        setGreenData(response);
                        greenUrl.current = url;
                    }
                }
            });
        }
    }

    // Add listener for popState
    // This event is fired when the user hits the back/forward links in their browser
    React.useEffect(() => {
        window.addEventListener('popstate', () => {
            navigate(document.location.pathname, false);
        });
    }, []);

    const onContentLoadHandler = (screen: 'green' | 'blue') => {
        return (title: string) => {
            setCurrentScreen(screen);
            document.title = title;
        };
    };

    return (
        <>
            <Sidebar {...props} navigate={navigate} />
            {greenData.status == 'render-html' && <ContentWrapper visible={currentScreen === 'green'} url={greenUrl.current} html={greenData.html} navigate={navigate} onLoad={onContentLoadHandler('green')} />}
            {blueData.status == 'render-html' && <ContentWrapper visible={currentScreen === 'blue'} url={blueUrl.current} html={blueData.html} navigate={navigate} onLoad={onContentLoadHandler('blue')} />}
        </>
    );
}

export function initShell() {
    const shellElement = document.getElementById('wagtailshell-root');
    const sidebarElement = document.getElementById('wagtailshell-sidebar');

    if (shellElement instanceof HTMLElement && sidebarElement instanceof HTMLElement && sidebarElement.dataset.props) {
        if (shellElement.dataset.initialResponse) {
            ReactDOM.render(
                <Shell {...JSON.parse(sidebarElement.dataset.props)} initialResponse={shellElement.dataset.initialResponse} />,
                shellElement
            );
        } else {
            // Legacy mode
            const navigate = (url: string) => {
                window.location.href = url;
            };

            ReactDOM.render(
                <Sidebar {...JSON.parse(sidebarElement.dataset.props)} navigate={navigate} />,
                sidebarElement
            );
        }
    }
}

if (!parent) {
    document.addEventListener('DOMContentLoaded', () => {
        initShell();
    });
}
