import React, { MutableRefObject } from 'react';

function ajaxifyLinks(element: HTMLElement, navigate: (url: string) => void) {
    element.querySelectorAll('a').forEach(aTag => {
        const href = aTag.getAttribute('href');
        if (href && href.startsWith('/admin/')) {
            aTag.addEventListener('click', (e) => {
                e.preventDefault();
                navigate(href);
            });
        }
    });
}

interface ContentWrapperProps {
    contentElement: HTMLElement;
    navigate(url: string): void;
    renderHtmlCallback: MutableRefObject<((html: string) => void) | null>;
}

export const ContentWrapper: React.FunctionComponent<ContentWrapperProps> = ({contentElement, navigate, renderHtmlCallback}) => {
    const nodeRef = React.useRef<HTMLDivElement | null>(null);

    renderHtmlCallback.current = (html: string) => {
        if (nodeRef.current) {
            nodeRef.current.innerHTML = html;
            ajaxifyLinks(nodeRef.current, navigate);
        }
    };

    React.useEffect(() => {
        if (nodeRef.current) {
            nodeRef.current.appendChild(contentElement);
            ajaxifyLinks(contentElement, navigate);
        }
    }, [nodeRef]);

    return (
        <div ref={nodeRef}></div>
    );
}
