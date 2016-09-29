import React from 'react';

import PageChooserPagination from './PageChooserPagination';


export class PageChooserResult extends React.Component {
    renderTitle() {
        if (this.props.isChoosable) {
            return <td className="title" data-listing-page-title="" valign="top">
                <h2>
                    <a
                        onClick={this.props.onChoose}
                        className="choose-page"
                        href="#"
                        data-id={this.props.page.id}
                        data-title={this.props.page.title}
                        data-url={this.props.page.meta.html_url}
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
        let pageType = this.props.page.meta.type;
        if (this.props.pageTypes && pageType in this.props.pageTypes) {
            pageType = this.props.pageTypes[pageType].verbose_name;
        }

        return <td className="type" valign="top">{pageType}</td>;
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
        if (this.props.isNavigable) {
            return <td className="children">
                <a
                    onClick={this.props.onNavigate}
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

        if (this.props.isParent) {
            classNames.push('index');
        }

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


export default class PageChooserResultSet extends React.Component {
    render() {
        // Results
        let resultsRendered = [];
        for (let i in this.props.items) {
            let page = this.props.items[i];

            let onChoose = (e) => {
                this.props.onPageChosen(page);
                e.preventDefault();
            };

            let onNavigate = (e) => {
                this.props.onNavigate(page);
                e.preventDefault();
            };

            // TODO: set isChoosable and isNavigable
            resultsRendered.push(
                <PageChooserResult
                    key={i}
                    page={this.props.items[i]}
                    isChoosable={true}
                    isNavigable={true}
                    onChoose={onChoose}
                    onNavigate={onNavigate}
                    pageTypes={this.props.pageTypes}
                />
            );
        }

        // Parent page
        let parent = null;
        if (this.props.parentPage) {
            let onChoose = (e) => {
                this.props.onPageChosen(this.props.parentPage);
                e.preventDefault();
            };

            let onNavigate = (e) => {
                this.props.onNavigate(this.props.parentPage);
                e.preventDefault();
            };

            // TODO: set isChoosable
            parent = (
                <PageChooserResult
                    page={this.props.parentPage}
                    isParent={true}
                    isChoosable={true}
                    isNavigable={false}
                    onChoose={onChoose}
                    onNavigate={onNavigate}
                    pageTypes={this.props.pageTypes}
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
                    {parent}
                </thead>
                <tbody>
                    {resultsRendered}
                </tbody>
            </table>

            <PageChooserPagination pageNumber={this.props.pageNumber} totalPages={this.props.totalPages} onChangePage={this.props.onChangePage} />
        </div>;
    }
}
