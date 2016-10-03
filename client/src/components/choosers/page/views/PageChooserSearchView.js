import React from 'react';

import PageChooserResultSet from '../PageChooserResultSet';


export default class PageChooserBrowseView extends React.Component {
    render() {
        return <div className="nice-padding">
            <h2>Search</h2>
            <PageChooserResultSet pageNumber={this.props.pageNumber} totalPages={this.props.totalPages} items={this.props.items} pageTypes={this.props.pageTypes} restrictPageTypes={this.props.restrictPageTypes} onPageChosen={this.props.onPageChosen} onNavigate={this.props.onNavigate} onChangePage={this.props.onChangePage} />
        </div>;
    }
}
