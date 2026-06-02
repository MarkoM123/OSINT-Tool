from jinja2 import Environment, PackageLoader, select_autoescape

try:
	from weasyprint import HTML
except Exception:  # pragma: no cover - optional dep
	HTML = None


env = Environment(
	loader=PackageLoader("reporting", "templates"), autoescape=select_autoescape(["html", "xml"])
)


def render_report(context: dict) -> bytes:
	template = env.get_template("report.html")
	html = template.render(**context)
	if HTML:
		doc = HTML(string=html)
		return doc.write_pdf()
	# Fallback: return HTML bytes
	return html.encode("utf-8")
