define(['assetman', 'http-api', 'lang'], function (assetman, httpApi, lang) {
    return function (widget) {
        var em = widget.em;
        var btn = em.find('.btn');
        var follow_msg_id = em.data('followMsgId');
        var unfollow_msg_id = em.data('unfollowMsgId');
        var following_msg_id = em.data('followingMsgId');

        em.mouseover(function () {
            if (btn.hasClass('following')) {
                btn.removeClass('btn-primary').addClass('btn-danger');
                btn.find('.icon').removeClass('fa-check').addClass('fa-remove');
                btn.find('.text').text(lang.t(unfollow_msg_id));
            }
        });

        em.mouseout(function () {
            if (btn.hasClass('following')) {
                btn.removeClass('btn-danger').addClass('btn-primary');
                btn.find('.icon').removeClass('fa-remove').addClass('fa-check');
                btn.find('.text').text(lang.t(following_msg_id));
            }
        });

        em.click(function (e) {
            e.preventDefault();

            if (btn.hasClass('following')) {
                if (!confirm(lang.t('auth_ui@unfollow_confirmation')))
                    return;

                httpApi.delete('auth/follow/' + em.data('userId')).done(function (data) {
                    btn.removeClass('btn-danger').addClass('btn-default').removeClass('following').addClass('non-following');
                    btn.find('.icon').addClass('fa-plus');
                    btn.find('.text').text(lang.t(follow_msg_id));
                });
            }
            else if (btn.hasClass('non-following')) {
                httpApi.post('auth/follow/' + em.data('userId')).done(function (data) {
                    btn.removeClass('btn-default').addClass('btn-danger').removeClass('non-following').addClass('following');
                    btn.find('.icon').removeClass('fa-plus').addClass('fa-remove');
                    btn.find('.text').text(lang.t(unfollow_msg_id));
                });
            }
        });

        assetman.loadCSS('auth_ui@css/widget-follow.css');
    }
});
