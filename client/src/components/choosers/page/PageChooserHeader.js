import React from 'react';


export default class PageChooserHeader extends React.Component {
    render() {
        return <header className="nice-padding hasform">
            <div className="row">
                <div className="left">
                    <div className="col">
                        <h1 className="icon icon-doc-empty-inverse">Choose a page <span>Page</span></h1>
                    </div>
                    <form className="col search-form" action="/admin/choose-page/search/?page_type=wagtailcore.page" method="get" novalidate="">
                        <ul className="fields">
                            <li className="required">
                                <div className="field char_field text_input field-small iconfield">
                                    <label for="id_q">Search term:</label>
                                    <div className="field-content">
                                        <div className="input icon-search ">
                                            <input id="id_q" name="q" placeholder="Search" type="text" />
                                            <span></span>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <li className="submit visuallyhidden"><input value="Search" className="button" type="submit" /></li>
                        </ul>
                    </form>
                </div>
                <div className="right"></div>
            </div>
        </header>;
    }
}
