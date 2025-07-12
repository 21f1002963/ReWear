# -*- encoding: utf-8 -*-
"""
Item forms for ReWear platform
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class AddItemForm(FlaskForm):
    title = StringField('Item Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=100, message='Title must be between 3 and 100 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500, message='Description cannot exceed 500 characters')
    ])
    
    category = SelectField('Category', validators=[DataRequired()], choices=[
        ('', 'Select Category'),
        ('tops', 'Tops'),
        ('bottoms', 'Bottoms'),
        ('dresses', 'Dresses'),
        ('outerwear', 'Outerwear'),
        ('shoes', 'Shoes'),
        ('accessories', 'Accessories'),
        ('activewear', 'Activewear'),
        ('formal', 'Formal Wear'),
        ('casual', 'Casual Wear'),
        ('vintage', 'Vintage'),
        ('other', 'Other')
    ])
    
    size = SelectField('Size', validators=[DataRequired()], choices=[
        ('', 'Select Size'),
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
        ('xxl', 'XXL'),
        ('xxxl', 'XXXL'),
        ('28', '28'),
        ('30', '30'),
        ('32', '32'),
        ('34', '34'),
        ('36', '36'),
        ('38', '38'),
        ('40', '40'),
        ('42', '42'),
        ('44', '44'),
        ('46', '46'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('one-size', 'One Size')
    ])
    
    condition = SelectField('Condition', validators=[DataRequired()], choices=[
        ('', 'Select Condition'),
        ('excellent', 'Excellent - Like new'),
        ('good', 'Good - Minor wear'),
        ('fair', 'Fair - Noticeable wear'),
        ('poor', 'Poor - Significant wear')
    ])
    
    color = StringField('Color', validators=[
        Optional(),
        Length(max=30, message='Color cannot exceed 30 characters')
    ])
    
    brand = StringField('Brand', validators=[
        Optional(),
        Length(max=50, message='Brand cannot exceed 50 characters')
    ])
    
    quantity = IntegerField('Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=1, max=50, message='Quantity must be between 1 and 50')
    ], default=1)
    
    media_file = FileField('Upload Image or Video', validators=[
        FileRequired(message='Please upload an image or video'),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi', 'webm'], 
                   message='Only image files (jpg, jpeg, png, gif) and video files (mp4, mov, avi, webm) are allowed')
    ])
    
    submit = SubmitField('Add Item')

class EditItemForm(FlaskForm):
    title = StringField('Item Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=100, message='Title must be between 3 and 100 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500, message='Description cannot exceed 500 characters')
    ])
    
    category = SelectField('Category', validators=[DataRequired()], choices=[
        ('', 'Select Category'),
        ('tops', 'Tops'),
        ('bottoms', 'Bottoms'),
        ('dresses', 'Dresses'),
        ('outerwear', 'Outerwear'),
        ('shoes', 'Shoes'),
        ('accessories', 'Accessories'),
        ('activewear', 'Activewear'),
        ('formal', 'Formal Wear'),
        ('casual', 'Casual Wear'),
        ('vintage', 'Vintage'),
        ('other', 'Other')
    ])
    
    size = SelectField('Size', validators=[DataRequired()], choices=[
        ('', 'Select Size'),
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
        ('xxl', 'XXL'),
        ('xxxl', 'XXXL'),
        ('28', '28'),
        ('30', '30'),
        ('32', '32'),
        ('34', '34'),
        ('36', '36'),
        ('38', '38'),
        ('40', '40'),
        ('42', '42'),
        ('44', '44'),
        ('46', '46'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('one-size', 'One Size')
    ])
    
    condition = SelectField('Condition', validators=[DataRequired()], choices=[
        ('', 'Select Condition'),
        ('excellent', 'Excellent - Like new'),
        ('good', 'Good - Minor wear'),
        ('fair', 'Fair - Noticeable wear'),
        ('poor', 'Poor - Significant wear')
    ])
    
    color = StringField('Color', validators=[
        Optional(),
        Length(max=30, message='Color cannot exceed 30 characters')
    ])
    
    brand = StringField('Brand', validators=[
        Optional(),
        Length(max=50, message='Brand cannot exceed 50 characters')
    ])
    
    quantity = IntegerField('Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=1, max=50, message='Quantity must be between 1 and 50')
    ])
    
    media_file = FileField('Upload New Image or Video (optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi', 'webm'], 
                   message='Only image files (jpg, jpeg, png, gif) and video files (mp4, mov, avi, webm) are allowed')
    ])
    
    submit = SubmitField('Update Item')
