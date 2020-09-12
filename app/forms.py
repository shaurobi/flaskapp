from flask_wtf import FlaskForm
from wtforms.fields import  SelectField, SubmitField, StringField, PasswordField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo

class ExampleForm(FlaskForm):
    ExampleField = StringField('Example', validators=[DataRequired()])
    submit = SubmitField('Submit')