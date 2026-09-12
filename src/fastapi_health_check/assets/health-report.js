(() => {
  "use strict";

  const runButton = document.querySelector("#run-diagnostic");
  if (!runButton) return;

  const statusClasses = ["healthy", "unhealthy", "degraded", "checking", "pending"];
  const records = () => [...document.querySelectorAll(".check-record")];

  const formatDuration = (durationMs) => {
    if (durationMs < 1) return `${(durationMs * 1000).toFixed(0)} µs`;
    if (durationMs < 1000) return `${durationMs.toFixed(2)} ms`;
    return `${(durationMs / 1000).toFixed(2)} s`;
  };

  const utcTime = () => `${new Date().toISOString().slice(11, 23)} UTC`;

  const updateRecord = (record, check, checkedAt) => {
    const isHealthy = check.status === "ok";
    const status = record.querySelector("[data-status]");
    const detailMessage = record.querySelector("[data-detail-message]");
    const message = check.message || "No diagnostic message returned";
    const duration = formatDuration(check.duration_ms);

    status.classList.remove(...statusClasses);
    status.classList.add(isHealthy ? "healthy" : "unhealthy");
    status.querySelector(".status__mark").textContent = "●";
    status.querySelector("[data-status-label]").textContent = isHealthy ? "healthy" : "unhealthy";
    record.querySelector("[data-latency]").textContent = duration;
    record.querySelector("[data-message]").textContent = message;
    record.querySelector("[data-detail-duration]").textContent = duration;
    record.querySelector("[data-detail-checked-at]").textContent = checkedAt;
    record.querySelector("[data-detail-message-key]").textContent = isHealthy ? "message" : "error";
    detailMessage.textContent = message;
    detailMessage.classList.toggle("trace__value--error", !isHealthy);
  };

  const setRunningState = () => {
    records().forEach((record) => {
      record.open = false;
      const status = record.querySelector("[data-status]");
      status.classList.remove(...statusClasses);
      status.classList.add("checking");
      status.querySelector(".status__mark").textContent = "◌";
      status.querySelector("[data-status-label]").textContent = "checking…";
      record.querySelector("[data-latency]").textContent = "—";
      record.querySelector("[data-message]").textContent = "Awaiting result";
    });
  };

  const updateTimestamp = () => {
    const timestamp = document.querySelector("#diagnostic-timestamp");
    const now = new Date();
    timestamp.dateTime = now.toISOString();
    timestamp.textContent = `${now.toISOString().slice(0, 10)} / ${utcTime()}`;
  };

  const runDiagnostic = async () => {
    runButton.disabled = true;
    runButton.firstChild.textContent = "Running diagnostic ";
    setRunningState();

    try {
      const response = await fetch(runButton.dataset.endpoint, {
        cache: "no-store",
        headers: { Accept: "application/json" },
      });
      const report = await response.json();
      const checkedAt = utcTime();
      records().forEach((record, index) => {
        if (report.checks[index]) updateRecord(record, report.checks[index], checkedAt);
      });
      updateTimestamp();
    } catch (_error) {
      records().forEach((record) => {
        const status = record.querySelector("[data-status]");
        status.classList.remove(...statusClasses);
        status.classList.add("unhealthy");
        status.querySelector(".status__mark").textContent = "●";
        status.querySelector("[data-status-label]").textContent = "unhealthy";
        record.querySelector("[data-latency]").textContent = "—";
        record.querySelector("[data-message]").textContent = "Diagnostic request failed";
      });
    } finally {
      runButton.disabled = false;
      runButton.firstChild.textContent = "Run diagnostic ";
    }
  };

  runButton.addEventListener("click", runDiagnostic);
})();
