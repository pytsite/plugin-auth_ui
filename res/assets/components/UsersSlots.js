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
        enabled: PropTypes.bool,
        maxSlots: PropTypes.number,
        modalTitle: PropTypes.string,
        modalAppendBody: PropTypes.object,
        modalOkButtonCaption: PropTypes.func,
        modalCancelButtonCaption: PropTypes.func,
        isModalOkButtonDisabled: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
        isModalCancelButtonDisabled: PropTypes.bool,
        modalUserSelectPlaceholder: PropTypes.string,
        onUserAdd: PropTypes.func,
        onUserDelete: PropTypes.func,
        onModalCancel: PropTypes.func,
        onModalUserSelect: PropTypes.func,
        slotContent: PropTypes.func,
        userTitleFormat: PropTypes.string,
        value: PropTypes.arrayOf(PropTypes.string),
    };

    static defaultProps = {
        className: '',
        enabled: false,
        maxSlots: 100,
        modalTitle: lang.t('auth_ui@select_user'),
        modalUserSelectPlaceholder: lang.t('auth_ui@user'),
    };

    constructor(props) {
        super(props);

        this.state = {
            users: {},
            isModalOpened: false,
            modalSelectedUserUid: null,
            userToReplaceUid: null,
        };

        this.slotRenderer = this.slotRenderer.bind(this);
        this.onModalClickOk = this.onModalClickOk.bind(this);
        this.onModalClickCancel = this.onModalClickCancel.bind(this);
        this.onModalUserSelect = this.onModalUserSelect.bind(this);
        this.onSlotClick = this.onSlotClick.bind(this);
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
        if (this.props.onUserDelete && !this.props.onUserDelete(user))
            return;

        if (confirm(lang.t('auth_ui@confirm_user_deletion'))) {
            const users = {};
            Object.keys(this.state.users).map(uid => {
                if (uid !== user.uid)
                    users[uid] = this.state.users[uid];
            });

            this.setState({
                users: users,
                modalSelectedUserUid: null,
            });
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
                enabled={this.props.enabled}
                content={this.props.slotContent}
                name={this.props.name}
                user={user}
                onDeleteButtonClick={this.onSlotDeleteButtonClick}
                userTitleFormat={this.props.userTitleFormat}
            />
        )
    }

    onModalClickOk() {
        httpApi.get(`auth/users/${this.state.modalSelectedUserUid}`).done(user => {
            const users = this.state.users;

            if (this.state.userToReplaceUid)
                delete users[this.state.userToReplaceUid];

            users[user.uid] = user;

            this.setState({
                users: users
            });

            this.props.onUserAdd && this.props.onUserAdd(user);

            this.setState({
                modalSelectedUserUid: null,
                userToReplaceUid: null,
            });
        });
    }

    onModalClickCancel() {
        this.setState({
            userToReplaceUid: null,
            modalSelectedUserUid: null,
        });

        this.props.onModalCancel && this.props.onModalCancel();
    }

    onSlotClick(userUid) {
        this.setState({
            userToReplaceUid: userUid,
            modalSelectedUserUid: userUid,
            isModalOpened: true,
        });
    }

    onModalUserSelect(userUid) {
        this.setState({
            modalSelectedUserUid: userUid,
        });

        this.props.onModalUserSelect && this.props.onModalUserSelect(userUid);
    }

    render() {
        return (
            <div className={`component-auth-ui component-users-slots ${this.props.className}`}>
                <input type="hidden" name={`${this.props.name}[]`}/>

                <Slots
                    data={this.state.users}
                    emptySlotRenderer={this.defaultEmptySlotRenderer}
                    enabled={this.props.enabled}
                    maxSlots={this.props.maxSlots}
                    onSlotClick={this.props.enabled && this.onSlotClick}
                    onEmptySlotClick={() => this.setState({isModalOpened: true})}
                    slotRenderer={this.slotRenderer}
                />

                <UserSearchModal
                    selectedUserUid={this.state.modalSelectedUserUid}
                    exclude={this.state.users}
                    isOpen={this.state.isModalOpened}
                    name={this.props.name}
                    okButtonCaption={this.props.modalOkButtonCaption}
                    cancelButtonCaption={this.props.modalCancelButtonCaption}
                    isOkButtonDisabled={this.props.isModalOkButtonDisabled || (() => !this.state.modalSelectedUserUid)}
                    isCancelButtonDisabled={this.props.isModalCancelButtonDisabled}
                    onToggle={() => this.setState({isModalOpened: !this.state.isModalOpened})}
                    onClickCancel={this.onModalClickCancel}
                    onClickOk={this.onModalClickOk}
                    onUserSelect={this.onModalUserSelect}
                    userSelectPlaceholder={this.props.modalUserSelectPlaceholder}
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
                          value={widget.data('value')}
                          enabled={widget.data('enabled') === 'True'}
                          maxSlots={widget.data('maxSlots')}
                          modalTitle={widget.data('modalTitle')}
                          modalOkButtonCaption={widget.data('modalOkButtonCaption')}
                          modalCancelButtonCaption={widget.data('modalCancelButtonCaption')}
    />;

    ReactDOM.render(c, widget.find('.widget-component')[0]);
});
