import React from 'react';


interface ContentWrapperProps {
    visible: boolean;
    url: string;
    html: string;
    navigate(url: string): void;
    onLoad(title: string): void;
}

export const ContentWrapper: React.FunctionComponent<ContentWrapperProps> = ({visible, url, html, navigate, onLoad}) => {
    const onIframeLoad = (e: React.SyntheticEvent<HTMLIFrameElement>) => {
        if (e.target instanceof HTMLIFrameElement && e.target.contentDocument) {
            // Insert a <base target="_parent"> tag into the <head> of the iframe
            // This makes it open all links in the main window
            const baseElement = e.target.contentDocument.createElement('base');
            baseElement.target = '_parent';
            e.target.contentDocument.head.appendChild(baseElement);

            // Ajaxify links
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

                    if (href.startsWith('?')) {
                        navigate(document.location.pathname + href);
                    } else {
                        navigate(href);
                    }
                });
            });

            // Ajaxify 'get' forms
            Array.from(e.target.contentDocument.forms).forEach(form => {
                // Don't ajaxify POST forms
                if (form.method.toLowerCase() == 'post') {
                    return;
                }

                // Make sure action is set to something.
                // If it's blank, the browser will try to post the data to 'about:srcdoc' which will result in an error.
                // Note: Don't use form.action here as some forms have an action field!
                const formAction = form.getAttribute('action');
                form.action = formAction || url;
            });

            onLoad(e.target.contentDocument.title);
        }
    };

    return (
        <iframe onLoad={onIframeLoad} style={{
            display: visible ? 'block' : 'none',
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
