import React from 'react';

import PageChooserPagination from '../PageChooserPagination';



class PageChooserResult extends React.Component {
    render() {
        return <tr className=" ">
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
        </tr>;
    }
}


class PageChooserResultSet extends React.Component {
    render() {
        return <div className="page-results">
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
                    <PageChooserResult />
                </tbody>
            </table>

            <PageChooserPagination />
        </div>;
    }
}


export default class PageChooserExplorerView extends React.Component {
    render() {
        return <div className="nice-padding">
            <p className="link-types">
                <b>Internal link</b> | <a href="/admin/choose-external-link/?parent_page_id=1&amp;allow_external_link=true&amp;allow_email_link=true">External link</a> | <a href="/admin/choose-email-link/?parent_page_id=1&amp;allow_external_link=true&amp;allow_email_link=true">Email link</a>
            </p>
            <PageChooserResultSet />
        </div>;
    }
}
