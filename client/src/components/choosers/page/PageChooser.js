import React from 'react';
import { connect } from 'react-redux';

import { BaseChooser } from '../BaseChooser';

import * as actions from './actions';
import PageChooserHeader from './PageChooserHeader';
import PageChooserBrowseView from './views/PageChooserBrowseView';
import PageChooserSearchView from './views/PageChooserSearchView';


// TODO PageChooserExternalLinkView
// TODO PageChooserEmailView


function getTotalPages(totalItems, itemsPerPage) {
    return Math.ceil(totalItems / itemsPerPage);
}

class PageChooser extends BaseChooser {
    renderModalContents() {
        // Event handlers
        let onSearch = (queryString) => {
            if (queryString) {
                this.props.search(queryString, 1);
            } else {
                // Search box is empty, browse instead
                this.props.browse('root', 1);
            }
        }

        let onNavigate = (page) => {
            this.props.browse(page.id, 1);
        };

        let onChangePage = (newPageNumber) => {
            switch (this.props.viewName) {
                case 'browse':
                    this.props.browse(this.props.viewOptions.parentPageID, newPageNumber);
                    break;
                case 'search':
                    this.props.search(this.props.viewOptions.queryString, newPageNumber);
                    break;
            }
        };

        // Views
        let view = null;
        switch (this.props.viewName) {
            case 'browse':
                view = <PageChooserBrowseView items={this.props.items} pageNumber={this.props.viewOptions.pageNumber} totalPages={getTotalPages(this.props.totalItems, 20)} onPageChosen={this.props.onPageChosen} onNavigate={onNavigate} onChangePage={onChangePage} />;
                break;
            case 'search':
                view = <PageChooserSearchView items={this.props.items} pageNumber={this.props.viewOptions.pageNumber} totalPages={getTotalPages(this.props.totalItems, 20)} onPageChosen={this.props.onPageChosen} onNavigate={onNavigate} onChangePage={onChangePage} />;
                break;
        }

        return (
            <div>
                <PageChooserHeader onSearch={onSearch} />
                {view}
            </div>
        );
    }

    componentDidMount() {
        this.props.browse('root', 1);
    }
}


const mapStateToProps = (state) => ({
    viewName: state.viewName,
    viewOptions: state.viewOptions,
    items: state.items,
    totalItems: state.totalItems,
    pageTypes: state.pageTypes,
});

const mapDispatchToProps = (dispatch) => ({
    browse: (parentPageID, pageNumber) => dispatch(actions.browse(parentPageID, pageNumber)),
    search: (queryString, pageNumber) => dispatch(actions.search(queryString, pageNumber)),
});

export default connect(mapStateToProps, mapDispatchToProps)(PageChooser);
