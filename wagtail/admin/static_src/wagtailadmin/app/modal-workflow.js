import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware, compose } from 'redux';
import thunkMiddleware from 'redux-thunk';

import PageChooser from 'components/choosers/page/PageChooser';
import pageChooser from 'components/choosers/page/reducers';



export function createPageChooser(id, modelNames, parent, canChooseRoot) {
    let modalPlacement = document.getElementById('react-modal');

    let chooserElement = document.getElementById(`${id}-chooser`);
    let pageTitleElement = chooserElement.querySelector('.title');
    let editLinkElement = chooserElement.querySelector('.edit-link');
    let inputElement = document.getElementById(id);
    let chooseButtons = chooserElement.querySelectorAll('.action-choose');
    let clearButton = chooserElement.querySelector('.action-clear');

    for (let chooseButton of chooseButtons) {
        chooseButton.addEventListener('click', function() {
            const middleware = [
                thunkMiddleware,
            ];

            const store = createStore(pageChooser, {}, compose(
                applyMiddleware(...middleware),
                // Expose store to Redux DevTools extension.
                window.devToolsExtension ? window.devToolsExtension() : f => f
            ));

            let onModalClose = () => {
                ReactDOM.render(<div />, modalPlacement);
            };

            let onPageChosen = (page) => {
                inputElement.value = page.id;
                pageTitleElement.innerHTML = page.title;  // FIXME
                chooserElement.classList.remove('blank');
                editLinkElement.href = `/admin/pages/${page.id}/edit/`;  // FIXME

                onModalClose();
            };

            ReactDOM.render(<Provider store={store}>
                <PageChooser onModalClose={onModalClose} onPageChosen={onPageChosen} />
            </Provider>, modalPlacement);
        });
    }

/*
    var chooserElement = $('#' + id + '-chooser');
    var pageTitle = chooserElement.find('.title');
    var input = $('#' + id);
    var editLink = chooserElement.find('.edit-link');

    $('.action-choose', chooserElement).click(function() {
        var initialUrl = window.chooserUrls.pageChooser;
        if (openAtParentId) {
            initialUrl += openAtParentId + '/';
        }

        var urlParams = {page_type: pageTypes.join(',')};
        if (canChooseRoot) {
            urlParams.can_choose_root = 'true';
        }

        ModalWorkflow({
            url: initialUrl,
            urlParams: urlParams,
            responses: {
                pageChosen: function(pageData) {
                    input.val(pageData.id);
                    openAtParentId = pageData.parentId;
                    pageTitle.text(pageData.title);
                    chooserElement.removeClass('blank');
                    editLink.attr('href', pageData.editUrl);
                }
            }
        });
    });

    $('.action-clear', chooserElement).click(function() {
        input.val('');
        openAtParentId = null;
        chooserElement.addClass('blank');
    });
*/
}
