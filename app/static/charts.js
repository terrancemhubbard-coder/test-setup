// Minimal dependency-free SVG line chart for trend data.
// datasets: [{ label, color, data: [{x: isoString, y: number}] }]
function renderLineChart(containerId, datasets, opts) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const points = datasets.flatMap((d) => d.data);
  if (points.length === 0) {
    container.innerHTML = '<p class="empty">No data yet.</p>';
    return;
  }

  const width = (opts && opts.width) || container.clientWidth || 600;
  const height = (opts && opts.height) || 220;
  const padding = { top: 16, right: 16, bottom: 28, left: 44 };

  const xs = points.map((p) => new Date(p.x).getTime());
  const ys = points.map((p) => p.y);
  let xMin = Math.min(...xs);
  let xMax = Math.max(...xs);
  if (xMin === xMax) { xMin -= 1; xMax += 1; }
  let yMin = Math.min(...ys);
  let yMax = Math.max(...ys);
  const yPad = (yMax - yMin) * 0.15 || 1;
  yMin -= yPad;
  yMax += yPad;

  const xScale = (t) => padding.left + ((t - xMin) / (xMax - xMin)) * (width - padding.left - padding.right);
  const yScale = (v) => height - padding.bottom - ((v - yMin) / (yMax - yMin)) * (height - padding.top - padding.bottom);

  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("width", "100%");
  svg.setAttribute("height", height);

  const gridColor = "var(--border, #ccc)";
  const textColor = "var(--muted, #666)";

  // horizontal gridlines + y labels
  const steps = 4;
  for (let i = 0; i <= steps; i++) {
    const v = yMin + ((yMax - yMin) * i) / steps;
    const y = yScale(v);
    const line = document.createElementNS(svgNS, "line");
    line.setAttribute("x1", padding.left);
    line.setAttribute("x2", width - padding.right);
    line.setAttribute("y1", y);
    line.setAttribute("y2", y);
    line.setAttribute("stroke", gridColor);
    line.setAttribute("stroke-width", "1");
    svg.appendChild(line);

    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("x", padding.left - 6);
    label.setAttribute("y", y + 3);
    label.setAttribute("text-anchor", "end");
    label.setAttribute("font-size", "10");
    label.setAttribute("fill", textColor);
    label.textContent = Math.round(v * 10) / 10;
    svg.appendChild(label);
  }

  // x labels: first and last timestamp
  [xMin, xMax].forEach((t, idx) => {
    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("x", xScale(t));
    label.setAttribute("y", height - 6);
    label.setAttribute("text-anchor", idx === 0 ? "start" : "end");
    label.setAttribute("font-size", "10");
    label.setAttribute("fill", textColor);
    label.textContent = new Date(t).toLocaleDateString();
    svg.appendChild(label);
  });

  datasets.forEach((dataset) => {
    if (dataset.data.length === 0) return;
    const sorted = [...dataset.data].sort((a, b) => new Date(a.x) - new Date(b.x));
    const path = sorted
      .map((p, i) => `${i === 0 ? "M" : "L"}${xScale(new Date(p.x).getTime())},${yScale(p.y)}`)
      .join(" ");
    const pathEl = document.createElementNS(svgNS, "path");
    pathEl.setAttribute("d", path);
    pathEl.setAttribute("fill", "none");
    pathEl.setAttribute("stroke", dataset.color || "var(--accent, #2563eb)");
    pathEl.setAttribute("stroke-width", "2");
    svg.appendChild(pathEl);

    sorted.forEach((p) => {
      const circle = document.createElementNS(svgNS, "circle");
      circle.setAttribute("cx", xScale(new Date(p.x).getTime()));
      circle.setAttribute("cy", yScale(p.y));
      circle.setAttribute("r", "3");
      circle.setAttribute("fill", dataset.color || "var(--accent, #2563eb)");
      const title = document.createElementNS(svgNS, "title");
      title.textContent = `${new Date(p.x).toLocaleString()}: ${p.y}${dataset.label ? " " + dataset.label : ""}`;
      circle.appendChild(title);
      svg.appendChild(circle);
    });
  });

  container.innerHTML = "";
  container.appendChild(svg);

  if (datasets.length > 1) {
    const legend = document.createElement("div");
    legend.style.display = "flex";
    legend.style.gap = "1rem";
    legend.style.fontSize = "0.8rem";
    legend.style.marginTop = "0.3rem";
    datasets.forEach((d) => {
      const item = document.createElement("span");
      item.style.color = d.color || "";
      item.textContent = "● " + d.label;
      legend.appendChild(item);
    });
    container.appendChild(legend);
  }
}
