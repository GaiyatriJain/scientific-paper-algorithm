let pyodide;
let ready = false;

const terminal = document.getElementById("terminal");
const runBtn = document.getElementById("runBtn");

function log(msg) {
  terminal.textContent += msg + "\n";
}

async function init() {
  try {
    log("Initializing Pyodide...");
    pyodide = await loadPyodide();

    log("Loading Python file...");
    const pyCode = await (await fetch("paper_recommenderss.py")).text();
    await pyodide.runPythonAsync(pyCode);

    ready = true;
    runBtn.disabled = false;
    log("✅ Ready. Enter a query and press run.");
  } catch (err) {
    log("❌ Error during initialization:");
    log(err.toString());
  }
}

async function run() {
  if (!ready) {
    log("⚠️ Still loading...");
    return;
  }

  const query = document.getElementById("query").value;
  if (!query) {
    log("⚠️ Please enter a query.");
    return;
  }

  try {
    terminal.textContent = "";
    log("Running recommender...");
    pyodide.globals.set("WEB_QUERY", query);
    await pyodide.runPythonAsync(`run_web_query(WEB_QUERY)`);
    log("\n✅ Done.");
  } catch (err) {
    log("❌ Python error:");
    log(err.toString());
  }
}

init();
