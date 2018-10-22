import {lang} from '@pytsite/assetman';
import PropTypes from 'prop-types';
import React from 'react';
import {Button, Form, FormGroup, Modal, ModalHeader, ModalBody, ModalFooter} from 'reactstrap';
import UserSelectSearch from './UserSelectSearch';


export default class UserSearchModal extends React.Component {
    static propTypes = {
        className: PropTypes.string,
        exclude: PropTypes.object,
        isOpen: PropTypes.bool,
        name: PropTypes.string.isRequired,
        okButtonCaption: PropTypes.string,
        onModalToggle: PropTypes.func,
        onUserSelect: PropTypes.func,
    };

    static defaultProps = {
        exclude: [],
        okButtonCaption: lang.t('auth_ui@add'),
    };

    constructor(props) {
        super(props);

        this.state = {
            userUid: null, // Selected user
        };

        this.onUserSelectSearchSelect = this.onUserSelectSearchSelect.bind(this);
        this.onModalClickOK = this.onModalClickOK.bind(this);
        this.onModalClickCancel = this.onModalClickCancel.bind(this);
    }

    onUserSelectSearchSelect(e) {
        this.setState({
            userUid: e.target.value
        });
    }

    onModalClickOK() {
        this.state.userUid && this.props.onUserSelect && this.props.onUserSelect(this.state.userUid);
        this.setState({userUid: null});
        this.props.onModalToggle();
    }

    onModalClickCancel() {
        this.setState({userUid: null});
        this.props.onModalToggle();
    }

    render() {
        return <Modal isOpen={this.props.isOpen} toggle={this.onModalClickCancel} className={this.props.className}>
            <ModalHeader toggle={this.onModalClickCancel}>{this.props.title}</ModalHeader>
            <ModalBody>
                <Form>
                    <FormGroup>
                        <UserSelectSearch name={this.props.name} onSelect={this.onUserSelectSearchSelect}
                                          exclude={this.props.exclude}/>
                    </FormGroup>
                </Form>
            </ModalBody>
            <ModalFooter>
                <Button color="secondary" onClick={this.onModalClickCancel}>
                    {lang.t('auth_ui@cancel')}
                </Button>{' '}
                <Button color="primary" disabled={!this.state.userUid} onClick={this.onModalClickOK}>
                    {this.props.okButtonCaption}
                </Button>
            </ModalFooter>
        </Modal>
    }
}
