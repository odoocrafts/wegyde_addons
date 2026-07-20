/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";

export class AccaListController extends ListController {
    setup() {
        super.setup();
        this.notification = useService("notification");
    }

    async onClickCopyUrl() {
        const url = browser.location.origin + "/acca/register";
        try {
            await browser.navigator.clipboard.writeText(url);
            this.notification.add("Public Registration URL copied to clipboard!", {
                type: "success",
            });
        } catch (error) {
            this.notification.add("Failed to copy URL to clipboard.", {
                type: "danger",
            });
        }
    }
}

registry.category("views").add("acca_registration_list", {
    ...listView,
    Controller: AccaListController,
    buttonTemplate: "acca_registration.ListButtons",
});
