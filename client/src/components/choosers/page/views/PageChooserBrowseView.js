import React from 'react';

import PageChooserResultSet from '../PageChooserResultSet';


export default class PageChooserBrowseView extends React.Component {
    render() {
        return <div className="nice-padding">
            <h2>Explorer</h2>
            <ul className="breadcrumb"></ul>
            <PageChooserResultSet pageNumber={this.props.pageNumber} totalPages={this.props.totalPages} parentPage={this.props.parentPage} items={this.props.items} pageTypes={this.props.pageTypes} restrictPageTypes={this.props.restrictPageTypes} onPageChosen={this.props.onPageChosen} onNavigate={this.props.onNavigate} onChangePage={this.props.onChangePage} />
        </div>;
    }
}
