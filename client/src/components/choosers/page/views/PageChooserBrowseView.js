import React from 'react';

import PageChooserResultSet from '../PageChooserResultSet';


export default class PageChooserBrowseView extends React.Component {
    render() {
        return <div className="nice-padding">
            <p className="link-types">
                <b>Internal link</b> | <a href="/admin/choose-external-link/?parent_page_id=1&amp;allow_external_link=true&amp;allow_email_link=true">External link</a> | <a href="/admin/choose-email-link/?parent_page_id=1&amp;allow_external_link=true&amp;allow_email_link=true">Email link</a>
            </p>
            <h2>Explorer</h2>
            <ul className="breadcrumb"></ul>
            <PageChooserResultSet pageNumber={1} totalPages={1} items={this.props.items} onPageChosen={this.props.onPageChosen} onNavigate={this.props.onNavigate} />
        </div>;
    }
}
