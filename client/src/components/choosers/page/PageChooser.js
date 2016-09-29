import React from 'react';

import { BaseChooser } from '../BaseChooser';


export default class PageChooser extends BaseChooser {
    renderModalContents() {
        return (
            <div>
                <header className="nice-padding hasform">
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
                </header>
                <div className="nice-padding">
                    <p className="link-types">
                        <b>Internal link</b> | <a href="/admin/choose-external-link/?parent_page_id=1&amp;allow_external_link=true&amp;allow_email_link=true">External link</a> | <a href="/admin/choose-email-link/?parent_page_id=1&amp;allow_external_link=true&amp;allow_email_link=true">Email link</a>
                    </p>
                    <div className="page-results">
                        <h2>Explorer</h2>
                        <ul className="breadcrumb"></ul>
                        <table className="listing  chooser">
                            <colgroup>
                                <col />
                                <col width="12%" />
                                <col width="12%" />
                                <col width="12%" />
                                <col width="10%" />
                            </colgroup>
                            <thead>
                                <tr className="table-headers">
                                    <th className="title">Title</th>
                                    <th className="updated">Updated</th>
                                    <th className="type">Type</th>
                                    <th className="status">Status</th>
                                    <th></th>
                                </tr>
                                <tr className="index  disabled">
                                    <td className="title">
                                        <h2>
                                            Root
                                        </h2>
                                    </td>
                                    <td className="updated" valign="bottom"></td>
                                    <td className="type" valign="bottom">
                                    </td>
                                    <td className="status" valign="bottom">
                                    </td>
                                    <td></td>
                                </tr>
                            </thead>
                            <tbody>
                                <tr className=" ">
                                    <td className="title" data-listing-page-title="" valign="top">
                                        <h2>
                                            <a className="choose-page" href="#2" data-id="2" data-title="Homepage" data-url="http://verdant-rca-staging.torchboxapps.com/" data-parent-id="1" data-edit-url="/admin/pages/2/edit/">Homepage</a>
                                        </h2>
                                    </td>
                                    <td className="updated" valign="top">
                                        <div className="human-readable-date" title="21 Sep 2016 10:46">1&nbsp;week, 1&nbsp;day ago</div>
                                    </td>
                                    <td className="type" valign="top">Home Page</td>
                                    <td className="status" valign="top">
                                        <a href="http://verdant-rca-staging.torchboxapps.com/" target="_blank" className="status-tag primary">live</a>
                                    </td>
                                    <td className="children">
                                        <a href="/admin/choose-page/2/?allow_external_link=true&amp;allow_email_link=true" className="icon text-replace icon-arrow-right navigate-pages" title="Explore subpages of 'Homepage'">Explore</a>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <div className="pagination">
                            <p>
                                Page 1 of 1.
                            </p>
                            <ul>
                                <li className="prev">
                                </li>
                                <li className="next">
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
