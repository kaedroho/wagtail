import React from 'react';


export default class PageChooserPagination extends React.Component {
    render() {
        return <div className="pagination">
            <p>
                {`Page ${this.props.pageNumber} of ${this.props.totalPages}.`}
            </p>
            <ul>
                <li className="prev">
                </li>
                <li className="next">
                </li>
            </ul>
        </div>;
    }
}
