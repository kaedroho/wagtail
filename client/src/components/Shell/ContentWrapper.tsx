import React from 'react';

interface ContentWrapperProps {
    contentElement: HTMLElement;
}

export const ContentWrapper: React.FunctionComponent<ContentWrapperProps> = ({contentElement}) => {
    const nodeRef = React.useRef<HTMLDivElement | null>(null);

    React.useEffect(() => {
        if (nodeRef.current) {
            nodeRef.current.appendChild(contentElement);
        }
    }, [nodeRef]);

    return (
        <div ref={nodeRef}></div>
    );
}
