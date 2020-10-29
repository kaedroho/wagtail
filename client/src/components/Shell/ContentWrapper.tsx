import React from 'react';


interface ContentWrapperProps {
    html: string;
    navigate(url: string): void;
}

export const ContentWrapper: React.FunctionComponent<ContentWrapperProps> = ({html, navigate}) => {
    // Insert a <base target="_parent"> tag into the <head> of the iframe
    // This makes it open all links in the main window
    const onIframeLoad = (e: React.SyntheticEvent<HTMLIFrameElement>) => {
        if (e.target instanceof HTMLIFrameElement && e.target.contentDocument) {
            const baseElement = e.target.contentDocument.createElement('base');
            baseElement.target = '_parent';
            e.target.contentDocument.head.appendChild(baseElement);

            Array.from(e.target.contentDocument.links).forEach(link => {
                // Don't ajaxify download links
                if (link.hasAttribute('download')) {
                    return
                }

                // Get href
                const href = link.getAttribute('href');
                if (!href || href.startsWith('#')) {
                    return;
                }

                link.addEventListener('click', (e: MouseEvent) => {
                    e.preventDefault();
                    navigate(href);
                });
            });
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
