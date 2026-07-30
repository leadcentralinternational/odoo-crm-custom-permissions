/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";

function enforceRestriction() {
    if (session.crm_custom_permissions_enabled) {
        document.documentElement.classList.add("o_crm_custom_permissions_restricted");
        if (document.body) {
            document.body.classList.add("o_crm_custom_permissions_restricted");
        }
    }
}

// Execute immediately upon JS loading
enforceRestriction();

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enforceRestriction);
}

const crmCustomPermissionsService = {
    dependencies: [],
    start() {
        if (!session.crm_custom_permissions_enabled) {
            return;
        }

        enforceRestriction();

        // MutationObserver to ensure class remains and any avatar/author popovers are removed
        const observer = new MutationObserver(() => {
            enforceRestriction();
            const popovers = document.querySelectorAll(".popover, .o_popover, .o_avatar_card, .o-mail-AvatarCardPopover, div[class*='AvatarCard']");
            popovers.forEach((popover) => {
                if (popover.querySelector(".o_avatar_card, .o-mail-AvatarCardPopover, [data-oe-model='res.partner'], button") || popover.classList.contains("o-mail-AvatarCardPopover")) {
                    popover.remove();
                }
            });
        });

        if (document.body) {
            observer.observe(document.body, { childList: true, subtree: true, attributes: true });
        }

        // Intercept clicks and mouse events on author links, avatars, and popovers
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
