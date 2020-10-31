import React from 'react';
import { Button } from '../..';
import { initExplorer } from '../Explorer';
import Icon from '../Icon/Icon';
import { ExplorerContext, gettext, ShellProps } from './Shell';

interface MenuItemCommon {
    name: string;
    url: string;
    classnames: string;
    icon_name: string;
    attr_string: string;
    label: string;
    active: boolean;
}

interface MenuItem {
    type: 'item',
    data: MenuItemCommon;
}

interface MenuGroup {
    type: 'group',
    data: MenuItemCommon;
    items: MenuData;
}

type MenuData = (MenuItem | MenuGroup)[];

interface MenuItemProps {
    data: MenuItemCommon;
    navigate(url: string): void;
}

const ExplorerMenuItem: React.FunctionComponent<MenuItemProps> = ({data, navigate}) => {
    const explorerToggle = React.useRef<((page: number) => void) | null>(null);

    const classNames = ['menu-item'];

    if (data.active) {
        classNames.push('menu-active');
    }

    const context = React.useContext(ExplorerContext);
    React.useEffect(() => {
        if (context?.wrapperRef?.current) {
            explorerToggle.current = initExplorer(context.wrapperRef.current, navigate);
        }
    }, [context, context?.wrapperRef]);

    const onClickExplorer = e => {
        e.preventDefault();

        if (explorerToggle.current) {
            explorerToggle.current(context.startPageId || 1);
        }
    }

    return (
        <li className={classNames.join(' ')}>
              <Button
                dialogTrigger={true}
                onClick={onClickExplorer}
            >
                <Icon name="folder-open-inverse" className="icon--menuitem" />
                    {data.label}
                <Icon name="arrow-right" className="icon--submenu-trigger" />
            </Button>
        </li>
    );
}

const MenuItem: React.FunctionComponent<MenuItemProps> = ({data, navigate}) => {
    const classNames = ['menu-item'];

    if (data.active) {
        classNames.push('menu-active');
    }

    // Special case: Page explorer
    if (data.name === 'explorer') {
        return <ExplorerMenuItem data={data} navigate={navigate} />
    }

    const onClick = (e) => {
        e.preventDefault();
        navigate(data.url);
    }

    return (
        <li className={classNames.join(' ')}>
            <a href="#"
               onClick={onClick}
               className={data.classnames}>
                {data.icon_name && <Icon name={data.icon_name} className="icon--menuitem"/>}
                {data.label}
            </a>
        </li>

    );
}

interface MenuGroupProps {
    data: MenuItemCommon;
    items: MenuData;
    navigate(url: string): void;
}

const MenuGroup: React.FunctionComponent<MenuGroupProps> = ({data, items, navigate}) => {
    const classNames = ['menu-item'];

    if (data.active) {
        classNames.push('menu-active');
    }

    return (
        <li className={classNames.join(' ')}>
            <a href="#" data-nav-primary-submenu-trigger className={data.classnames}>
                {data.icon_name && <Icon name={data.icon_name} className="icon--menuitem"/>}
                {data.label}
                <Icon name="arrow-right" className="icon--submenu-trigger"/>
            </a>
            <div className="nav-submenu">
                <h2 id={`nav-submenu-${data.name}-title`} className={data.classnames}>
                    {data.icon_name && <Icon name={data.icon_name} className="icon--submenu-header"/>}
                    {data.label}
                </h2>
                <ul className="nav-submenu__list" aria-labelledby="nav-submenu-{{ name }}-title">
                    {renderMenuItems(items, navigate)}
                </ul>
            </div>
        </li>
    );
}

function renderMenuItems(menuItems: MenuData, navigate: (url: string) => void) {
    return (
        <>
            {menuItems.map(menuItem => {
                switch (menuItem.type) {
                    case 'group':
                        return <MenuGroup key={menuItem.data.name} data={menuItem.data} items={menuItem.items} navigate={navigate} />;
                    case 'item':
                        return <MenuItem key={menuItem.data.name} data={menuItem.data} navigate={navigate} />;
                }
            })}
        </>
    )
}

interface MenuProps {
    menuItems: MenuData;
    user: ShellProps['user'];
    accountUrl: string;
    logoutUrl: string;
    navigate(url: string): void;
}

export const Menu: React.FunctionComponent<MenuProps> = ({menuItems, user, accountUrl, logoutUrl, navigate}) => {
    const onClickLink = (e: React.MouseEvent<HTMLAnchorElement>) => {
        if (e.target instanceof HTMLAnchorElement) {
            const href = e.target.getAttribute('href');
            if (href && href.startsWith('/')) {
                e.preventDefault();
                navigate(href);
            }
        }
    };

    return (
        <nav className="nav-main">
            <ul>
                {renderMenuItems(menuItems, navigate)}

                <li className="footer" id="footer">
                    <div className="account" id="account-settings" title={gettext('Edit your account')}>
                        <span className="avatar square avatar-on-dark">
                            <img src={user.avatarUrl} alt="" />
                        </span>
                        <em className="icon icon-arrow-up-after">{user.name}</em>
                    </div>

                    <ul className="footer-submenu">
                        <li><a href={accountUrl} onClick={onClickLink} className="icon icon-user">{gettext('Account settings')}</a></li>
                        <li><a href={logoutUrl} onClick={onClickLink} className="icon icon-logout">{gettext('Log out')}</a></li>
                    </ul>
                </li>
            </ul>
        </nav>
    );
}
