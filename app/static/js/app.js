/**
 * Multi-Document Contradiction and Consensus Analyzer - Core UI Logic
 */

const Icons = {
    PLUS: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,
    UPLOAD: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>`,
    REFRESH: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 4v6h-6"></path><path d="M1 20v-6h6"></path><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>`,
    PLAY: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>`,
    TRASH: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>`,
    DOC: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`,
    INFO: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
    SHIELD: `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`
};

document.addEventListener("DOMContentLoaded", () => {
    const docsContainer = document.getElementById("docs");
    const statsDiv = document.getElementById("stats");
    const claimsDiv = document.getElementById("claims");
    const relationsSummaryDiv = document.getElementById("relationsSummary");
    const errorDiv = document.getElementById("error");
    const uploadDocsBtn = document.getElementById("uploadDocsBtn");
    const uploadDocsInput = document.getElementById("uploadDocsInput");
    const resetDocsBtn = document.getElementById("resetDocsBtn");
    const addDocBtn = document.getElementById("addDoc");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const dropzone = document.getElementById("dropzone");

    // Add icons to buttons
    addDocBtn.innerHTML = `${Icons.PLUS} Add Document`;
    uploadDocsBtn.innerHTML = `${Icons.UPLOAD} Upload Files`;
    resetDocsBtn.innerHTML = `${Icons.REFRESH} Reset Sample`;
    analyzeBtn.innerHTML = `${Icons.PLAY} Run Analysis`;
    dropzone.innerHTML = `${Icons.UPLOAD} <span>Drag & Drop files or click to upload</span>`;

    function createSnippetList(items) {
        if (!items || items.length === 0) {
            return '<div class="empty">No snippets available</div>';
        }
        return `<ul class="snippets">${items.slice(0, 5).map((i) => `<li>${i}</li>`).join("")}</ul>`;
    }

    function addDocumentCard(defaultSource = "", defaultText = "") {
        const wrapper = document.createElement("div");
        wrapper.className = "doc";

        const count = document.querySelectorAll(".doc").length + 1;

        wrapper.innerHTML = `
            <div class="doc-head">
                <span class="doc-number">Document ${count}</span>
                <button type="button" class="btn-danger remove-doc">${Icons.TRASH}</button>
            </div>
            <div class="input-group">
                <label>Source</label>
                <input type="text" class="source" placeholder="e.g. Research Paper / Article A" value="${defaultSource}">
            </div>
            <div class="input-group">
                <label>Content</label>
                <textarea class="text" placeholder="Paste document content here...">${defaultText}</textarea>
            </div>
        `;

        docsContainer.appendChild(wrapper);
        refreshDocHeadings();
    }

    function refreshDocHeadings() {
        document.querySelectorAll(".doc").forEach((doc, idx) => {
            doc.querySelector(".doc-number").textContent = `Document ${idx + 1}`;
        });
    }

    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.style.display = "block";
        errorDiv.className = "panel btn-danger"; // Reuse styles
        errorDiv.style.marginTop = "12px";
        errorDiv.scrollIntoView({ behavior: 'smooth' });
    }

    function hideError() {
        errorDiv.style.display = "none";
    }

    docsContainer.addEventListener("click", (event) => {
        const removeBtn = event.target.closest(".remove-doc");
        if (!removeBtn) return;

        const allDocs = document.querySelectorAll(".doc");
        if (allDocs.length <= 3) {
            showError("A minimum of 3 documents is required for meaningful analysis.");
            return;
        }

        const card = removeBtn.closest(".doc");
        if (card) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.remove();
                refreshDocHeadings();
            }, 300);
        }
    });

    function initDefaults() {
        docsContainer.innerHTML = "";
        addDocumentCard(
            "Medical Report A",
            "The vaccine reduces severe disease in adults. Clinical studies confirm the vaccine reduces severe disease in adult participants."
        );
        addDocumentCard("Policy Study B", "The carbon tax policy reduces national emissions by 20 percent according to 2024 projections.");
        addDocumentCard("Criticism Report C", "Independent analysis suggests the carbon tax policy does not reduce national emissions by 20 percent.");
    }

    async function uploadAndParseFiles(fileList) {
        const files = Array.from(fileList || []);
        if (files.length === 0) return;

        hideError();
        const formData = new FormData();
        files.forEach((file) => formData.append("files", file));

        try {
            uploadDocsBtn.disabled = true;
            uploadDocsBtn.innerHTML = `<div class="spinner" style="width:16px; height:16px; margin:0"></div> Processing...`;

            const response = await fetch("/upload-documents", {
                method: "POST",
                body: formData
            });
            const payload = await response.json();
            
            if (!response.ok) throw new Error(payload.detail || "Upload failed.");

            const docs = payload.documents || [];
            if (docs.length === 0) {
                showError("No readable content found in selected files.");
                return;
            }
            docs.forEach((doc) => addDocumentCard(doc.source || "Uploaded Document", doc.text || ""));
        } catch (error) {
            showError(error.message || "Upload failed.");
        } finally {
            uploadDocsBtn.disabled = false;
            uploadDocsBtn.innerHTML = `${Icons.UPLOAD} Upload Files`;
        }
    }

    addDocBtn.addEventListener("click", () => {
        addDocumentCard();
        hideError();
    });

    uploadDocsBtn.addEventListener("click", () => uploadDocsInput.click());

    uploadDocsInput.addEventListener("change", async (event) => {
        await uploadAndParseFiles(event.target.files);
        uploadDocsInput.value = "";
    });

    ["dragenter", "dragover"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            event.stopPropagation();
            dropzone.classList.add("active");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            event.stopPropagation();
            dropzone.classList.remove("active");
        });
    });

    dropzone.addEventListener("drop", async (event) => {
        const files = event.dataTransfer ? event.dataTransfer.files : null;
        await uploadAndParseFiles(files);
    });

    dropzone.addEventListener("click", () => uploadDocsInput.click());

    resetDocsBtn.addEventListener("click", () => {
        hideError();
        initDefaults();
        statsDiv.innerHTML = "";
        relationsSummaryDiv.innerHTML = "";
        claimsDiv.innerHTML = "";
    });

    analyzeBtn.addEventListener("click", async () => {
        hideError();
        const docs = [...document.querySelectorAll(".doc")].map((el) => ({
            source: el.querySelector(".source").value.trim(),
            text: el.querySelector(".text").value.trim()
        })).filter((d) => d.source && d.text);

        if (docs.length < 3) {
            showError("Please provide at least 3 complete documents with source and text.");
            return;
        }

        // Show loading state
        const resultsPanel = claimsDiv.closest('.panel');
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `<div class="spinner"></div><p>Analyzing cross-document relationships...</p>`;
        resultsPanel.style.position = 'relative';
        resultsPanel.appendChild(overlay);

        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = `<div class="spinner" style="width:16px; height:16px; margin:0"></div> Analyzing...`;

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ documents: docs })
            });
            if (!response.ok) {
                const msg = await response.text();
                throw new Error(msg || "Request failed.");
            }
            const result = await response.json();
            renderResult(result);
        } catch (err) {
            showError(`Analysis failed: ${err.message}`);
        } finally {
            overlay.remove();
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = `${Icons.PLAY} Run Analysis`;
        }
    });

    function renderResult(result) {
        const stats = result.stats || {};
        const relations = result.relations || [];
        const entailmentCount = relations.filter((r) => r.label === "entailment").length;
        const contradictionCount = relations.filter((r) => r.label === "contradiction").length;

        statsDiv.innerHTML = `
            <div class="stat"><div class="k">Docs</div><div class="v">${stats.document_count || 0}</div></div>
            <div class="stat"><div class="k">Sentences</div><div class="v">${stats.sentence_count || 0}</div></div>
            <div class="stat"><div class="k">Claims</div><div class="v">${stats.claim_count || 0}</div></div>
            <div class="stat"><div class="k">Relations</div><div class="v">${stats.relation_count || 0}</div></div>
            <div class="stat"><div class="k">Clusters</div><div class="v">${stats.cluster_count || 0}</div></div>
        `;

        relationsSummaryDiv.innerHTML = `
            <span class="badge badge-ent">${Icons.SHIELD} Consensus Agreements: ${entailmentCount}</span>
            <span class="badge badge-con">${Icons.INFO} Contradictions Found: ${contradictionCount}</span>
        `;

        claimsDiv.innerHTML = "";
        const sortedClaims = [...(result.claims || [])].sort((a, b) => (b.confidence || 0) - (a.confidence || 0));

        sortedClaims.forEach((claim, index) => {
            const confidence = Number(claim.confidence || 0);
            const confidencePct = Math.max(0, Math.min(100, Math.round(confidence * 100)));
            
            const card = document.createElement("article");
            card.className = "claim";
            card.style.animationDelay = `${index * 0.1}s`;
            
            card.innerHTML = `
                <div class="claim-header">
                    <p class="claim-text">${claim.text}</p>
                    <div class="claim-meta">
                        <span class="meta-item">${Icons.DOC} ${claim.source}</span>
                        <span class="meta-item">${Icons.INFO} Cluster: ${claim.cluster_id}</span>
                        <span class="meta-item">${Icons.SHIELD} Support: ${claim.support_count}</span>
                    </div>
                </div>
                
                <div class="confidence-section">
                    <div class="confidence-label">
                        <span>Analysis Confidence</span>
                        <span>${confidencePct}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%"></div>
                    </div>
                </div>

                <details>
                    <summary>Supporting Evidence (${claim.supporting_snippets?.length || 0})</summary>
                    ${createSnippetList(claim.supporting_snippets)}
                </details>
                <details>
                    <summary>Contradicting Viewpoints (${claim.contradicting_snippets?.length || 0})</summary>
                    ${createSnippetList(claim.contradicting_snippets)}
                </details>
            `;
            
            claimsDiv.appendChild(card);
            
            // Animate progress bar after append
            setTimeout(() => {
                card.querySelector('.progress-fill').style.width = `${confidencePct}%`;
            }, 100);
        });

        if (sortedClaims.length === 0) {
            claimsDiv.innerHTML = `
                <div class="panel" style="grid-column: 1/-1; text-align: center; background: rgba(255,255,255,0.02)">
                    <p class="subtitle">No cross-document claims were extracted. Try adding more specific content.</p>
                </div>`;
        }
        
        // Scroll to results
        statsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    // Initialize with defaults
    initDefaults();
});
