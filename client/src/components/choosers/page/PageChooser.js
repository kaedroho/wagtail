import React from 'react';

import { BaseChooser } from '../BaseChooser';

import PageChooserHeader from './PageChooserHeader';
import PageChooserExplorerView from './views/PageChooserExplorerView';


// TODO PageChooserSearchView
// TODO PageChooserExternalLinkView
// TODO PageChooserEmailView


export default class PageChooser extends BaseChooser {
    renderModalContents() {
        return (
            <div>
                <PageChooserHeader />
                <PageChooserExplorerView />
            </div>
        );
    }
}
