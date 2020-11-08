import React, { MutableRefObject } from 'react';
import ReactDOM from 'react-dom';

import {LogoImages} from './components/Logo';
import {ContentWrapper} from './components/ContentWrapper';
import {Sidebar} from './components/Sidebar';

import {shellFetch, ShellResponse} from './fetch';

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

export interface Frame {
    id: number;
    url: string;
    data: ShellResponse;
}

const Shell: React.FunctionComponent<ShellProps> = (props) => {
    const nextFrameId = React.useRef(0);
    const [currentFrame, setCurrentFrame] = React.useState<Frame>({
        id: nextFrameId.current++,
        url: window.location.pathname,
        data: JSON.parse(props.initialResponse),
    });
    const [nextFrame, setNextFrame] = React.useState<Frame | null>(null);

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

                setNextFrame({
                    id: nextFrameId.current++,
                    url,
                    data: response,
                });
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

    const onLoadNextFrame = (title: string) => {
        if (nextFrame) {
            setCurrentFrame(nextFrame);
            setNextFrame(null);
            document.title = title;
        }
    };

    let frames: React.ReactNode[] = [];
    frames.push(
        <ContentWrapper
            key={currentFrame.id}
            visible={true}
            frame={currentFrame}
            navigate={navigate}
        />
    );

    if (nextFrame) {
        frames.push(
            <ContentWrapper
                key={nextFrame.id}
                visible={false}
                frame={nextFrame}
                navigate={navigate}
                onLoad={onLoadNextFrame}
            />
        );
    }

    return (
        <>
            <Sidebar {...props} navigate={navigate} />
            {frames}
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
