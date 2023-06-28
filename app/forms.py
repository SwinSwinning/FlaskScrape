
from wtforms import StringField, SubmitField, FormField, IntegerField, RadioField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange
from wtforms.fields import FieldList


class AttributeForm(FlaskForm):
    fieldname = StringField("Attribute Name", validators=[DataRequired()], default="name")
    selector_code = StringField("Selector Code", validators=[DataRequired()], default='//td[@class="name"]')
    
class MulAttrForm(FlaskForm):
    """A form for one or more addresses"""
    attributes = FieldList(FormField(AttributeForm, separator='_'), min_entries=1, max_entries=5)
    submit = SubmitField('Download')


class ScrapeForm(FlaskForm):
    start_url = StringField('URL to scrape', validators=[DataRequired()], default='https://store.playstation.com/nl-nl/pages/browse/1') # UrL validator?
    item_url = StringField('Link extractor', default='//a[@class="psw-link psw-content-link"]') # regex checking the format
    next_page_url = StringField('next page url', default='//button[@data-qa="ems-sdk-grid#ems-sdk-top-paginator-root#next"]')
    num_of_attrs = IntegerField('number of Attributes to scrape', validators=[NumberRange(min=1, max=5)], default=1)
    
    # attributes = FieldList(FormField(AttributeForm), min_entries=1)
    attr1_name = StringField('Attribute name', validators=[DataRequired()], default='title')
    attr1_val = StringField('CSS selector Value', validators=[DataRequired()], default='h1.psw-m-b-5')
    attr2_name = StringField('Attribute name', default='price')
    attr2_val = StringField('CSS selector Value', default='span[data-qa="mfeCtaMain#offer0#finalPrice"]')
    attr3_name = StringField('Attribute name', default='price')
    attr3_val = StringField('CSS selector Value', default='//a[@class="psw-link psw-content-link"]')
    attr4_name = StringField('Attribute name', default='link')
    attr4_val = StringField('CSS selector Value', default='//a[@class="psw-link psw-content-link"]')
    attr5_name = StringField('Attribute name', default='other')
    attr5_val = StringField('CSS selector Value',  default='//a[@class="psw-link psw-content-link"]')

    submit = SubmitField('Submit')







