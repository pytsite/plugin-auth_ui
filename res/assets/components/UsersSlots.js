import './css/UsersSlots.scss';
import PropTypes from "prop-types";
import React from 'react';
import ReactDOM from 'react-dom';
import {lang} from '@pytsite/assetman';
import httpApi from '@pytsite/http-api';
import {Slots} from '@pytsite/widget/components';
import setupWidget from "@pytsite/widget";
import UserSlot from './UserSlot';
import UserSearchModal from './UserSearchModal';


export default class UsersSlots extends React.Component {
    static propTypes = {
        name: PropTypes.string.isRequired,
        className: PropTypes.string,
        isEmptySlotEnabled: PropTypes.bool,
        maxSlots: PropTypes.number,
        modalTitle: PropTypes.string,
        modalAppendBody: PropTypes.object,
        modalOkButtonCaption: PropTypes.func,
        modalCancelButtonCaption: PropTypes.func,
        isModalOkButtonDisabled: PropTypes.bool,
        isModalCancelButtonDisabled: PropTypes.bool,
        onModalClickCancel: PropTypes.func,
        onUserAdd: PropTypes.func,
        onModalUserSelect: PropTypes.func,
        slotContent: PropTypes.func,
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
            isModalOpened: false,
        };

        this.slotRenderer = this.slotRenderer.bind(this);
        this.onModalClickOk = this.onModalClickOk.bind(this);
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

    /**
     * Render empty slot
     *
     * @returns {React.Component}
     */
    defaultEmptySlotRenderer() {
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
    slotRenderer(user) {
        return (
            <UserSlot
                content={this.props.slotContent}
                name={this.props.name}
                user={user}
                onDeleteButtonClick={this.onSlotDeleteButtonClick}
                userTitleFormat={this.props.userTitleFormat}
            />
        )
    }

    onModalClickOk(userUid) {
        httpApi.get(`auth/users/${userUid}`).done(user => {
            const users = this.state.users;
            users[user.uid] = user;

            this.setState({
                users: users
            });

            this.props.onUserAdd && this.props.onUserAdd(user);
        });
    }

    render() {
        return (
            <div className={`component-auth-ui component-users-slots ${this.props.className}`}>
                <input type="hidden" name={`${this.props.name}[]`}/>

                <Slots
                    data={this.state.users}
                    emptySlotRenderer={this.defaultEmptySlotRenderer}
                    isEmptySlotEnabled={this.props.isEmptySlotEnabled}
                    maxSlots={this.props.maxSlots}
                    onEmptySlotClick={() => this.setState({isModalOpened: true})}
                    slotRenderer={this.slotRenderer}
                />

                <UserSearchModal
                    exclude={this.state.users}
                    isOpen={this.state.isModalOpened}
                    name={this.props.name}
                    okButtonCaption={this.props.modalOkButtonCaption}
                    cancelButtonCaption={this.props.modalCancelButtonCaption}
                    isOkButtonDisabled={this.props.isModalOkButtonDisabled}
                    isCancelButtonDisabled={this.props.isModalCancelButtonDisabled}
                    onToggle={() => this.setState({isModalOpened: !this.state.isModalOpened})}
                    onClickCancel={this.props.onModalClickCancel}
                    onClickOk={this.onModalClickOk}
                    onUserSelect={this.props.onModalUserSelect}
                    title={this.props.modalTitle}
                >
                    {this.props.modalAppendBody}
                </UserSearchModal>
            </div>
        )
    }
}

setupWidget('plugins.auth_ui._widget.UsersSlots', widget => {
    const c = <UsersSlots name={widget.uid}
                          isEmptySlotEnabled={widget.data('isEmptySlotEnabled') === 'True'}
                          maxSlots={widget.data('maxSlots')}
    />;

    ReactDOM.render(c, widget.find('.widget-component')[0]);
});
