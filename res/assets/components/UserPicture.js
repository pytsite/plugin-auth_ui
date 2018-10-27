import './css/UserPicture.scss';
import React from 'react';
import PropTypes from "prop-types";

/**
 * User Picture
 */
export default class UserPicture extends React.Component {
    static propTypes = {
        className: PropTypes.string,
        user: PropTypes.shape({
            picture: PropTypes.shape({
                url: PropTypes.string,
            })
        })
    };

    static defaultProps = {
        className: '',
    };

    render() {
        return <img className={`component-auth-ui component-user-picture ${this.props.className}`.trim()}
                    src={this.props.user.picture.url}/>;
    }
}
