import React from 'react';

import {gettext, url} from './Shell';

export interface LogoImages {
    mobileLogo: string;
    desktopLogoBody: string
    desktopLogoTail: string;
    desktopLogoEyeOpen: string;
    desktopLogoEyeClosed: string;
}

interface LogoProps {
    images: LogoImages;
}

export const Logo: React.FunctionComponent<LogoProps> = ({images}) => {
    return (
        <a href={url('wagtailadmin_home')} className="logo" aria-label={gettext('Dashboard')}>
            {/* Mobile */}
            <div className="wagtail-logo-container__mobile u-hidden@sm">
                <img className="wagtail-logo wagtail-logo__full" src={images.mobileLogo} alt="" width="80" />
            </div>

            {/* Desktop (animated) */}
            <div className="wagtail-logo-container__desktop u-hidden@xs" data-animated-logo-container>
                <div className="wagtail-logo-container-inner">
                    <img className="wagtail-logo wagtail-logo__body" src={images.desktopLogoBody} alt=""/>
                    <img className="wagtail-logo wagtail-logo__tail" src={images.desktopLogoTail} alt="" />
                    <img className="wagtail-logo wagtail-logo__eye--open" src={images.desktopLogoEyeOpen} alt="" />
                    <img className="wagtail-logo wagtail-logo__eye--closed" src={images.desktopLogoEyeClosed} alt="" />
                </div>
            </div>
            <span className="u-hidden@sm">{gettext('Dashboard')}</span>
        </a>
    );
}
