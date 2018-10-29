import PropTypes from 'prop-types';
import React from 'react';
import {Form, FormGroup} from 'reactstrap';
import {lang} from '@pytsite/assetman';
import {TwoButtonsModal} from '@pytsite/widget/components';
import UserSelectSearch from './UserSelectSearch';


export default class UserSearchModal extends React.Component {
    static propTypes = {
        name: PropTypes.string.isRequired,
        className: PropTypes.string,
        exclude: PropTypes.object,
        isOpen: PropTypes.bool,
        cancelButtonCaption: PropTypes.string,
        isCancelButtonDisabled: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
        okButtonCaption: PropTypes.string,
        isOkButtonDisabled: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
        onToggle: PropTypes.func,
        onClickCancel: PropTypes.func,
        onClickOk: PropTypes.func,
        onUserSelect: PropTypes.func,
        title: PropTypes.string,
    };

    static defaultProps = {
        exclude: [],
        okButtonCaption: lang.t('auth_ui@add'),
        title: lang.t('auth_ui@select_user'),
    };

    constructor(props) {
        super(props);

        this.state = {
            userUid: null, // Selected user UID
        };

        this.onClickOk = this.onClickOk.bind(this);
        this.onClickCancel = this.onClickCancel.bind(this);
    }

    isUserSelected() {
        return this.state && this.state.userUid;
    }

    onClickOk() {
        this.props.onClickOk && this.props.onClickOk(this.state.userUid);
        this.setState({userUid: null});
        this.props.onToggle();
    }

    onClickCancel() {
        this.props.onClickCancel && this.props.onClickCancel();
        this.setState({userUid: null});
        this.props.onToggle();
    }

    render() {
        const isOkBtnDisabled = this.props.isOkButtonDisabled !== undefined ?
            this.props.isOkButtonDisabled :
            !this.isUserSelected();

        return (
            <TwoButtonsModal
                title={this.props.title}
                isOpen={this.props.isOpen}
                onToggle={this.props.onToggle}
                className={this.props.className}
                onClickOk={this.onClickOk}
                onClickCancel={this.onClickCancel}
                okButtonCaption={this.props.okButtonCaption}
                cancelButtonCaption={this.props.cancelButtonCaption}
                isOkButtonDisabled={isOkBtnDisabled}
                isCancelButtonDisabled={this.props.isCancelButtonDisabled}
            >
                <Form>
                    <FormGroup>
                        <UserSelectSearch
                            exclude={this.props.exclude}
                            name={this.props.name}
                            onSelect={userUid => {
                                this.setState({userUid: userUid});
                                this.props.onUserSelect && this.props.onUserSelect(userUid);
                            }}
                        />
                    </FormGroup>

                    {this.props.children}
                </Form>
            </TwoButtonsModal>
        )
    }
}
