/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";

function addRestrictedClass() {
    if (session.crm_custom_permissions_enabled) {
        if (document.documentElement && !document.documentElement.classList.contains("o_crm_custom_permissions_restricted")) {
            document.documentElement.classList.add("o_crm_custom_permissions_restricted");
        }
        if (document.body && !document.body.classList.contains("o_crm_custom_permissions_restricted")) {
            document.body.classList.add("o_crm_custom_permissions_restricted");
        }
    }
}

// Execute safely when script loads
addRestrictedClass();

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addRestrictedClass);
}

const crmCustomPermissionsService = {
    dependencies: [],
    start() {
        if (!session.crm_custom_permissions_enabled) {
            return;
        }

        addRestrictedClass();

        // Safe capturing-phase listener on window to block clicks and hovers on author/avatar elements
        const blockSelector = ".o-mail-Message-author, .o-mail-Message-avatar, .o-mail-Message-authorName, .o_author_card, .o_popover_author, .o_avatar_card, .o_avatar_card_popover, .o-mail-AvatarCardPopover, [data-oe-model='res.partner'], div[class*='AvatarCard']";

        window.addEventListener("click", (ev) => {
            const target = ev.target.closest(blockSelector);
            if (target) {
                ev.preventDefault();
                ev.stopPropagation();
                ev.stopImmediatePropagation();
            }
        }, true);

        window.addEventListener("mouseover", (ev) => {
            const target = ev.target.closest(blockSelector);
            if (target) {
                ev.preventDefault();
                ev.stopPropagation();
                ev.stopImmediatePropagation();
            }
        }, true);
    },
};

registry.category("services").add("crm_custom_permissions_service", crmCustomPermissionsService);
