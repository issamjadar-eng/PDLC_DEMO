class SlidePresentation {
    constructor() {
        this.slides = Array.from(document.querySelectorAll(".slide"));
        this.currentSlide = 0;
        this.progressBar = document.querySelector(".progress-bar");
        this.navDotsContainer = document.querySelector(".nav-dots");
        this.assignChromeNumbers();
        this.setupNavDots();
        this.setupIntersectionObserver();
        this.setupKeyboardNav();
        this.setupTouchNav();
        this.setupProgress();
        this.setupProvenanceModal();
    }
    assignChromeNumbers() {
        // Auto-number every chrome block by DOM position. Title slide skipped.
        let n = 1;
        this.slides.forEach((s) => {
            const chromeNum = s.querySelector(".chrome .chrome-num");
            if (chromeNum) {
                n += 1;
                chromeNum.textContent = String(n).padStart(2, "0");
            }
        });
    }
    setupNavDots() {
        this.navDotsContainer.innerHTML = "";
        this.slides.forEach((_, i) => {
            const b = document.createElement("button");
            b.className = "dot";
            b.setAttribute("aria-label", `Go to slide ${i + 1}`);
            if (i === 0) b.classList.add("active");
            b.addEventListener("click", () => this.goTo(i));
            this.navDotsContainer.appendChild(b);
        });
        this.dots = Array.from(this.navDotsContainer.querySelectorAll(".dot"));
    }
    setupIntersectionObserver() {
        const obs = new IntersectionObserver((entries) => {
            entries.forEach((e) => {
                if (e.isIntersecting && e.intersectionRatio > 0.5) {
                    e.target.classList.add("visible");
                    const idx = this.slides.indexOf(e.target);
                    if (idx >= 0) {
                        this.currentSlide = idx;
                        this.updateChrome();
                    }
                }
            });
        }, { threshold: [0.5] });
        this.slides.forEach((s) => obs.observe(s));
    }
    setupKeyboardNav() {
        document.addEventListener("keydown", (e) => {
            if (["ArrowDown", "ArrowRight", "PageDown", " "].includes(e.key)) {
                e.preventDefault();
                this.next();
            } else if (["ArrowUp", "ArrowLeft", "PageUp"].includes(e.key)) {
                e.preventDefault();
                this.prev();
            } else if (e.key === "Home") { e.preventDefault(); this.goTo(0); }
            else if (e.key === "End") { e.preventDefault(); this.goTo(this.slides.length - 1); }
            else if (e.key === "?") { e.preventDefault(); this.toggleProvenance(); }
        });
    }
    setupTouchNav() {
        let touchStartY = 0;
        document.addEventListener("touchstart", (e) => { touchStartY = e.touches[0].clientY; }, { passive: true });
        document.addEventListener("touchend", (e) => {
            const dy = touchStartY - e.changedTouches[0].clientY;
            if (Math.abs(dy) > 50) { dy > 0 ? this.next() : this.prev(); }
        });
    }
    setupProgress() {
        document.addEventListener("scroll", () => {
            const max = document.documentElement.scrollHeight - window.innerHeight;
            const pct = max > 0 ? (window.scrollY / max) * 100 : 0;
            this.progressBar.style.width = pct + "%";
        }, { passive: true });
    }
    setupProvenanceModal() {
        const modal = document.createElement("div");
        modal.className = "provenance-modal";
        modal.innerHTML = `
            <div class="provenance-card" role="dialog" aria-label="Deck provenance">
                <h3>Deck provenance</h3>
                <dl>
                    <dt>Source</dt><dd>${document.querySelector('meta[name="md-deck:source"]')?.content || ""}</dd>
                    <dt>SHA-256</dt><dd>${document.querySelector('meta[name="md-deck:source-sha256"]')?.content?.slice(0, 16) || ""}…</dd>
                    <dt>Built at</dt><dd>${document.querySelector('meta[name="md-deck:built-at"]')?.content || ""}</dd>
                    <dt>Built by</dt><dd>${document.querySelector('meta[name="md-deck:built-by"]')?.content || ""}</dd>
                    <dt>Style</dt><dd>${document.querySelector('meta[name="md-deck:style"]')?.content || ""}</dd>
                    <dt>Generator</dt><dd>${document.querySelector('meta[name="generator"]')?.content || ""}</dd>
                </dl>
                <p class="hint">Press ? to toggle · Esc to close</p>
            </div>`;
        modal.style.display = "none";
        document.body.appendChild(modal);
        modal.addEventListener("click", (e) => { if (e.target === modal) this.toggleProvenance(); });
        document.addEventListener("keydown", (e) => { if (e.key === "Escape") modal.style.display = "none"; });
        this.provenanceModal = modal;
    }
    toggleProvenance() {
        this.provenanceModal.style.display = this.provenanceModal.style.display === "none" ? "flex" : "none";
    }
    next() { if (this.currentSlide < this.slides.length - 1) this.goTo(this.currentSlide + 1); }
    prev() { if (this.currentSlide > 0) this.goTo(this.currentSlide - 1); }
    goTo(i) {
        this.currentSlide = i;
        this.slides[i].scrollIntoView({ behavior: "smooth" });
        this.updateChrome();
    }
    updateChrome() {
        this.dots.forEach((d, i) => d.classList.toggle("active", i === this.currentSlide));
    }
}
document.addEventListener("DOMContentLoaded", () => new SlidePresentation());
