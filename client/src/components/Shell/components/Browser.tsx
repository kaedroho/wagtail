import React from 'react';

import { NavigationController } from "../navigation";
import { ContentWrapper } from './ContentWrapper';

export interface BrowserProps {
    navigationController: NavigationController;
}

export const Browser: React.FunctionComponent<BrowserProps> = ({navigationController}) => {
    const {currentFrame, nextFrame, navigate} = navigationController;

    const onLoadNextFrame = (title: string) => {
        navigationController.onLoadNextFrame();
        document.title = title;
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

    return <>{frames}</>;
};
