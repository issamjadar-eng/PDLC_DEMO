(function (global) {
  function escapeHtml(s) {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function inlineMd(s) {
    return s
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>");
  }

  function renderMarkdown(md) {
    const lines = md.split("\n");
    const out = [];
    let inList = false;
    let para = [];

    const flushPara = () => {
      if (para.length) {
        out.push("<p>" + inlineMd(para.join(" ")) + "</p>");
        para = [];
      }
    };
    const closeList = () => {
      if (inList) {
        out.push("</ul>");
        inList = false;
      }
    };

    for (const raw of lines) {
      const line = escapeHtml(raw);
      const bullet = /^\s*[-*]\s+(.*)$/.exec(line);
      const heading = /^(#{1,6})\s+(.*)$/.exec(line);

      if (bullet) {
        flushPara();
        if (!inList) {
          out.push("<ul>");
          inList = true;
        }
        out.push("<li>" + inlineMd(bullet[1]) + "</li>");
      } else if (heading) {
        flushPara();
        closeList();
        const level = Math.min(heading[1].length + 2, 6);
        out.push(`<h${level}>${inlineMd(heading[2])}</h${level}>`);
      } else if (line.trim() === "") {
        flushPara();
        closeList();
      } else {
        closeList();
        para.push(line);
      }
    }
    flushPara();
    closeList();
    return out.join("\n");
  }

  global.renderMarkdown = renderMarkdown;
})(window);
