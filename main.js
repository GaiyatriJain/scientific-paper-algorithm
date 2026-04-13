let pyodideReady = false;
let pyodide;

async function init() {
  pyodide = await loadPyodide();
  await pyodide.runPythonAsync(await (await fetch("paper_recommenderss.py")).text());
  pyodideReady = true;
  log("Ready.");
}

function log(text) {
  document.getElementById("terminal").textContent += text + "\n";
}

async function run() {
  if (!pyodideReady) return;
  document.getElementById("terminal").textContent = "";
  const q = document.getElementById("query").value;
  pyodide.globals.set("WEB_QUERY", q);
  await pyodide.runPythonAsync("run_web_query(WEB_QUERY)");
}

init();
