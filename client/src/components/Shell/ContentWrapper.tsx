import React from 'react';


interface ContentWrapperProps {
    html: string;
    navigate(url: string): void;
}

export const ContentWrapper: React.FunctionComponent<ContentWrapperProps> = ({html}) => {
    // Insert a <base target="_parent"> tag into the <head> of the iframe
    // This makes it open all links in the main window
    const onIframeLoad = (e: React.SyntheticEvent<HTMLIFrameElement>) => {
        if (e.target instanceof HTMLIFrameElement && e.target.contentDocument) {
            const baseElement = e.target.contentDocument.createElement('base');
            baseElement.target = '_parent';
            e.target.contentDocument.head.appendChild(baseElement);
        }
    };

    return (
        <iframe onLoad={onIframeLoad} style={{
            display: 'block',
            overflow: 'scroll',
            border: 0,
            width: 'calc(100% - 200px)',
            height: '100%',
            position: 'absolute',
            top: 0,
            left: 200,
        }} srcDoc={html} />
    );
}
