from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


class ChatForm(FlaskForm):
    question = CKEditorField(label="", validators=[DataRequired()])
    submit = SubmitField("Send query")