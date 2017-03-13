from selenium import webdriver
from PIL import Image, ImageDraw
from seleniumrequests import PhantomJS

class ScreenshotMaker:
    
    logged_in_user = None

    def __init__(self, width=1200, height=768):
        self.height = height
        self.width = width
        self.reset_driver()

    def reset_driver(self):
        self.driver = PhantomJS()
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
            self.logout()

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
        hi_w = element.size['width']+margin
        hi_h = element.size['height']+margin
        highlighter = Image.new('RGBA', (hi_w, hi_h) )

        center_x = hi_w/2 # + left
        center_y = hi_h/2 # + top
        d=25
        draw = ImageDraw.Draw(highlighter)
        draw.ellipse(
            [(center_x-d, center_y-d), (center_x+d, center_y+d)],
            outline=(255,128,0,128),
            fill=(255,255,0,64),
        )
        draw.ellipse(
            [(center_x-(d+1), center_y-(d+1)), (center_x+(d+1), center_y+(d+1))],
            outline=(255,128,0,128),
        )
        del draw

        left = element.location['x'] - int(margin/2)
        top = element.location['y'] - int(margin/2)

        im.paste(highlighter, (left, top), mask=highlighter)
        im.save(filename) # saves new cropped image

    def crop(self, filename, crop):
        im = Image.open(filename) # uses PIL library to open image in memory
        im = im.crop(crop)
        im.save(filename) # saves new cropped image

    def hightlight_box(self, filename, selector):
        element = self.driver.find_element_by_css_selector(selector)
        im = Image.open(filename).convert('RGBA') # uses PIL library to open image in memory

        margin = 4
        hi_w = element.size['width']+margin
        hi_h = element.size['height']+margin
        highlighter = Image.new('RGBA', (hi_w, hi_h) )

        draw = ImageDraw.Draw(highlighter)
        for d in range(0,int(margin/2)+1):
            draw.rectangle(
                [(d, d), (hi_w-(d+1), hi_h-(d+1))],
                outline=(256,64,64,256),
            )
        del draw

        left = element.location['x'] - int(margin/2)
        top = element.location['y'] - int(margin/2)

        im.paste(highlighter, (left, top), mask=highlighter)
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
