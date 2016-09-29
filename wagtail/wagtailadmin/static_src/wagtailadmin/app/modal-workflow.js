import React from 'react';
import ReactDOM from 'react-dom';

import PageChooser from 'components/choosers/page/PageChooser';


export function createPageChooser(id, modelNames, parent, canChooseRoot) {
    let modalPlacement = document.getElementById('react-modal');

    let chooserElement = document.getElementById(`${id}-chooser`);
    let pageTitleElement = chooserElement.querySelector('.title');
    let editLinkElement = chooserElement.querySelector('.edit-link');
    let inputElement = document.getElementById(id);
    let chooseButton = chooserElement.querySelector('.action-choose');
    let clearButton = chooserElement.querySelector('.action-clear');

    // TODO: Change this to chooseButton
    chooserElement.addEventListener('click', function() {
        let onModalClose = () => {
            ReactDOM.render(<div />, modalPlacement);
        };

        ReactDOM.render(<PageChooser onModalClose={onModalClose} />, modalPlacement);
    });


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
