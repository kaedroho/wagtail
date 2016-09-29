import React from 'react';

import PageChooserResultSet from '../PageChooserResultSet';


export default class PageChooserBrowseView extends React.Component {
    render() {
        return <div className="nice-padding">
            <h2>Search</h2>
            <PageChooserResultSet pageNumber={1} totalPages={1} items={this.props.items} onPageChosen={this.props.onPageChosen} onNavigate={this.props.onNavigate} />
        </div>;
    }
}
