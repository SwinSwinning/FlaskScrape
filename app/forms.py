from wtforms import StringField, SubmitField, IntegerField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange


class ScrapeForm(FlaskForm):
    start_url = StringField('URL to scrape', validators=[DataRequired()], default='https://store.playstation.com/nl-nl/pages/browse/1') 
    item_url = StringField('Link extractor',validators=[DataRequired()], default='//a[@class="psw-link psw-content-link"]') 
    next_page_url = StringField('next page url', default='//button[@data-qa="ems-sdk-grid#ems-sdk-top-paginator-root#next"]')
    next_page_url_add = StringField('next page url - value to extract', default='value')   # Possible to use a link extractor?
    num_of_attrs = IntegerField('number of Attributes to scrape', validators=[NumberRange(min=1, max=5)], default=1)
    
  
    attr1_name = StringField('Attribute name', validators=[DataRequired()], default='title')
    attr1_val = StringField('CSS selector', validators=[DataRequired()], default='h1.psw-m-b-5')
    attr1_add = StringField('CSS selector add', default='')    
    attr2_name = StringField('Attribute name', default='price')
    attr2_val = StringField('CSS selector Value', default='span[data-qa="mfeCtaMain#offer0#finalPrice"]')
    attr2_add = StringField('CSS selector add', default='')
    attr3_name = StringField('Attribute name', default='price')
    attr3_val = StringField('CSS selector Value', default='//a[@class="psw-link psw-content-link"]')
    attr3_add = StringField('CSS selector add', default='')
    attr4_name = StringField('Attribute name', default='link')
    attr4_val = StringField('CSS selector Value', default='//a[@class="psw-link psw-content-link"]')
    attr4_add = StringField('CSS selector add', default='')
    attr5_name = StringField('Attribute name', default='other')
    attr5_val = StringField('CSS selector Value',  default='//a[@class="psw-link psw-content-link"]')
    attr5_add = StringField('CSS selector add', default='')
    submit = SubmitField('Submit')







