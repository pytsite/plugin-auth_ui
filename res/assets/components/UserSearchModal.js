import PropTypes from 'prop-types';
import React from 'react';
import {Form, FormGroup} from 'reactstrap';
import {lang} from '@pytsite/assetman';
import {TwoButtonsModal} from '@pytsite/widget/components';
import UserSelectSearch from './UserSelectSearch';


export default class UserSearchModal extends React.Component {
    static propTypes = {
        name: PropTypes.string,
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
        selectedUserUid: PropTypes.string,
        title: PropTypes.string,
        userSelectPlaceholder: PropTypes.string,
    };

    static defaultProps = {
        exclude: [],
        okButtonCaption: lang.t('auth_ui@add'),
        title: lang.t('auth_ui@select_user'),
        userSelectPlaceholder: lang.t('auth_ui@user'),
    };

    constructor(props) {
        super(props);

        this.onClickOk = this.onClickOk.bind(this);
        this.onClickCancel = this.onClickCancel.bind(this);
    }

    onClickOk() {
        this.props.onClickOk && this.props.onClickOk();
        this.props.onToggle();
    }

    onClickCancel() {
        this.props.onClickCancel && this.props.onClickCancel();
        this.props.onToggle();
    }

    render() {
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
                isOkButtonDisabled={this.props.isOkButtonDisabled}
                isCancelButtonDisabled={this.props.isCancelButtonDisabled}
            >
                <Form>
                    <FormGroup>
                        <UserSelectSearch
                            value={this.props.selectedUserUid}
                            exclude={this.props.exclude}
                            name={this.props.name}
                            placeholder={this.props.userSelectPlaceholder}
                            onSelect={this.props.onUserSelect}
                        />
                    </FormGroup>

                    {this.props.children}
                </Form>
            </TwoButtonsModal>
        )
    }
}
