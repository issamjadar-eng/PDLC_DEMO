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

    let inTable = false;
    let tableHead = false;

    const closeTable = () => {
      if (inTable) {
        out.push("</tbody></table>");
        inTable = false;
        tableHead = false;
      }
    };

    const isTableRow = (l) => l.trim().startsWith("|") && l.trim().endsWith("|");
    const isSeparator = (l) => /^\|[\s:|-]+\|$/.test(l.trim());
    const parseRow = (l, tag) => {
      const cells = l.trim().replace(/^\||\|$/g, "").split("|");
      return "<tr>" + cells.map(c => `<${tag}>${inlineMd(c.trim())}</${tag}>`).join("") + "</tr>";
    };

    for (const raw of lines) {
      const line = escapeHtml(raw);
      const bullet = /^\s*[-*]\s+(.*)$/.exec(line);
      const heading = /^(#{1,6})\s+(.*)$/.exec(line);

      if (isTableRow(line)) {
        flushPara();
        closeList();
        if (isSeparator(line)) {
          tableHead = true;
          continue;
        }
        if (!inTable) {
          out.push('<table class="md-table"><thead>');
          out.push(parseRow(line, "th"));
          out.push("</thead><tbody>");
          inTable = true;
          continue;
        }
        out.push(parseRow(line, "td"));
      } else if (bullet) {
        flushPara();
        closeTable();
        if (!inList) {
          out.push("<ul>");
          inList = true;
        }
        out.push("<li>" + inlineMd(bullet[1]) + "</li>");
      } else if (heading) {
        flushPara();
        closeList();
        closeTable();
        const level = Math.min(heading[1].length + 2, 6);
        out.push(`<h${level}>${inlineMd(heading[2])}</h${level}>`);
      } else if (line.trim() === "") {
        flushPara();
        closeList();
        closeTable();
      } else {
        closeList();
        closeTable();
        para.push(line);
      }
    }
    flushPara();
    closeList();
    closeTable();
    return out.join("\n");
  }

  global.renderMarkdown = renderMarkdown;
})(window);
