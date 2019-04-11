# PytSite Auth UI Plugin


## Changelog


### 4.14.1 (2019-04-11)

Link fixed in `UserSlot` React component. 


### 4.14 (2019-04-08)

`widget.UserSelect` replaced with `Select2` version.


### 4.13 (2019-03-21)

- Support of `widget-4.16`.
- CSS fixed.


### 4.12 (2019-03-09)

Support of `auth-3.15`.


### 4.11 (2019-03-09)

Support of `auth-3.14`.


### 4.10.5 (2019-02-11)

Issues fixed in `*_url()` API functions.


### 4.10.4 (2019-02-11)

`reactstrap`dependency updated.


### 4.10.3 (2018-12-13)

`UserSelectSearch` component behaviour fixed.


### 4.10.2 (2018-12-02)

Error in `UserSelectSearch` React component fixed.


### 4.10.1 (2018-11-28)

`UserProfileModify` controller fixed.


### 4.10 (2018-11-22)

Support of `http_api-3.3`.


### 4.9 (2018-11-19)

- New API functions: `role_form()`, `user_form()`.
- New configuration parameters: `auth_ui.*_form_class`.


### 4.8.3 (2018-11-06)

`UsersSlots` React component fixed.


### 4.8.2 (2018-11-06)

Handling of `onSlotClick` property of React component `UsersSlots`
fixed.


### 4.8.1 (2018-11-06)

`plugin.json` fixed.


### 4.8 (2018-11-06)

Basic editing functionality added to `UsersSlots` React component.


### 4.7 (2018-11-01)

New field `url` added to `auth.AbstractUser.as_jsonable()` response.


### 4.6 (2018-10-31)

New properties in React components:

- `UserSelectSearch.placeholder`;
- `UserSearchModal.userSelectPlaceholder`;
- `UsersSlots.modalUserSelectPlaceholder`.


### 4.5.1 (2018-10-30)

`UsersSlots` widget's arguments processing fixed.


### 4.5 (2018-10-29)

- Support of `widget-4.2`.
- `widget.UsersSlots`'s `is_empty_slot_enabled` kwarg renamed to
  `enabled`.


### 4.4 (2018-10-29)

`UsersSlots` React component and widget:

- new property `onUserDelete` added;
- widget's value issue fixed;
- `onModalClickCancel` property renamed to `onModalCancel`.


### 4.3 (2018-10-28)

React components refactored.


### 4.2.1 (2018-10-23)

User form CSS fixed.


### 4.2 (2018-10-22)

- Support of `assetman-5.x` and `widget-4.x`.
- New React components: `UserPicture`, `UserSearchModal`,
  `UserSelectSearch`, `UsersSlots`.
- New widget: `UsersSlots`.


### 4.1 (2018-10-12)

Support of `assetman-4.x`.


### 4.0.1 (2018-10-08)

Cleanup.


### 4.0 (2018-10-08)

Support of `pytsite-8.x`.


### 3.19.1 (2018-09-09)

User form fixed.


### 3.19 (2018-09-09)

Support of `form-4.14`.


### 3.18 (2017-08-23)

Support of `widget-2.12`.


### 3.17 (2017-08-23)

Support of `auth-3.8`.


### 3.16.2 (2017-08-23)

Missing function usage fixed.


### 3.16.1 (2017-08-22)

- User's `full_name` usage replaced with `first_last_name`.
- Unnecessary usage of `hreflang` plugin removed.


### 3.16 (2017-08-10)

Added `redirect` argument to `sign_out_url()`.


### 3.15 (2017-08-10)

Support of `auth-3.6`.


### 3.14.2 (2018-08-08)

Translations fixed.


### 3.14.1 (2018-08-08)

Role's form fixed.


### 3.14 (2018-08-02)

Support of `widget-2.5`.


### 3.13 (2018-07-30)

Forms names added.


### 3.12 (2018-07-30)

Support of `form-4.8`.


### 3.11 (2018-07-29)

- Support of `auth-3.5`.
- User's form reworked.


### 3.10.3 (2018-07-22)

Form icons fix.


### 3.10.2 (2018-07-22)

Form icons fix.


### 3.10.1 (2018-07-21)

Support of Twitter Bootstrap 4 fixed.


### 3.10 (2018-07-19)

User profile templates names changed.


### 3.9 (2018-07-16)

Support of `auth-3.4`, `http_api-2.0` and  `auth_http_api-2.0`.


### 3.8.1 (2018-07-08)

Missing public API functions added.


### 3.8 (2018-07-03)

`request` argument of form related API functions is now optional.


### 3.7 (2018-06-26)

Support of `assetman-2.0`.


### 3.6.1 (2018-06-24)

Controller arguments fix.


### 3.6 (2018-06-24)

Support for application provided form controllers.


### 3.5.1 (2018-06-23)

Non existent confirmation hash processing fixed.


### 3.5 (2018-06-07)

- Support of `pytsite-7.29`.
- `AuthFilterController` renamed to `AuthFilter`.


### 3.4.1 (2018-06-01)

Invalid mail recipient issue fixed.


### 3.4 (2018-06-01)

Support of `pytsite-7.24`.


### 3.3 (2018-05-21)

- Support of `auth-3.3`.
- Bugs fixed.


### 3.2 (2018-05-06)

- Support of `pytsite-7.17`, `auth-3.1`, `form-4.0`.
- New `Driver`'s abstract method added: `get_restore_account_form()`.


### 3.1.1 (2018-04-26)

Convenient CSS classes added to forms.


### 3.1 (2018-04-25)

- Meta titles added to profile view and edit controllers.
- Translation issue fixed.


### 3.0 (2018-04-25)

- Support of `auth-3.0`.
- New routes: `auth_ui@user_profile_view` and
  `auth_ui@user_profile_modify`.
- New module: `form`.



### 2.8.3 (2018-04-10)

Typo fixed.


### 2.8.2 (2018-04-10)

`sign_in_url()` fixed.


### 2.8.1 (2018-04-10)

Forms processing issues fixed.


### 2.8 (2018-04-10)

Support of `auth-2.6`.


### 2.7 (2018-04-09)

Support of `auth-2.5`.


### 2.6.3 (2018-04-09)

Missing mail templates fixed.


### 2.6.2 (2018-04-08)

Sign up form's CSS fixed.


### 2.6.1 (2018-04-08)

Form initialization fixed.


### 2.6 (2018-04-07)

- Sign up support added.
- Support of `auth-2.1`.
- Various little issues fixed.


### 2.5.1 (2018-03-28)

Package init fixed.


### 2.5 (2018-03-28)

- `user_profile_view_url()`, `user_profile_edit_url` removed.
- Profile view and edit controllers removed.


### 2.4 (2018-03-28)

- New API functions: `user_profile_view_url()`, `user_profile_edit_url`.
- `widget.Profile` and `widget.Follow` removed.
- Tpl globals removed in favour of using `plugins` global.
- Profile view conroller refactored.


### 2.3.1 (2018-03-18)

Form caching fixed.


### 2.3 (2018-03-15)

Support for `widget-1.6`.


### 2.2.3 (2017-12-18)

Init refactored.


### 2.2.2 (2017-12-18)

Text strings changed.


### 2.2.1 (2017-12-13)

Init fixed.


### 2.2 (2017-12-13)

- Support for `pytsite-7.0`.
- Part of the code moved to the `auth_settings` plugin.


### 2.1 (2017-12-02)

Support for last `auth` plugin update.


### 2.0 (2017-12-02)

- Support for `pytsite-6.1`.
- Merged code from various plugins.
- Added UI driver.


### 1.0 (2017-11-25)

First release.
