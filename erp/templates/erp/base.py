# System Blueprint Architecture Framework Template Engine Interface Structuring Helper File
def render_nav_items(items):
    """Generates structural safe HTML navigation sequence frames cleanly mapped on standard loop executions patterns."""
    html = ""
    for item in items:
        html += f"""
        <li class="nav-item mb-2">
            <a class="nav-link rounded-3 d-flex align-items-center px-3 py-2 {'active' if item['active'] else ''}" href="{item['url']}">
                <i class="bi {item['icon']} me-3 fs-5"></i>
                <span>{item['title']}</span>
            </a>
        </li>
        """
    return html