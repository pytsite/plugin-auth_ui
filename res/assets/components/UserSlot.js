import React from "react";
import PropTypes from "prop-types";
import {Button} from "reactstrap";
import UserPicture from "./UserPicture";

export default class UserSlot extends React.Component {
    static propTypes = {
        className: PropTypes.string,
        content: PropTypes.func,
        enabled: PropTypes.bool,
        name: PropTypes.string,
        onDeleteButtonClick: PropTypes.func,
        user: PropTypes.shape({
            uid: PropTypes.string.isRequired,
        }).isRequired,
        userTitleFormat: PropTypes.string,
    };

    static defaultProps = {
        className: '',
        userTitleFormat: '{first_name} {last_name}',
    };

    formatUserTitle(user) {
        let mask = this.props.userTitleFormat;

        Object.keys(user).map(key => {
            if (user.hasOwnProperty(key))
                mask = mask.replace(`{${key}}`, user[key]);
        });

        return mask;
    }

    render() {
        const userTitle = this.formatUserTitle(this.props.user);
        let content = null;

        if (this.props.content)
            content = this.props.content(this.props.user, userTitle);
        else
            content = (
                <React.Fragment>
                    <input type="hidden" name={this.props.name + '[]'} value={this.props.user.uid}/>
                    <UserPicture user={this.props.user}/>
                    <div className={'user-title'}>{userTitle}</div>
                </React.Fragment>
            );

        if (this.props.enabled) {
            content = (
                <React.Fragment>
                    {content}

                    <div className={'slot-actions'}>
                        <Button size={'sm'} color={'danger'}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    this.props.onDeleteButtonClick && this.props.onDeleteButtonClick(this.props.user)
                                }}>
                            <i className="fas fa-times"></i>
                        </Button>
                    </div>
                </React.Fragment>
            )
        }
        else if(this.props.user.hasOwnProperty('url')) {
            content = (
                <a href={this.props.user.url}>{content}</a>
            )
        }

        return (
            <div className={`component-auth-ui component-user-slot ${this.props.className}`}>
                {content}
            </div>
        )
    }
}
