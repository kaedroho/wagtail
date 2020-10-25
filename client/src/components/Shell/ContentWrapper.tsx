import React, { useEffect } from 'react';
import Frame from 'react-frame-component';

export function fetchTemplate(): Promise<string> {
    return fetch('/admin/shell/template/').then(response => response.text());
}


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
    content: string;
    css: string;
    js: string;
    navigate(url: string): void;
}

export const ContentWrapper: React.FunctionComponent<ContentWrapperProps> = ({content, navigate}) => {
    const contentNodeRef = React.useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (contentNodeRef.current) {
            ajaxifyLinks(contentNodeRef.current, navigate);
        }
    }, [contentNodeRef, content]);

    const [template, setTemplate] = React.useState<string | null>(null);

    React.useEffect(() => {
        fetchTemplate().then(setTemplate);
    }, []);

    if (template == null) {
        return (
            <h1>Loading</h1>
        );
    }

    return (
        <Frame
            style={{
                display: 'block',
                overflow: 'scroll',
                border: 0,
                width: 'calc(100% - 200px)',
                height: '100%',
                position: 'absolute',
                top: 0,
                left: 200,
            }}
        >
            <div ref={contentNodeRef} dangerouslySetInnerHTML={{__html: template}} />
        </Frame>
    );
}
