import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "SaveCompressedWeppy.ContextMenu",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        const origGetExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
        nodeType.prototype.getExtraMenuOptions = function (_, options) {
            if (origGetExtraMenuOptions) {
                origGetExtraMenuOptions.apply(this, arguments);
            }
            if (this.imgs && this.imgs.length > 0) {
                let imageIndex = (this.imageIndex != null) ? this.imageIndex : (this.overIndex != null ? this.overIndex : this.imgs.length - 1);
                options.push({
                    content: "Save Compressed Weppy",
                    callback: async () => {
                        let img = this.imgs[imageIndex];
                        if (!img || !img.src) return;
                        
                        let url = new URL(img.src);
                        let filename = url.searchParams.get("filename");
                        let type = url.searchParams.get("type");
                        let subfolder = url.searchParams.get("subfolder") || "";
                        
                        if (!filename) return;

                        const p = await app.graphToPrompt();
                        const prompt = p.output;
                        const workflow = p.workflow;

                        try {
                            const response = await fetch("/save_compressed_weppy", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                },
                                body: JSON.stringify({
                                    filename,
                                    type,
                                    subfolder,
                                    prompt,
                                    workflow
                                })
                            });
                            
                            if (response.ok) {
                                const result = await response.json();
                                if (result.status === "success") {
                                    console.log("Saved WebP successfully:", result.filename);
                                } else {
                                    console.error("Failed to save WebP:", result.message);
                                }
                            } else {
                                console.error("HTTP error when saving WebP:", response.status);
                            }
                        } catch (e) {
                            console.error("Error saving WebP:", e);
                        }
                    }
                });
            }
        };
    }
});
