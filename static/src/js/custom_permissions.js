/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";

const crmCustomPermissionsService = {
    dependencies: [],
    start() {
        if (session.crm_custom_permissions_enabled) {
            document.body.classList.add("o_crm_custom_permissions_restricted");
        }
    },
};

registry.category("services").add("crm_custom_permissions_service", crmCustomPermissionsService);
