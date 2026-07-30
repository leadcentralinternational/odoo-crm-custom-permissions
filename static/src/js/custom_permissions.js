/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";

const crmCustomPermissionsService = {
    dependencies: [],
    start() {
        if (session.crm_custom_permissions_enabled) {
            document.body.classList.add("o_crm_custom_permissions_restricted");

            // Intercept clicks & mouse events on author links, avatars, and popovers
            const blockSelector = ".o-mail-Message-author, .o-mail-Message-avatar, .o-mail-Message-authorName, .o_author_card, .o_popover_author, .o_avatar_card, .o_avatar_card_popover, .o-mail-AvatarCardPopover, [data-oe-model='res.partner']";

            document.addEventListener("click", (ev) => {
                const target = ev.target.closest(blockSelector);
                if (target) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    ev.stopImmediatePropagation();
                }
            }, true);

            document.addEventListener("mouseenter", (ev) => {
                const target = ev.target.closest(blockSelector);
                if (target) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    ev.stopImmediatePropagation();
                }
            }, true);
        }
    },
};

registry.category("services").add("crm_custom_permissions_service", crmCustomPermissionsService);
