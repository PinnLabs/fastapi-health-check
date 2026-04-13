from __future__ import annotations

from html import escape
from importlib.resources import files

from fastapi_health_check.models import HealthCheckResult, HealthReport

_ASSETS = files("fastapi_health_check.assets")
_HTML_TEMPLATE = (_ASSETS / "health-report.html").read_text(encoding="utf-8")
_CSS_STYLES = (_ASSETS / "health-report.css").read_text(encoding="utf-8")


def render_health_report_page(report: HealthReport, *, title: str = "FastAPI Health Check") -> str:
    summary_label = "Healthy" if report.is_healthy else "Issues detected"
    summary_class = "ok" if report.is_healthy else "fail"
    checks_markup = "\n".join(_render_check_card(check) for check in report.checks) or _render_empty_state()

    replacements = {
        "{{ title }}": escape(title),
        "{{ styles }}": _CSS_STYLES,
        "{{ summary_class }}": summary_class,
        "{{ summary_label }}": escape(summary_label),
        "{{ checks_count }}": str(len(report.checks)),
        "{{ checks_markup }}": checks_markup,
    }

    html = _HTML_TEMPLATE
    for marker, value in replacements.items():
        html = html.replace(marker, value)

    return html


def _render_check_card(check: HealthCheckResult) -> str:
    message = escape(check.message) if check.message else "No additional details."
    return f"""        <article class="check-card">
          <div class="check-header">
            <h2 class="check-name">{escape(check.name)}</h2>
            <div class="check-meta">
              <div class="badge {check.status}">{escape(check.status.upper())}</div>
              <span class="duration">{check.duration_ms:.3f} ms</span>
            </div>
          </div>
          <p class="message">{message}</p>
        </article>"""


def _render_empty_state() -> str:
    return '        <div class="empty">No health checks are currently registered.</div>'
