import './css/UsersSlots.scss';
import PropTypes from "prop-types";
import React from 'react';
import ReactDOM from 'react-dom';
import {lang} from '@pytsite/assetman';
import httpApi from '@pytsite/http-api';
import {Slots} from '@pytsite/widget/components';
import UserPicture from './UserPicture';
import UserSearchModal from './UserSearchModal';
import {Button} from 'reactstrap';
import setupWidget from "@pytsite/widget";


class UserSlot extends React.Component {
    static propTypes = {
        className: PropTypes.string,
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

    formatText(user) {
        let mask = this.props.userTitleFormat;

        Object.keys(user).map(key => {
            if (user.hasOwnProperty(key))
                mask = mask.replace(`{${key}}`, user[key]);
        });

        return mask;
    }

    render() {
        return <div className={`component-auth-ui component-user-slot ${this.props.className}`}>
            <input type="hidden" name={this.props.name} value={this.props.user.uid}/>
            <UserPicture user={this.props.user}/>
            <div className={'user-title'}>
                {this.formatText(this.props.user)}
            </div>
            <div className={'slot-actions'}>
                <Button size={'sm'} color={'danger'} onClick={() => this.props.onDeleteButtonClick(this.props.user)}>
                    <i className="fas fa-times"></i>
                </Button>
            </div>
        </div>
    }
}


export default class UsersSlots extends React.Component {
    static propTypes = {
        className: PropTypes.string,
        isEmptySlotEnabled: PropTypes.bool,
        maxSlots: PropTypes.number,
        modalTitle: PropTypes.string,
        name: PropTypes.string.isRequired,
        userTitleFormat: PropTypes.string,
        value: PropTypes.arrayOf(PropTypes.string),
    };

    static defaultProps = {
        className: '',
        isEmptySlotEnabled: false,
        maxSlots: 100,
        modalTitle: lang.t('auth_ui@select_user'),
    };

    constructor(props) {
        super(props);

        this.state = {
            users: {},
            modalIsOpened: false,
        };

        this.renderSlot = this.renderSlot.bind(this);
        this.onModalToggle = this.onModalToggle.bind(this);
        this.onUserSelect = this.onUserSelect.bind(this);
        this.onSlotDeleteButtonClick = this.onSlotDeleteButtonClick.bind(this);
    }

    componentDidMount() {
        httpApi.get('auth/users', {uids: JSON.stringify(this.props.value)}).done(data => {
            const users = {};
            data.map(user => users[user.uid] = user);

            this.setState({
                users: users,
            });
        });
    }

    onModalToggle() {
        this.setState({modalIsOpened: !this.state.modalIsOpened});
    }

    /**
     * Render empty slot
     *
     * @returns {React.Component}
     */
    renderEmptySlot() {
        return <i className={'fa fas fa-user-plus fa-2x'}></i>;
    }

    onSlotDeleteButtonClick(user) {
        if (confirm(lang.t('auth_ui@confirm_user_deletion'))) {
            const users = {};
            Object.keys(this.state.users).map(uid => {
                if (uid !== user.uid)
                    users[uid] = this.state.users[uid];
            });
            this.setState({users: users});
        }
    }

    /**
     * Render single slot
     *
     * @param user
     * @returns {React.Component}
     */
    renderSlot(user) {
        return <UserSlot name={this.props.name} user={user} onDeleteButtonClick={this.onSlotDeleteButtonClick}
                         userTitleFormat={this.props.userTitleFormat}/>
    }

    onUserSelect(userUid) {
        httpApi.get(`auth/users/${userUid}`).done(user => {
            const users = this.state.users;
            users[user.uid] = user;

            this.setState({
                users: users
            });
        });
    }

    render() {
        return <div className={`component-auth-ui component-users-slots ${this.props.className}`}>
            <Slots data={this.state.users} isEmptySlotEnabled={this.props.isEmptySlotEnabled}
                   renderEmptySlot={this.renderEmptySlot} renderSlot={this.renderSlot}
                   onEmptySlotClick={this.onModalToggle} maxSlots={this.props.maxSlots}/>

            <UserSearchModal name={this.props.name} isOpen={this.state.modalIsOpened} onModalToggle={this.onModalToggle}
                             title={this.props.modalTitle} onUserSelect={this.onUserSelect} exclude={this.state.users}/>
        </div>
    }
}

setupWidget('plugins.auth_ui._widget.UsersSlots', widget => {
    const c = <UsersSlots name={widget.uid} isEmptySlotEnabled={widget.data('isEmptySlotEnabled') === 'True'}
                          maxSlots={widget.data('maxSlots')}/>;

    ReactDOM.render(c, widget.find('.widget-component')[0]);
});
