import PropTypes from "prop-types";
import React from 'react';
import {lang} from '@pytsite/assetman';
import httpApi from "@pytsite/http-api";
import Select2 from '@pytsite/widget/components/Select2';

export default class UserSelectSearch extends React.Component {
    static propTypes = {
        className: PropTypes.string,
        id: PropTypes.string,
        exclude: PropTypes.object,
        name: PropTypes.string,
        onSelect: PropTypes.func,
        placeholder: PropTypes.string,
        userTitleFormat: PropTypes.string,
    };

    static defaultProps = {
        className: '',
        exclude: {},
        placeholder: lang.t('auth_ui@user'),
        userTitleFormat: '{first_name} {last_name}'
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
        const options = {
            placeholder: this.props.placeholder,
            ajax: {
                url: httpApi.url('auth/users', {exclude: JSON.stringify(Object.keys(this.props.exclude))}),
                dataType: 'json',
                cache: true,
                delay: 500,
                processResults: data => ({
                    results: data.map(user => ({id: user.uid, text: this.formatText(user)}))
                })
            }
        };

        return (
            <Select2 className={`form-control ${this.props.className}`.trim()}
                     id={this.props.id}
                     name={this.props.name}
                     options={options}
                     onSelect={e => this.props.onSelect && this.props.onSelect(e.target.value)}
            />
        )
    }
}