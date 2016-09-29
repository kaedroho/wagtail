import React from 'react';

import PageChooserPagination from '../PageChooserPagination';


class PageChooserResult extends React.Component {
    renderTitle() {
        if (this.props.isChoosable) {
            return <td className="title" data-listing-page-title="" valign="top">
                <h2>
                    <a
                        className="choose-page"
                        href="#2"
                        data-id={this.props.page.id}
                        data-title={this.props.page.title}
                        data-url={this.props.page.meta.html_url}
                        data-parent-id={this.props.page.meta.parent.id}
                        data-edit-url="/admin/pages/{this.props.page.id}/edit/">

                        {this.props.page.title}
                    </a>
                </h2>
            </td>;
        } else {
            return <td className="title" data-listing-page-title="" valign="top">
                <h2>
                    {this.props.page.title}
                </h2>
            </td>;
        }
    }

    renderUpdatedAt() {
        // TODO: Unhardcode this
        return <td className="updated" valign="top">
            <div className="human-readable-date" title="21 Sep 2016 10:46">
                1&nbsp;week, 1&nbsp;day ago
            </div>
        </td>;
    }

    renderType() {
        // TODO: Human-readable type
        return <td className="type" valign="top">{this.props.page.meta.type}</td>;
    }

    renderStatus() {
        return <td className="status" valign="top">
            <a
                href={this.props.page.meta.html_url}
                arget="_blank"
                className="status-tag primary">

                {this.props.page.meta.status.status}
            </a>
        </td>;
    }

    renderChildren() {
        if (this.props.hasChoosableChildren) {
            return <td className="children">
                <a
                    className="icon text-replace icon-arrow-right navigate-pages"
                    title={`Explore subpages of '${this.props.page.title}'`}>

                    Explore
                </a>
            </td>;
        } else {
            return <td></td>;
        }
    }

    render() {
        let classNames = [];

        if (!this.props.page.meta.status.live) {
            classNames.push('unpublished');
        }

        if (!this.props.isChoosable) {
            classNames.push('disabled');
        }

        return <tr className={classNames}>
            {this.renderTitle()}
            {this.renderUpdatedAt()}
            {this.renderType()}
            {this.renderStatus()}
            {this.renderChildren()}
        </tr>;
    }
}


class PageChooserResultSet extends React.Component {
    render() {
        let resultsRendered = [];

        for (let i in this.props.items) {
            // TODO: set isChoosable and hasChoosableChildren
            resultsRendered.push(
                <PageChooserResult
                    key={i}
                    page={this.props.items[i]}
                    isChoosable={true}
                    hasChoosableChildren={true}
                />
            );
        }

        return <div className="page-results">
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
                    {resultsRendered}
                </tbody>
            </table>

            <PageChooserPagination pageNumber={1} totalPages={1} />
        </div>;
    }
}


export default class PageChooserExplorerView extends React.Component {
    render() {
        return <div className="nice-padding">
            <p className="link-types">
                <b>Internal link</b> | <a href="/admin/choose-external-link/?parent_page_id=1&amp;allow_external_link=true&amp;allow_email_link=true">External link</a> | <a href="/admin/choose-email-link/?parent_page_id=1&amp;allow_external_link=true&amp;allow_email_link=true">Email link</a>
            </p>
            <h2>Explorer</h2>
            <ul className="breadcrumb"></ul>
            <PageChooserResultSet pageNumber={1} totalPages={1} items={[
                {
                    id: 2,
                    meta: {
                        type: "rca.HomePage",
                        html_url: "http://verdant-rca-staging.torchboxapps.com/",
                        status: {
                            status: "live",
                            live: false,
                            has_unpublished_changes: false
                        },
                        parent: {
                            id: 1
                        }
                    },
                    title: "Homepage"
                }
            ]} />
        </div>;
    }
}
