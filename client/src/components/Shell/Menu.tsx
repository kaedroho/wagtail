import React from 'react';
import { initExplorer } from '../Explorer';
import Icon from '../Icon/Icon';
import { ExplorerContext, gettext, url } from './Shell';

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
}

const ExplorerMenuItem: React.FunctionComponent<MenuItemProps> = ({data}) => {
    const classNames = ['menu-item'];

    if (data.active) {
        classNames.push('menu-active');
    }

    const context = React.useContext(ExplorerContext);
    console.log(context);
    const toggleRef = React.useRef<HTMLAnchorElement | null>(null);
    React.useEffect(() => {
        if (context?.wrapperRef?.current && toggleRef.current) {
            initExplorer(context.wrapperRef.current, toggleRef.current);
        }
    }, [context, context?.wrapperRef, toggleRef]);

    return (
        <li className={classNames.join(' ')}>
            <a href={data.url}
               className={data.classnames} ref={toggleRef} data-explorer-start-page={context.startPageId}>
                {data.icon_name && <Icon name={data.icon_name} className="icon--menuitem"/>}
                {data.label}
            </a>
        </li>
    );
}

const MenuItem: React.FunctionComponent<MenuItemProps> = ({data}) => {
    const classNames = ['menu-item'];

    if (data.active) {
        classNames.push('menu-active');
    }

    // Special case: Page explorer
    if (data.name === 'explorer') {
        return <ExplorerMenuItem data={data} />
    }

    return (
        <li className={classNames.join(' ')}>
            <a href={data.url}
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
}

const MenuGroup: React.FunctionComponent<MenuGroupProps> = ({data, items}) => {
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
                    {renderMenuItems(items)}
                </ul>
            </div>
        </li>
    );
}

function renderMenuItems(menuItems: MenuData) {
    return (
        <>
            {menuItems.map(menuItem => {
                switch (menuItem.type) {
                    case 'group':
                        return <MenuGroup data={menuItem.data} items={menuItem.items} />;
                    case 'item':
                        return <MenuItem data={menuItem.data} />;
                }
            })}
        </>
    )
}

interface MenuProps {
    menuItems: MenuData;
}

export const Menu: React.FunctionComponent<MenuProps> = ({menuItems}) => {
    return (
        <nav className="nav-main">
            <ul>
                {renderMenuItems(menuItems)}

                <li className="footer" id="footer">
                    <div className="account" id="account-settings" title={gettext('Edit your account')}>
                        <span className="avatar square avatar-on-dark">
                            <img src={url('avatar_url')} alt="" />
                        </span>
                        <em className="icon icon-arrow-up-after">Karl</em>
                    </div>

                    <ul className="footer-submenu">
                        <li><a href="{% url 'wagtailadmin_account' %}" className="icon icon-user">{gettext('Account settings')}</a></li>
                        <li><a href="{% url 'wagtailadmin_logout' %}" className="icon icon-logout">{gettext('Log out')}</a></li>
                    </ul>
                </li>
            </ul>
        </nav>
    );
}
