import React from 'react';
import { connect } from 'react-redux';

import { BaseChooser } from '../BaseChooser';

import * as actions from './actions';
import PageChooserHeader from './PageChooserHeader';
import PageChooserBrowseView from './views/PageChooserBrowseView';


// TODO PageChooserSearchView
// TODO PageChooserExternalLinkView
// TODO PageChooserEmailView


class PageChooser extends BaseChooser {
    renderModalContents() {
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

        return (
            <div>
                <PageChooserHeader onSearch={onSearch} />
                <PageChooserBrowseView items={this.props.items} onPageChosen={this.props.onPageChosen} onNavigate={onNavigate} />
            </div>
        );
    }

    componentDidMount() {
        this.props.browse('root', 1);
    }
}


const mapStateToProps = (state) => ({
    state: state,
    items: state.pages,
    pageTypes: state.pageTypes,
});

const mapDispatchToProps = (dispatch) => ({
    browse: (parentPageID, pageNumber) => dispatch(actions.browse(parentPageID, pageNumber)),
    search: (queryString, pageNumber) => dispatch(actions.search(queryString, pageNumber)),
});

export default connect(mapStateToProps, mapDispatchToProps)(PageChooser);
