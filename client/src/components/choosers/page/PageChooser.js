import React from 'react';
import { connect } from 'react-redux';

import { BaseChooser } from '../BaseChooser';

import * as actions from './actions';
import PageChooserHeader from './PageChooserHeader';
import PageChooserExplorerView from './views/PageChooserExplorerView';


// TODO PageChooserSearchView
// TODO PageChooserExternalLinkView
// TODO PageChooserEmailView


class PageChooser extends BaseChooser {
    renderModalContents() {
        return (
            <div>
                <PageChooserHeader />
                <PageChooserExplorerView items={this.props.items} />
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
});

export default connect(mapStateToProps, mapDispatchToProps)(PageChooser);
