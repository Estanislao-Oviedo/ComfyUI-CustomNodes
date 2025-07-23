import { app } from "../../scripts/app.js";

const _PREFIX = "region_spec";
const _TYPE = "REGION_SPEC";

app.registerExtension({
    name: "Custom.RegionConditionMerge.DynamicInputs",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "RegionConditionMerge") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const me = onNodeCreated?.apply(this);
            // Add the first dynamic input
            this.addInput(_PREFIX + "1", _TYPE);
            return me;
        };

        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function (slotType, slot_idx, event, link_info, node_slot) {
            const me = onConnectionsChange?.apply(this, arguments);

            // Only handle input slots
            if (slotType === 1) {
                // Count connected region_spec slots
                let count = 1;
                while (this.inputs.find(i => i.name === `${_PREFIX}${count}` && i.link != null)) {
                    count++;
                }
                // Add a new slot if the last is connected
                if (!this.inputs.find(i => i.name === `${_PREFIX}${count}`)) {
                    this.addInput(`${_PREFIX}${count}`, _TYPE);
                }
                // Optionally, remove unused slots (not strictly necessary)
            }
            this?.graph?.setDirtyCanvas(true);
            return me;
        };
        return nodeType;
    }
});