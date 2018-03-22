
import jinja2

def app(self):
    app = Sanic(__name__)
    self.jinja = SanicJinja2(
        app,
        loader=FileSystemLoader([
            str(app_root / 'datasette' / 'templates')
        ]),
        autoescape=False,
    )
    self.jinja.add_env('escape_css_string', escape_css_string, 'filters')
    self.jinja.add_env('quote_plus', lambda u: urllib.parse.quote_plus(u), 'filters')
    self.jinja.add_env('escape_table_name', escape_sqlite_table_name, 'filters')
    app.add_route(IndexView.as_view(self), '/<as_json:(.jsono?)?$>')
    # TODO: /favicon.ico and /-/static/ deserve far-future cache expires
    app.add_route(favicon, '/favicon.ico')
    app.static('/-/static/', str(app_root / 'datasette' / 'static'))
    app.add_route(
        DatabaseView.as_view(self),
        '/<db_name:[^/\.]+?><as_json:(.jsono?)?$>'
    )
    app.add_route(
        DatabaseDownload.as_view(self),
        '/<db_name:[^/]+?><as_db:(\.db)$>'
    )
    app.add_route(
        TableView.as_view(self),
        '/<db_name:[^/]+>/<table:[^/]+?><as_json:(.jsono?)?$>'
    )
    app.add_route(
        RowView.as_view(self),
        '/<db_name:[^/]+>/<table:[^/]+?>/<pk_path:[^/]+?><as_json:(.jsono?)?$>'
    )
    return app
