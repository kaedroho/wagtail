import React, { useEffect } from 'react';
import root from 'react-shadow';
import { Stylesheet } from './navigator';

function ajaxifyLinks(element: HTMLElement, navigate: (url: string) => void) {
    element.querySelectorAll('a').forEach(aTag => {
        const href = aTag.getAttribute('href');
        if (href && href.startsWith('/admin/') && !aTag.dataset.ajaxified) {
            aTag.addEventListener('click', (e) => {
                e.preventDefault();
                navigate(href);
            });
            aTag.dataset.ajaxified = 'true';
        }
    });
}

interface ContentWrapperProps {
    html: string;
    stylesheets: Stylesheet[];
    navigate(url: string): void;
}

export const ContentWrapper: React.FunctionComponent<ContentWrapperProps> = ({html, stylesheets, navigate}) => {
    const nodeRef = React.useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (nodeRef.current) {
            ajaxifyLinks(nodeRef.current, navigate);
        }
    }, [nodeRef, html]);

    return (
        <root.div>
            <div ref={nodeRef} dangerouslySetInnerHTML={{__html: html}} />
            {stylesheets.map(stylesheet => <link key={stylesheet.src} rel="stylesheet" type="text/css" href={stylesheet.src} />)}
        </root.div>
    );
}
