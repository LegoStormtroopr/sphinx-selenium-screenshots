from selenium import webdriver
from PIL import Image, ImageDraw
from importlib import import_module

def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    module_path, class_name = dotted_path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, class_name)

class ScreenshotMaker:
    
    logged_in_user = None

    def __init__(self, width=1200, height=800, driver="selenium.webdriver.PhantomJS"):
        self.driver_class = import_string(driver)
        self.height = height
        self.width = width
        self.reset_driver()

    def reset_driver(self, driver_class=None):
        if driver_class is not None:
            self.driver_class = import_string(driver_class)
        self.driver = self.driver_class()
        self.driver.set_window_size(self.width, self.height)

    def set_browser_height(self, height):
        self.height = height
        self.driver.set_window_size(self.width, self.height)

    def mobile(self, height=800, width=600):
        self.set_viewport_size(width=width, height=height)

    def set_viewport_size(self, width, height):
        window_size = self.driver.execute_script("""
            return [window.outerWidth - window.innerWidth + arguments[0],
              window.outerHeight - window.innerHeight + arguments[1]];
            """, width, height)
        self.driver.set_window_size(*window_size)

    def do_forms(self, form_data):
        for form in form_data:
            for field, data in form.items():
                if field != '__submit__':
                    input_field = self.driver.find_element_by_css_selector('*[name="%s"]'%field)
                    #username_input.send_keys(username)
                    self.driver.execute_script(
                        "arguments[0].value = '" + data +"'", input_field
                    )
            if form.get('__submit__', True):
                input_field.submit()

    def login(self, url, username, password):
        if self.logged_in_user == username:
            return
        elif self.logged_in_user is not None:
            self.logout(self.default_logout_path)

        self.driver.get(url)
        username_input = self.driver.find_element_by_css_selector('input[name="username"]')
        username_input.send_keys(username)
        password_input = self.driver.find_element_by_css_selector('input[name="password"]')
        password_input.send_keys(password)
        password_input.submit()
        self.logged_in_user = username

    def logout(self, url):
        self.driver.get(url)
        self.logged_in_user = None

    def capture_page(self, filename, url, preamble=None, form_data=None, login=None, logout=None, **kwargs):
        if login is not None:
            self.login(**login)

        if kwargs.get('browser_height', None):
            self.set_browser_height(kwargs.get('browser_height'))

        if url is not None:
            self.driver.get(url)
        if form_data:
            self.do_forms(form_data)
        browser = self.driver
        if preamble:
            for line in preamble:
                exec(line)
        self.driver.save_screenshot(filename) # save a screenshot to disk
    
        if kwargs.get('box', None):
            self.hightlight_box(filename, kwargs.get('box'))
        if kwargs.get('clicker', None):
            self.clicker(filename, kwargs.get('clicker'))
        if kwargs.get('crop', None):
            self.crop(filename, kwargs.get('crop'))
        if kwargs.get('crop_element', None):
            self.crop_element(filename, kwargs.get('crop_element'))
        if logout:
            self.logout(**logout)

    def clicker(self, filename, selector):
        element = self.driver.find_element_by_css_selector(selector)
        im = Image.open(filename).convert('RGBA') # uses PIL library to open image in memory

        margin = 40
        hi_w = element.size['width']
        hi_h = element.size['height']
        highlighter = Image.new('RGBA', (hi_w+margin, hi_h+margin) )

        r=12  # radius of the dot in pixels
        center_x = int(hi_w - max(r+1, hi_h/11 * 2) + margin/2) # + left
        center_y = int(hi_h - max(r+1, hi_h/11 * 5) + margin/2) # + top

        draw = ImageDraw.Draw(highlighter)
        draw.ellipse(
            [(center_x-r, center_y-r), (center_x+r, center_y+r)],
            outline=(203, 75, 22,200),
            fill=(203, 75, 22,128),
        )
        draw.ellipse(
            [(center_x-(r+1), center_y-(r+1)), (center_x+(r+1), center_y+(r+1))],
            outline=(203, 75, 22,200),
        )
        del draw

        left = element.location['x'] - int(margin/2)
        top = element.location['y'] - int(margin/2)

        im.paste(highlighter, (int(left), int(top)), mask=highlighter)
        im.save(filename) # saves new cropped image

    def crop(self, filename, crop):
        im = Image.open(filename) # uses PIL library to open image in memory
        im = im.crop(crop)
        im.save(filename) # saves new cropped image

    def hightlight_box(self, filename, selector):
        element = self.driver.find_element_by_css_selector(selector)
        im = Image.open(filename).convert('RGBA') # uses PIL library to open image in memory

        margin = 28
        side = int(margin/2)-1
        hi_w = element.size['width']+margin
        hi_h = element.size['height']+margin
        highlighter = Image.new('RGBA', (hi_w, hi_h) )

        draw = ImageDraw.Draw(highlighter)
        for d in range(side-4,side-1):
            draw.rectangle(
                [(d, d), (hi_w-(d+1), hi_h-(d+1))],
                outline=(38, 139, 210, 250),
            )
        for d in range(1,side-4):
            draw.rectangle(
                [(d, d), (hi_w-(d+1), hi_h-(d+1))],
                outline=(38, 139, 210,
                    int(
                        200/(side-4)*d
                    )
                ),
            )
        del draw

        left = element.location['x'] - side
        top = element.location['y'] - side

        im.paste(highlighter, (int(left), int(top)), mask=highlighter)
        im.save(filename) # saves new cropped image

    def crop_element(self, filename, element_selector):
        element = self.driver.find_element_by_css_selector(element_selector)

        im = Image.open(filename) # uses PIL library to open image in memory
        
        delta_x = 50
        delta_y = 50
        left = element.location['x'] - delta_x
        top = element.location['y'] - delta_y
        right = element.location['x'] + element.size['width'] + delta_x
        bottom = element.location['y'] + element.size['height'] + delta_y

        self.crop(filename, (left, top, right, bottom)) # defines crop points
        # im.save(filename) # saves new cropped image


    def capture_element(self, filename, url, element_selector, preamble=None):
        element = self.driver.find_element_by_css_selector(element_selector)
        element.screenshot(filename) # saves screenshot of entire page
        
        im = Image.open(filename) # uses PIL library to open image in memory
        
        delta_x = 50
        delta_y = 50
        left = element.location['x'] - delta_x
        top = element.location['y'] - delta_y
        right = element.location['x'] + element.size['width'] + delta_x
        bottom = element.location['y'] + element.size['height'] + delta_y

        im = im.crop((left, top, right, bottom)) # defines crop points
        im.save(filename) # saves new cropped image

if __name__ == "__main__":
    s = ScreenshotMaker()
    s.capture_page('screens.png', url='http://registry.aristotlemetadata.com')
    s.capture_element('login.png', url='http://registry.aristotlemetadata.com', element_selector='a.login') #, padding=())
