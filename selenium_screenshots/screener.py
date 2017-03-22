import os

def setup(app):
    app.add_config_value('screenshots_server_path', 'localhost', 'html')
    app.add_config_value('screenshots_save_path', '.', 'html')
    app.add_config_value('screenshots_read_path', '.', 'html')
    app.add_config_value('screenshots_logout_path', '/logout/', 'html')
    app.add_config_value('screenshots_driver', 'selenium.webdriver.PhantomJS', 'html')

    app.add_directive('screenshot', ScreenshotPageDirective)
    # app.connect('doctree-resolved', process_todo_nodes)
    # app.connect('env-purge-doc', purge_todos)

    return {'version': '0.1'}   # identifies the version of our extension


from docutils.parsers.rst import Directive, directives

try:
    from .screenshot import ScreenshotMaker
    s = ScreenshotMaker()
except:
    raise
    # We could be on readthedocs, lets hope files are in the right places
    s = None

from sphinx.util.compat import make_admonition
from sphinx.locale import _


from docutils.parsers.rst.directives import images, html, tables


class ScreenshotDirectiveBase(images.Image):
    # this enables content in the directive
    has_content = True

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    def pre_run(self):
        self.env = self.state.document.settings.env
        self.server = self.env.config['screenshots_server_path']
        s.reset_driver(driver_class=self.env.config['screenshots_driver'])
        s.default_logout_path = self.env.config['screenshots_server_path']+self.env.config['screenshots_logout_path']

        if len(self.arguments) > 0:
            reference = directives.uri(self.arguments[0])
            self.filename = reference
            self.options['uri'] = reference
        else:
            self.filename = "screenshot-%s-%d.%s" % (
                self.env.docname.replace('/','--'),
                self.env.new_serialno('screenshots'),
                'png'
            )
            self.arguments.append(None)

        self.arguments[0] = os.path.join(
            self.env.config['screenshots_read_path'],
            self.filename
        )
        return []

    def get_filename(self, name=None):
        if name is None:
            name = self.filename
        return os.path.join(
            self.env.config['screenshots_save_path'],
            name
        )

    def option_as_literal(self, option):
        d = self.options.get(option)
        if d:
            d = literal_eval(d)
        return d

    def option_as_dict_url(self, option):
        d = self.option_as_literal(option)
        if d:
            d['url'] = self.server+d['url']
        return d

from ast import literal_eval

class ScreenshotPageDirective(ScreenshotDirectiveBase):

    option_spec = images.Image.option_spec.copy()
    option_spec['server_path'] = directives.unchanged
    option_spec['form_data'] = directives.unchanged
    option_spec['login'] = directives.unchanged
    option_spec['logout'] = directives.unchanged
    option_spec['clicker'] = directives.unchanged
    option_spec['box'] = directives.unchanged
    option_spec['crop'] = directives.unchanged
    option_spec['crop_element'] = directives.unchanged
    option_spec['browser_height'] = directives.unchanged


    def run(self):
        out = super(ScreenshotPageDirective, self).pre_run()

        server_path = self.options.get('server_path')
        if server_path is not None and not server_path.startswith(('http://','https://')):
            server_path = self.server+self.options['server_path']

        if s is not None:
            s.capture_page(
                filename = self.get_filename(),
                url=server_path,
                preamble=self.content,
                form_data=self.option_as_literal('form_data'),
                login=self.option_as_dict_url('login'),
                logout=self.option_as_dict_url('logout'),
                clicker=self.options.get('clicker'),
                box=self.options.get('box'),
                height=self.options.get('browser_height'),
                crop=self.option_as_literal('crop'),
                crop_element=self.options.get('crop_element'),
            )
        return super(ScreenshotPageDirective, self).run()
